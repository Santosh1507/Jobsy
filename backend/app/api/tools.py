from fastapi import APIRouter, Depends, HTTPException
from typing import Optional, List
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.services.pdf_generator import pdf_generator
from app.services.job_evaluator import job_evaluator
from app.services.insider_intel_service import insider_intel_service
from app.services.interview_prep_service import interview_prep_service
from app.services.outreach_service import outreach_service
from app.services.voice_interview_service import voice_mock_interview

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


class BatchEvaluateRequest(BaseModel):
    jobs: List[dict]
    user_data: dict
    cv_text: Optional[str] = ""


class SalaryRequest(BaseModel):
    company: str
    role: str
    level: Optional[str] = None
    city: Optional[str] = None


class InterviewPrepRequest(BaseModel):
    company: str
    role: str
    question_type: str = "mixed"


class OutreachRequest(BaseModel):
    company: str
    role: str
    user_data: dict
    linkedin_url: Optional[str] = None


class VoiceInterviewRequest(BaseModel):
    user_id: str
    company: str
    role: str
    interview_type: str = "mixed"


class SubmitAnswerRequest(BaseModel):
    session_id: str
    answer: str
    time_taken_seconds: int


class StoryBankRequest(BaseModel):
    user_id: str
    story: dict


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


@router.post("/generate-tailored-resume")
async def generate_tailored_resume(request: GeneratePDFRequest):
    """Generate job-specific tailored resume"""
    
    try:
        job_description = request.job_data.get("description", "") if request.job_data else ""
        keywords = request.keywords or []
        
        pdf_bytes = await pdf_generator.generate_tailored_resume(
            user_data=request.user_data,
            job_description=job_description,
            keywords=keywords
        )
        
        filepath = await pdf_generator.save_resume_pdf(
            user_id=request.user_id,
            user_data=request.user_data,
            job_data=request.job_data,
            keywords=keywords
        )
        
        return {
            "success": True,
            "file_path": filepath,
            "tailored": True
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


@router.post("/batch-evaluate")
async def batch_evaluate_jobs(request: BatchEvaluateRequest):
    """Evaluate multiple jobs in batch"""
    
    results = []
    
    for job in request.jobs:
        try:
            evaluation = await job_evaluator.evaluate_job(
                job_data=job,
                user_data=request.user_data,
                cv_text=request.cv_text or ""
            )
            results.append({
                "job": job.get("title", "Unknown"),
                "company": job.get("company", ""),
                "evaluation": evaluation
            })
        except Exception as e:
            results.append({
                "job": job.get("title", "Unknown"),
                "company": job.get("company", ""),
                "error": str(e)
            })
    
    return {
        "total": len(request.jobs),
        "results": results
    }


@router.get("/portal-config")
async def get_portal_config():
    """Get portal scanner configuration"""
    from app.utils.portals import get_portal_config, get_enabled_companies
    
    return {
        "config": get_portal_config(),
        "enabled_companies": get_enabled_companies(),
        "supported_ats": ["greenhouse", "lever", "ashby", "workday"]
    }


@router.post("/salary-intelligence")
async def get_salary_intelligence(
    request: SalaryRequest,
    db: AsyncSession = Depends(get_db)
):
    """Get salary data for company/role"""
    
    try:
        salary_data = await insider_intel_service.get_salary_data(
            company=request.company,
            role=request.role,
            db=db,
            level=request.level,
            city=request.city
        )
        
        if salary_data:
            return salary_data
        
        market_data = await insider_intel_service.get_market_benchmark(
            role=request.role,
            db=db
        )
        
        return {
            "company": request.company,
            "role": request.role,
            "data_source": "market",
            "salary_min": market_data.get("min", 100000),
            "salary_max": market_data.get("max", 500000),
            "median": market_data.get("median", 250000),
            "note": "Based on market average - company specific data not available"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/interview-prep")
async def get_interview_prep(request: InterviewPrepRequest):
    """Get interview preparation questions and tips"""
    
    try:
        questions = await interview_prep_service.generate_questions(
            company=request.company,
            role=request.role,
            question_type=request.question_type
        )
        
        company_patterns = interview_prep_service.COMPANY_INTERVIEW_PATTERNS.get(
            request.company.lower(),
            {}
        )
        
        return {
            "company": request.company,
            "role": request.role,
            "questions": questions,
            "rounds": company_patterns.get("rounds", 3),
            "round_types": company_patterns.get("types", []),
            "tips": company_patterns.get("tips", [])
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/recruiter-outreach")
async def generate_outreach(
    request: OutreachRequest,
    db: AsyncSession = Depends(get_db)
):
    """Generate recruiter outreach message"""
    
    try:
        result = await outreach_service.generate_outreach_message(
            company=request.company,
            role=request.role,
            user_data=request.user_data,
            linkedin_url=request.linkedin_url
        )
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/story-bank")
async def add_story(
    request: StoryBankRequest,
    db: AsyncSession = Depends(get_db)
):
    """Add STAR+ story to story bank"""
    
    from app.services.story_bank import story_bank_service
    
    try:
        story_id = story_bank_service.add_story(
            user_id=request.user_id,
            story=request.story
        )
        
        return {
            "success": True,
            "story_id": story_id
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/story-bank/{user_id}")
async def get_stories(
    user_id: str,
    archetype: Optional[str] = None,
    limit: int = 5
):
    """Get user's STAR stories"""
    
    from app.services.story_bank import story_bank_service
    
    if archetype:
        stories = story_bank_service.get_stories_for_archetype(user_id, archetype, limit)
    else:
        stories = story_bank_service.get_all_stories(user_id, limit)
    
    return {
        "user_id": user_id,
        "stories": stories
    }


@router.post("/negotiation-script")
async def get_negotiation_script(
    company: str = "Unknown",
    offer_details: dict = {}
):
    """Get salary negotiation scripts"""
    
    from app.utils.negotiation import get_negotiation_script
    
    script = get_negotiation_script(company, offer_details)
    
    return {
        "company": company,
        "scripts": script
    }


@router.post("/voice-interview/start")
async def start_voice_interview(request: VoiceInterviewRequest):
    """Start a voice mock interview session"""
    
    result = voice_mock_interview.start_interview(
        user_id=request.user_id,
        company=request.company,
        role=request.role,
        interview_type=request.interview_type
    )
    
    return result


@router.get("/voice-interview/{session_id}/question")
async def get_voice_interview_question(session_id: str):
    """Get the next question in the voice interview"""
    
    question = voice_mock_interview.get_next_question(session_id)
    
    if not question:
        raise HTTPException(status_code=404, detail="No more questions or session not found")
    
    return question


@router.post("/voice-interview/answer")
async def submit_voice_interview_answer(request: SubmitAnswerRequest):
    """Submit an answer to the current question"""
    
    result = voice_mock_interview.submit_answer(
        session_id=request.session_id,
        answer=request.answer,
        time_taken_seconds=request.time_taken_seconds
    )
    
    return result


@router.post("/voice-interview/{session_id}/complete")
async def complete_voice_interview(session_id: str):
    """Complete the interview and get feedback"""
    
    result = voice_mock_interview.complete_interview(session_id)
    
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    
    return result


@router.get("/voice-interview/{session_id}/status")
async def get_voice_interview_status(session_id: str):
    """Get the current status of a voice interview session"""
    
    status = voice_mock_interview.get_session_status(session_id)
    
    if not status:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return status