from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, func
from pydantic import BaseModel
from datetime import datetime, timedelta

from app.core.database import get_db
from app.models.database import Application, Job, User
from app.models.schemas import ApplicationResponse, ApplicationCreate, ApplicationUpdate

router = APIRouter(prefix="/applications", tags=["Applications"])


@router.get("/", response_model=List[ApplicationResponse])
async def get_applications(
    user_id: Optional[str] = None,
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 20,
    db: AsyncSession = Depends(get_db)
):
    """Get applications with optional filters"""
    
    query = select(Application)
    
    if user_id:
        query = query.where(Application.user_id == user_id)
    if status:
        query = query.where(Application.status == status)
    
    query = query.order_by(desc(Application.applied_at)).offset(skip).limit(limit)
    
    result = await db.execute(query)
    applications = result.scalars().all()
    
    return applications


@router.get("/{application_id}", response_model=ApplicationResponse)
async def get_application(
    application_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get single application by ID"""
    
    result = await db.execute(
        select(Application).where(Application.id == application_id)
    )
    app = result.scalar_one_or_none()
    
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")
    
    return app


@router.post("/", response_model=ApplicationResponse)
async def create_application(
    application: ApplicationCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new application"""
    
    db_app = Application(**application.dict())
    db.add(db_app)
    await db.commit()
    await db.refresh(db_app)
    
    return db_app


@router.patch("/{application_id}")
async def update_application(
    application_id: str,
    update: ApplicationUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update application status"""
    
    result = await db.execute(
        select(Application).where(Application.id == application_id)
    )
    app = result.scalar_one_or_none()
    
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")
    
    if update.status:
        app.status = update.status
        app.status_updated_at = datetime.utcnow()
    
    if update.notes is not None:
        app.notes = update.notes
    
    if update.ats_submission_id:
        app.ats_submission_id = update.ats_submission_id
    
    await db.commit()
    await db.refresh(app)
    
    return {"id": str(app.id), "status": app.status.value}


@router.get("/stats/summary")
async def get_application_stats(
    user_id: str,
    days: int = 30,
    db: AsyncSession = Depends(get_db)
):
    """Get application statistics for a user"""
    
    start_date = datetime.utcnow() - timedelta(days=days)
    
    # Total applications
    total_result = await db.execute(
        select(func.count(Application.id))
        .where(Application.user_id == user_id)
        .where(Application.applied_at >= start_date)
    )
    total = total_result.scalar()
    
    # Status breakdown
    status_result = await db.execute(
        select(Application.status, func.count(Application.id))
        .where(Application.user_id == user_id)
        .where(Application.applied_at >= start_date)
        .group_by(Application.status)
    )
    status_breakdown = {row[0]: row[1] for row in status_result.all()}
    
    # This week's applications
    week_start = datetime.utcnow() - timedelta(days=7)
    week_result = await db.execute(
        select(func.count(Application.id))
        .where(Application.user_id == user_id)
        .where(Application.applied_at >= week_start)
    )
    this_week = week_result.scalar()
    
    return {
        "total_applications": total,
        "this_week": this_week,
        "status_breakdown": status_breakdown,
        "days": days
    }


@router.get("/stats/daily")
async def get_daily_stats(
    user_id: str,
    days: int = 30,
    db: AsyncSession = Depends(get_db)
):
    """Get daily application counts"""
    
    start_date = datetime.utcnow() - timedelta(days=days)
    
    result = await db.execute(
        select(
            func.date(Application.applied_at).label("date"),
            func.count(Application.id).label("count")
        )
        .where(Application.user_id == user_id)
        .where(Application.applied_at >= start_date)
        .group_by(func.date(Application.applied_at))
        .order_by(func.date(Application.applied_at))
    )
    
    daily_stats = [{"date": str(row[0]), "count": row[1]} for row in result.all()]
    
    return {"daily_stats": daily_stats}


@router.post("/{application_id}/status/{new_status}")
async def update_status(
    application_id: str,
    new_status: str,
    db: AsyncSession = Depends(get_db)
):
    """Update application status via URL"""
    
    from app.models.database import ApplicationStatus
    
    try:
        status = ApplicationStatus(new_status)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid status")
    
    result = await db.execute(
        select(Application).where(Application.id == application_id)
    )
    app = result.scalar_one_or_none()
    
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")
    
    app.status = status
    app.status_updated_at = datetime.utcnow()
    
    await db.commit()
    
    return {"id": str(app.id), "status": status.value, "updated_at": app.status_updated_at}