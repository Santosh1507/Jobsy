import asyncio
import logging
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from loguru import logger

from app.core.database import AsyncSessionLocal
from app.services.scraper_service import job_scraper
from app.services.whatsapp_service import whatsapp_service
from app.models.database import User


logger.add("logs/workers.log", rotation="500 MB", retention="10 days")


class JobScraperWorker:
    """Background worker for scraping jobs"""

    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.keywords = [
            "backend engineer",
            "software engineer",
            "full stack developer",
            "python developer",
            "data engineer",
            "devops engineer"
        ]

    async def scrape_daily(self):
        """Daily job scraping task"""
        logger.info("Starting daily job scrape...")

        async with AsyncSessionLocal() as db:
            try:
                jobs = await job_scraper.scrape_all_sources(self.keywords)
                saved = await job_scraper.save_jobs_to_db(jobs, db)
                logger.info(f"Scraped {len(jobs)} jobs, saved {saved} new")
            except Exception as e:
                logger.error(f"Job scrape error: {e}")

    async def send_job_drops(self):
        """Send daily job drops to users"""
        logger.info("Sending daily job drops...")

        async with AsyncSessionLocal() as db:
            from sqlalchemy import select

            result = await db.execute(
                select(User).where(User.onboarding_completed == True)
            )
            users = result.scalars().all()

            for user in users:
                try:
                    # Get matched jobs for user
                    matched_jobs = await self.get_matched_jobs(user, db)

                    if matched_jobs:
                        await whatsapp_service.send_daily_job_drop(
                            user.phone,
                            matched_jobs
                        )
                        logger.info(f"Sent job drop to {user.phone}")
                except Exception as e:
                    logger.error(f"Job drop error for {user.phone}: {e}")

    async def get_matched_jobs(self, user, db):
        """Get matched jobs for user"""
        from sqlalchemy import select, desc
        from app.models.database import Job
        from app.services.scraper_service import job_scraper

        # Get recent active jobs
        result = await db.execute(
            select(Job)
            .where(Job.is_active == True)
            .order_by(desc(Job.scraped_at))
            .limit(5)
        )

        jobs = result.scalars().all()

        job_list = []
        for job in jobs:
            # Simple matching based on skills/location
            if user.preferred_cities and job.location not in user.preferred_cities:
                if not (job.remote and "remote" in [c.lower() for c in user.preferred_cities]):
                    continue

            job_list.append({
                "id": str(job.id),
                "title": job.title,
                "company": job.company,
                "location": job.location or "N/A",
                "salary": f"{job.salary_min} - {job.salary_max}" if job.salary_min else None,
                "match_score": 75,
                "apply_url": job.apply_url
            })

        return job_list[:3]

    def start(self):
        """Start the scheduler"""
        # Daily at 5:30 AM for scraping
        self.scheduler.add_job(
            self.scrape_daily,
            CronTrigger(hour=5, minute=30),
            id="daily_scrape"
        )

        # Daily at 8 AM for job drops
        self.scheduler.add_job(
            self.send_job_drops,
            CronTrigger(hour=8, minute=0),
            id="daily_job_drop"
        )

        self.scheduler.start()
        logger.info("Job scraper worker started")


class NotificationWorker:
    """Background worker for notifications"""

    def __init__(self):
        self.scheduler = AsyncIOScheduler()

    async def send_weekly_digest(self):
        """Send weekly digest to all active users"""
        logger.info("Sending weekly digests...")

        async with AsyncSessionLocal() as db:
            from sqlalchemy import select
            from app.services.tracker_service import tracker_service

            result = await db.execute(
                select(User).where(User.onboarding_completed == True)
            )
            users = result.scalars().all()

            for user in users:
                try:
                    await tracker_service.send_daily_digest(str(user.id), db)
                except Exception as e:
                    logger.error(f"Digest error for {user.phone}: {e}")

    def start(self):
        """Start the scheduler"""
        # Weekly on Sunday at 10 AM
        self.scheduler.add_job(
            self.send_weekly_digest,
            CronTrigger(day_of_week="sun", hour=10, minute=0),
            id="weekly_digest"
        )

        self.scheduler.start()
        logger.info("Notification worker started")


# Worker instances
scraper_worker = JobScraperWorker()
notification_worker = NotificationWorker()


async def start_all_workers():
    """Start all background workers"""
    scraper_worker.start()
    notification_worker.start()
    logger.info("All workers started")


async def stop_all_workers():
    """Stop all background workers"""
    scraper_worker.scheduler.shutdown()
    notification_worker.scheduler.shutdown()
    logger.info("All workers stopped")