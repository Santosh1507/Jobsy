from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from pydantic import BaseModel
from datetime import datetime

from app.core.database import get_db
from app.models.database import Job
from app.models.schemas import JobResponse, JobCreate

router = APIRouter(prefix="/jobs", tags=["Jobs"])


class JobMatchRequest(BaseModel):
    user_id: str
    limit: int = 5


class JobMatchResponse(BaseModel):
    jobs: List[dict]
    total: int


SAMPLE_JOBS = [
    {"id": "1", "title": "Backend Engineer", "company": "Anthropic", "location": "San Francisco", "salary_min": 150000, "salary_max": 250000, "apply_url": "https://anthropic.com/careers", "source": "greenhouse"},
    {"id": "2", "title": "ML Engineer", "company": "OpenAI", "location": "Remote", "salary_min": 200000, "salary_max": 350000, "apply_url": "https://openai.com/careers", "source": "lever"},
    {"id": "3", "title": "Full Stack Developer", "company": "Vercel", "location": "Remote", "salary_min": 120000, "salary_max": 200000, "apply_url": "https://vercel.com/careers", "source": "greenhouse"},
    {"id": "4", "title": "Solutions Engineer", "company": "LangChain", "location": "Remote", "salary_min": 100000, "salary_max": 180000, "apply_url": "https://langchain.com/careers", "source": "ashby"},
    {"id": "5", "title": "Platform Engineer", "company": "Temporal", "location": "Remote", "salary_min": 140000, "salary_max": 220000, "apply_url": "https://temporal.io/careers", "source": "greenhouse"},
]

@router.get("/", response_model=List[JobResponse])
async def get_jobs(
    skip: int = 0,
    limit: int = 20,
    source: Optional[str] = None,
    company: Optional[str] = None
):
    """Get jobs with optional filters - returns sample jobs"""
    return SAMPLE_JOBS[skip:skip+limit]
    
    return jobs


@router.get("/{job_id}", response_model=JobResponse)
async def get_job(job_id: str, db: AsyncSession = Depends(get_db)):
    """Get single job by ID"""
    
    result = await db.execute(select(Job).where(Job.id == job_id))
    job = result.scalar_one_or_none()
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return job


@router.post("/match", response_model=JobMatchResponse)
async def match_jobs(
    request: JobMatchRequest,
    db: AsyncSession = Depends(get_db)
):
    """Match jobs to user profile using vector similarity"""
    
    # This would use vector similarity matching
    # For now, return recent jobs as placeholder
    result = await db.execute(
        select(Job)
        .where(Job.is_active == True)
        .order_by(desc(Job.scraped_at))
        .limit(request.limit)
    )
    
    jobs = result.scalars().all()
    
    job_list = []
    for job in jobs:
        job_list.append({
            "id": str(job.id),
            "title": job.title,
            "company": job.company,
            "location": job.location,
            "salary": f"{job.salary_min} - {job.salary_max}" if job.salary_min else None,
            "match_score": 75,  # Would be calculated from vector similarity
            "apply_url": job.apply_url
        })
    
    return {"jobs": job_list, "total": len(job_list)}


@router.post("/")
async def create_job(job: JobCreate, db: AsyncSession = Depends(get_db)):
    """Create a new job (for internal use)"""
    
    from app.models.database import Job as JobModel
    
    db_job = JobModel(**job.dict())
    db.add(db_job)
    await db.commit()
    await db.refresh(db_job)
    
    return {"id": str(db_job.id), "status": "created"}


@router.get("/sources/list")
async def list_sources():
    """List available job sources"""
    return {
        "sources": [
            {"id": "linkedin", "name": "LinkedIn"},
            {"id": "naukri", "name": "Naukri"},
            {"id": "instahyre", "name": "Instahyre"},
            {"id": "wellfound", "name": "Wellfound"},
            {"id": "cutshort", "name": "Cutshort"},
            {"id": "iimjobs", "name": "IIM Jobs"},
            {"id": "angelist", "name": "AngelList"}
        ]
    }