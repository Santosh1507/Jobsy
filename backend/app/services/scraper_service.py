import asyncio
import hashlib
import re
import json
from typing import List, Dict, Optional, Any
from datetime import datetime
from bs4 import BeautifulSoup
import httpx
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.database import Job, JobType


class JobScraperService:
    """Service for scraping jobs from various job boards"""
    
    def __init__(self):
        self.session = httpx.AsyncClient(
            timeout=30.0,
            follow_redirects=True,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            }
        )
        self.scrapers = {
            "linkedin": self.scrape_linkedin,
            "naukri": self.scrape_naukri,
            "wellfound": self.scrape_wellfound,
            "instahyre": self.scrape_instahyre,
            "cutshort": self.scrape_cutshort,
        }

    async def scrape_all_sources(self, keywords: List[str] = None) -> List[Dict]:
        """Scrape jobs from all configured sources"""
        all_jobs = []
        
        # Scrape from each source concurrently
        tasks = []
        for source, scraper_func in self.scrapers.items():
            tasks.append(self.safe_scrape(source, scraper_func, keywords or []))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for source, result in zip(self.scrapers.keys(), results):
            if isinstance(result, Exception):
                logger.error(f"Error scraping {source}: {result}")
            else:
                all_jobs.extend(result)
                logger.info(f"Scraped {len(result)} jobs from {source}")
        
        # Deduplicate
        unique_jobs = self.deduplicate_jobs(all_jobs)
        
        return unique_jobs

    async def safe_scrape(self, source: str, scraper_func, keywords: List[str]):
        """Safely execute scraper with error handling"""
        try:
            return await scraper_func(keywords)
        except Exception as e:
            logger.error(f"Scraper error for {source}: {e}")
            return []

    async def scrape_wellfound(self, keywords: List[str]) -> List[Dict]:
        """Scrape jobs from Wellfound (AngelList)"""
        jobs = []
        
        try:
            # Wellfound API endpoint
            url = "https://wellfound.com/api/v1/jobs"
            
            for keyword in keywords or ["backend", "software engineer"]:
                params = {
                    "query": keyword,
                    "location": "india",
                    "per_page": 20
                }
                
                response = await self.session.get(url, params=params)
                
                if response.status_code == 200:
                    data = response.json()
                    for job in data.get("jobs", []):
                        jobs.append({
                            "source": "wellfound",
                            "source_job_id": str(job.get("id", "")),
                            "title": job.get("title", ""),
                            "company": job.get("company", {}).get("name", ""),
                            "location": job.get("location", ""),
                            "description": job.get("description", ""),
                            "requirements": job.get("requirements", []),
                            "salary_min": self.parse_salary(job.get("salary_min")),
                            "salary_max": self.parse_salary(job.get("salary_max")),
                            "apply_url": job.get("application_url", ""),
                            "remote": job.get("remote", True),
                            "posted_at": job.get("published_at")
                        })
                        
        except Exception as e:
            logger.error(f"Wellfound scraping error: {e}")
        
        return jobs

    async def scrape_naukri(self, keywords: List[str]) -> List[Dict]:
        """Scrape jobs from Naukri"""
        jobs = []
        
        try:
            for keyword in keywords or ["backend engineer", "software engineer"]:
                # Naukri uses POST for search
                url = "https://www.naukri.com/jobapi/v2/search"
                
                payload = {
                    "title": keyword,
                    "location": "India",
                    "noOfResults": 20
                }
                
                headers = {
                    "User-Agent": "Mozilla/5.0",
                    "Accept": "application/json",
                    "Referer": "https://www.naukri.com/"
                }
                
                response = await self.session.post(
                    url,
                    json=payload,
                    headers=headers
                )
                
                if response.status_code == 200:
                    data = response.json()
                    for job in data.get("jobDetails", []):
                        jobs.append({
                            "source": "naukri",
                            "source_job_id": str(job.get("jobId", "")),
                            "title": job.get("title", ""),
                            "company": job.get("companyName", ""),
                            "location": job.get("location", ""),
                            "description": job.get("jobDescription", ""),
                            "salary_min": self.parse_salary(job.get("minSalary")),
                            "salary_max": self.parse_salary(job.get("maxSalary")),
                            "apply_url": job.get("applyLink", ""),
                            "job_type": job.get("type", ""),
                            "posted_at": job.get("postedDate", "")
                        })
                        
        except Exception as e:
            logger.error(f"Naukri scraping error: {e}")
        
        return jobs

    async def scrape_linkedin(self, keywords: List[str]) -> List[Dict]:
        """Scrape jobs from LinkedIn"""
        jobs = []
        
        # Note: LinkedIn has strict anti-scraping
        # This would typically use their official API or paid service
        # Placeholder for demo purposes
        
        try:
            # LinkedIn Easy Apply jobs (requires auth)
            # Would need LinkedIn session cookie
            
            if not settings.LINKEDIN_COOKIE:
                logger.warning("LinkedIn cookie not configured, skipping")
                return jobs
            
            # Implementation would use Playwright with auth
            pass
            
        except Exception as e:
            logger.error(f"LinkedIn scraping error: {e}")
        
        return jobs

    async def scrape_instahyre(self, keywords: List[str]) -> List[Dict]:
        """Scrape jobs from Instahyre"""
        jobs = []
        
        try:
            url = "https://www.instahyre.com/api/v1/jobs/"
            
            for keyword in keywords or ["backend", "software engineer"]:
                params = {
                    "search": keyword,
                    "page": 1
                }
                
                response = await self.session.get(url, params=params)
                
                if response.status_code == 200:
                    data = response.json()
                    for job in data.get("jobs", []):
                        jobs.append({
                            "source": "instahyre",
                            "source_job_id": str(job.get("id", "")),
                            "title": job.get("title", ""),
                            "company": job.get("company", {}).get("name", ""),
                            "location": job.get("location", ""),
                            "description": job.get("description", ""),
                            "salary_min": self.parse_salary(job.get("salary_min")),
                            "salary_max": self.parse_salary(job.get("salary_max")),
                            "apply_url": f"https://www.instahyre.com/job/{job.get('slug', '')}",
                            "remote": job.get("remote", False)
                        })
                        
        except Exception as e:
            logger.error(f"Instahyre scraping error: {e}")
        
        return jobs

    async def scrape_cutshort(self, keywords: List[str]) -> List[Dict]:
        """Scrape jobs from Cutshort"""
        jobs = []
        
        try:
            # Cutshort API
            url = "https://cutshort.io/api/public/jobs"
            
            params = {
                "keywords": ",".join(keywords or ["backend"]),
                "location": "India"
            }
            
            response = await self.session.get(url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                for job in data.get("data", []):
                    jobs.append({
                        "source": "cutshort",
                        "source_job_id": str(job.get("id", "")),
                        "title": job.get("title", ""),
                        "company": job.get("company_name", ""),
                        "location": job.get("location", ""),
                        "description": job.get("description", ""),
                        "salary_min": self.parse_salary(job.get("min_salary")),
                        "salary_max": self.parse_salary(job.get("max_salary")),
                        "apply_url": job.get("url", ""),
                        "remote": job.get("remote", False)
                    })
                    
        except Exception as e:
            logger.error(f"Cutshort scraping error: {e}")
        
        return jobs

    def parse_salary(self, salary: Optional[str]) -> Optional[str]:
        """Parse salary string to standard format"""
        if not salary:
            return None
        
        # Remove currency symbols and convert to LPA for India
        salary = str(salary).replace("₹", "").replace(",", "").strip()
        
        # If salary is in annual format, convert to LPA
        try:
            value = float(salary)
            if value > 100000:  # Likely annual in rupees
                lpa = value / 100000
                return f"{lpa:.1f} LPA"
        except ValueError:
            pass
        
        return salary

    def deduplicate_jobs(self, jobs: List[Dict]) -> List[Dict]:
        """Remove duplicate jobs based on company + title + location"""
        seen_hashes = set()
        unique_jobs = []
        
        for job in jobs:
            # Create hash for deduplication
            hash_input = f"{job.get('company', '')}|{job.get('title', '')}|{job.get('location', '')}"
            job_hash = hashlib.sha256(hash_input.lower().encode()).hexdigest()
            
            if job_hash not in seen_hashes:
                seen_hashes.add(job_hash)
                job["hash"] = job_hash
                unique_jobs.append(job)
        
        logger.info(f"Deduplicated: {len(jobs)} -> {len(unique_jobs)} jobs")
        
        return unique_jobs

    async def save_jobs_to_db(self, jobs: List[Dict], db: AsyncSession):
        """Save scraped jobs to database"""
        
        saved_count = 0
        
        for job_data in jobs:
            # Check if job already exists
            from sqlalchemy import select
            
            result = await db.execute(
                select(Job).where(Job.hash == job_data.get("hash"))
            )
            existing = result.scalar_one_or_none()
            
            if existing:
                # Update if older than 7 days
                continue
            
            # Create new job
            job = Job(
                source=job_data.get("source", "unknown"),
                source_job_id=job_data.get("source_job_id", ""),
                title=job_data.get("title", ""),
                company=job_data.get("company", ""),
                location=job_data.get("location", ""),
                description=job_data.get("description", ""),
                requirements=job_data.get("requirements"),
                salary_min=job_data.get("salary_min"),
                salary_max=job_data.get("salary_max"),
                apply_url=job_data.get("apply_url", ""),
                remote=job_data.get("remote", False),
                hash=job_data.get("hash", ""),
                posted_at=job_data.get("posted_at")
            )
            
            db.add(job)
            saved_count += 1
        
        await db.commit()
        logger.info(f"Saved {saved_count} new jobs to database")
        
        return saved_count

    async def close(self):
        """Close the HTTP session"""
        await self.session.aclose()


# Singleton instance
job_scraper = JobScraperService()