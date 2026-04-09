from fastapi import APIRouter, Depends, HTTPException
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from datetime import datetime

from app.core.database import get_db
from app.models.database import User, SubscriptionTier

router = APIRouter(prefix="/subscription", tags=["Subscriptions"])


class SubscribeRequest(BaseModel):
    user_id: str
    tier: str  # pro, unlimited


class SubscriptionResponse(BaseModel):
    user_id: str
    tier: str
    started_at: datetime
    expires_at: Optional[datetime]
    features: dict


SUBSCRIPTION_FEATURES = {
    "free": {
        "applications_per_month": 10,
        "ats_optimizer": False,
        "recruiter_outreach": False,
        "interview_prep": True,
        "salary_intel": False,
        "offer_analysis": False
    },
    "pro": {
        "applications_per_month": 100,
        "ats_optimizer": True,
        "recruiter_outreach": 3,
        "interview_prep": True,
        "salary_intel": True,
        "offer_analysis": True
    },
    "unlimited": {
        "applications_per_month": -1,  # unlimited
        "ats_optimizer": True,
        "recruiter_outreach": -1,
        "interview_prep": True,
        "salary_intel": True,
        "offer_analysis": True,
        "priority_support": True
    }
}

PRICING = {
    "free": {"monthly": 0, "yearly": 0},
    "pro": {"monthly": 499, "yearly": 3999},
    "unlimited": {"monthly": 999, "yearly": 9999}
}


@router.get("/plans")
async def get_plans():
    """Get available subscription plans"""
    return {
        "plans": [
            {
                "tier": "free",
                "name": "Free",
                "price": 0,
                "features": SUBSCRIPTION_FEATURES["free"]
            },
            {
                "tier": "pro",
                "name": "Pro",
                "price": 499,
                "price_yearly": 3999,
                "features": SUBSCRIPTION_FEATURES["pro"],
                "popular": True
            },
            {
                "tier": "unlimited",
                "name": "Unlimited",
                "price": 999,
                "price_yearly": 9999,
                "features": SUBSCRIPTION_FEATURES["unlimited"]
            }
        ]
    }


@router.get("/user/{user_id}")
async def get_user_subscription(
    user_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get user's current subscription"""
    
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {
        "user_id": str(user.id),
        "tier": user.subscription_tier.value,
        "features": SUBSCRIPTION_FEATURES.get(user.subscription_tier.value, {}),
        "pricing": PRICING.get(user.subscription_tier.value, {})
    }


@router.post("/subscribe")
async def subscribe(
    request: SubscribeRequest,
    db: AsyncSession = Depends(get_db)
):
    """Subscribe user to a plan (simulated - would use Razorpay in production)"""
    
    result = await db.execute(select(User).where(User.id == request.user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if request.tier not in SUBSCRIPTION_FEATURES:
        raise HTTPException(status_code=400, detail="Invalid tier")
    
    # Update subscription
    user.subscription_tier = SubscriptionTier(request.tier)
    user.updated_at = datetime.utcnow()
    
    await db.commit()
    
    return {
        "success": True,
        "user_id": str(user.id),
        "tier": request.tier,
        "features": SUBSCRIPTION_FEATURES[request.tier],
        "message": f"Subscribed to {request.tier} plan"
    }


@router.post("/cancel")
async def cancel_subscription(
    user_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Cancel user's subscription"""
    
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user.subscription_tier = SubscriptionTier.FREE
    user.updated_at = datetime.utcnow()
    
    await db.commit()
    
    return {"success": True, "message": "Subscription cancelled"}


@router.get("/check-usage/{user_id}")
async def check_usage(
    user_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Check user's usage against subscription limits"""
    
    from app.models.database import Application
    from datetime import datetime, timedelta
    
    # Get current month's applications
    start_of_month = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0)
    
    result = await db.execute(
        select(Application)
        .where(Application.user_id == user_id)
        .where(Application.applied_at >= start_of_month)
    )
    apps = result.scalars().all()
    
    # Get user's tier
    user_result = await db.execute(select(User).where(User.id == user_id))
    user = user_result.scalar_one_or_none()
    
    tier = user.subscription_tier.value if user else "free"
    features = SUBSCRIPTION_FEATURES.get(tier, SUBSCRIPTION_FEATURES["free"])
    limit = features.get("applications_per_month", 10)
    
    return {
        "user_id": user_id,
        "tier": tier,
        "applications_this_month": len(apps),
        "limit": limit,
        "remaining": max(0, limit - len(apps)) if limit > 0 else -1,
        "reset_date": start_of_month.replace(month=start_of_month.month % 12 + 1)
    }