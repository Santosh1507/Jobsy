import asyncio
import random
from typing import Dict, List, Optional, Any
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from loguru import logger

from app.models.database import Application, User, Job, ApplicationStatus
from app.services.whatsapp_service import whatsapp_service
from app.services.ollama_service import ollama_service
from app.services.insider_intel_service import insider_intel_service


class TrackerService:
    """Application tracking and notification service"""

    async def update_status(
        self,
        application_id: str,
        new_status: str,
        db: AsyncSession
    ) -> Dict[str, Any]:
        """Update application status and notify user"""

        result = await db.execute(
            select(Application).where(Application.id == application_id)
        )
        app = result.scalar_one_or_none()

        if not app:
            return {"error": "Application not found"}

        old_status = app.status.value
        app.status = ApplicationStatus(new_status)
        app.status_updated_at = datetime.utcnow()

        await db.commit()

        # Get user for notification
        user_result = await db.execute(
            select(User).where(User.id == app.user_id)
        )
        user = user_result.scalar_one_or_none()

        if user:
            # Send WhatsApp notification
            await self.notify_status_change(
                user.phone,
                app.job.company,
                old_status,
                new_status
            )

        return {
            "id": str(app.id),
            "old_status": old_status,
            "new_status": new_status,
            "notified": bool(user)
        }

    async def notify_status_change(
        self,
        phone: str,
        company: str,
        old_status: str,
        new_status: str
    ):
        """Send status change notification via WhatsApp"""

        status_icons = {
            "viewed": "👀",
            "shortlisted": "✅",
            "interview": "🎉",
            "offer": "💰",
            "rejected": "😔"
        }

        icon = status_icons.get(new_status, "📋")

        messages = {
            "viewed": f"{icon} *{company}* viewed your resume! Keep an eye out for next steps.",
            "shortlisted": f"{icon} Great news! *{company}* shortlisted you. They may reach out soon.",
            "interview": f"{icon} Amazing! *{company}* wants to interview you. Want help preparing?",
            "offer": f"{icon} Congratulations! *{company}* made an offer. Want me to analyze it?",
            "rejected": f"{icon} *{company}* went with other candidates. Don't lose hope - keep applying!"
        }

        message = messages.get(new_status, f"Update from *{company}*")
        await whatsapp_service.send_message(phone, message)

    async def send_daily_digest(self, user_id: str, db: AsyncSession) -> Dict[str, Any]:
        """Send weekly digest of application status"""

        user_result = await db.execute(
            select(User).where(User.id == user_id)
        )
        user = user_result.scalar_one_or_none()

        if not user:
            return {"error": "User not found"}

        # Get application stats
        apps_result = await db.execute(
            select(Application).where(Application.user_id == user_id)
        )
        apps = apps_result.scalars().all()

        status_counts = {}
        for app in apps:
            status = app.status.value
            status_counts[status] = status_counts.get(status, 0) + 1

        # Generate digest message
        message = f"📊 *Weekly Application Digest*\n\n"
        message += f"Total applications: {len(apps)}\n\n"
        message += f"📨 Applied: {status_counts.get('applied', 0)}\n"
        message += f"👀 Viewed: {status_counts.get('viewed', 0)}\n"
        message += f"✅ Shortlisted: {status_counts.get('shortlisted', 0)}\n"
        message += f"🎯 Interview: {status_counts.get('interview', 0)}\n"
        message += f"💰 Offers: {status_counts.get('offer', 0)}\n"
        message += f"😔 Rejected: {status_counts.get('rejected', 0)}\n\n"

        if status_counts.get("interview", 0) > 0:
            message += "🎉 You're getting interviews! Want prep help?"

        await whatsapp_service.send_message(user.phone, message)

        return {"sent": True, "stats": status_counts}

    async def get_user_applications(
        self,
        user_id: str,
        status: Optional[str] = None,
        db: AsyncSession
    ) -> List[Dict[str, Any]]:
        """Get user's applications with job details"""

        query = select(Application).where(Application.user_id == user_id)

        if status:
            query = query.where(Application.status == status)

        result = await db.execute(query.order_by(Application.applied_at.desc()))
        apps = result.scalars().all()

        applications = []
        for app in apps:
            job_result = await db.execute(
                select(Job).where(Job.id == app.job_id)
            )
            job = job_result.scalar_one_or_none()

            applications.append({
                "id": str(app.id),
                "company": job.company if job else "Unknown",
                "title": job.title if job else "Unknown",
                "status": app.status.value,
                "applied_at": app.applied_at.isoformat() if app.applied_at else None,
                "status_updated": app.status_updated_at.isoformat() if app.status_updated_at else None
            })

        return applications


# Singleton instance
tracker_service = TrackerService()