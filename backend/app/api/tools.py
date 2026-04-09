from fastapi import APIRouter, Depends, HTTPException
from typing import Optional
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.services.pdf_generator import pdf_generator
from app.services.job_evaluator import job_evaluator

router = APIRouter(prefix="/tools", tags=["Tools"])


class GeneratePDFRequest(BaseModel):
    user_id: str
    user_data: dict
    job_data: Optional[dict] = None
    keywords: Optional[list] = None


class EvaluateJobRequest(BaseModel):
    job_data: dict
    user_data: dict
    cv_text: Optional[str] = ""


@router.post("/generate-pdf")
async def generate_resume_pdf(
    request: GeneratePDFRequest,
    db: AsyncSession = Depends(get_db)
):
    """Generate ATS-optimized PDF resume"""
    
    try:
        pdf_bytes = await pdf_generator.generate_resume_pdf(
            user_data=request.user_data,
            job_data=request.job_data,
            keywords=request.keywords
        )
        
        # Save to file
        filepath = await pdf_generator.save_resume_pdf(
            user_id=request.user_id,
            user_data=request.user_data,
            job_data=request.job_data,
            keywords=request.keywords
        )
        
        return {
            "success": True,
            "file_path": filepath,
            "size_bytes": len(pdf_bytes)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/evaluate-job")
async def evaluate_job(request: EvaluateJobRequest):
    """Evaluate job using A-F scoring system (career-ops style)"""
    
    try:
        evaluation = await job_evaluator.evaluate_job(
            job_data=request.job_data,
            user_data=request.user_data,
            cv_text=request.cv_text or ""
        )
        
        return evaluation
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/portal-config")
async def get_portal_config():
    """Get portal scanner configuration"""
    from app.utils.portals import get_portal_config, get_enabled_companies
    
    return {
        "config": get_portal_config(),
        "enabled_companies": get_enabled_companies()
    }


@router.get("/story-bank/{user_id}")
async def get_story_bank(user_id: str):
    """Get user's STAR story bank"""
    from app.services.story_bank import story_bank
    
    stories = story_bank.get_master_stories(user_id)
    export = story_bank.export_stories(user_id)
    
    return {
        "stories": stories,
        "markdown": export
    }


@router.post("/story-bank/{user_id}")
async def add_story(
    user_id: str,
    story: dict
):
    """Add STAR story to story bank"""
    from app.services.story_bank import story_bank
    
    story_id = story_bank.add_story(user_id, story)
    
    return {"success": True, "story_id": story_id}


@router.post("/negotiation-script")
async def generate_negotiation_script(
    offer_data: dict,
    market_data: Optional[dict] = None
):
    """Generate negotiation script for job offer"""
    from app.utils.negotiation import generate_negotiation_script
    
    script = generate_negotiation_script(offer_data, market_data)
    
    return script