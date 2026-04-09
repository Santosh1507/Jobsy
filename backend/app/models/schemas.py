from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class SubscriptionTier(str, Enum):
    FREE = "free"
    PRO = "pro"
    UNLIMITED = "unlimited"


class JobType(str, Enum):
    FULL_TIME = "full-time"
    PART_TIME = "part-time"
    CONTRACT = "contract"
    INTERNSHIP = "intern"


class ApplicationStatus(str, Enum):
    APPLIED = "applied"
    VIEWED = "viewed"
    SHORTLISTED = "shortlisted"
    INTERVIEW = "interview"
    OFFER = "offer"
    REJECTED = "rejected"
    WITHDRAWN = "withdrawn"


class UserBase(BaseModel):
    phone: str
    whatsapp_id: Optional[str] = None
    name: Optional[str] = None
    target_role: Optional[str] = None
    experience_years: Optional[int] = None
    current_ctc: Optional[str] = None
    target_ctc: Optional[str] = None
    preferred_cities: Optional[List[str]] = []
    skills: Optional[List[str]] = []
    blacklist_companies: Optional[List[str]] = []


class UserCreate(UserBase):
    pass


class UserUpdate(BaseModel):
    name: Optional[str] = None
    target_role: Optional[str] = None
    experience_years: Optional[int] = None
    current_ctc: Optional[str] = None
    target_ctc: Optional[str] = None
    preferred_cities: Optional[List[str]] = None
    skills: Optional[List[str]] = None
    blacklist_companies: Optional[List[str]] = None
    resume_url: Optional[str] = None
    resume_parsed: Optional[dict] = None


class UserResponse(UserBase):
    id: str
    resume_url: Optional[str] = None
    resume_parsed: Optional[dict] = None
    subscription_tier: SubscriptionTier = SubscriptionTier.FREE
    created_at: datetime
    updated_at: datetime
    last_active_at: Optional[datetime] = None
    onboarding_completed: bool = False
    profile_version: int = 1

    class Config:
        from_attributes = True


class JobBase(BaseModel):
    source: str
    source_job_id: str
    title: str
    company: str
    location: Optional[str] = None
    description: Optional[str] = None
    requirements: Optional[dict] = None
    salary_min: Optional[str] = None
    salary_max: Optional[str] = None
    job_type: Optional[JobType] = None
    remote: Optional[bool] = None
    apply_url: Optional[str] = None
    ats_platform: Optional[str] = None
    posted_at: Optional[datetime] = None


class JobCreate(JobBase):
    hash: str


class JobResponse(JobBase):
    id: str
    scraped_at: datetime
    is_active: bool = True

    class Config:
        from_attributes = True


class ApplicationBase(BaseModel):
    user_id: str
    job_id: str
    resume_version: str = "v1"


class ApplicationCreate(ApplicationBase):
    pass


class ApplicationUpdate(BaseModel):
    status: Optional[ApplicationStatus] = None
    notes: Optional[str] = None
    ats_submission_id: Optional[str] = None


class ApplicationResponse(ApplicationBase):
    id: str
    status: ApplicationStatus = ApplicationStatus.APPLIED
    applied_at: datetime
    status_updated_at: Optional[datetime] = None
    notes: Optional[str] = None
    follow_up_sent: bool = False

    class Config:
        from_attributes = True


class SalaryDataBase(BaseModel):
    company: str
    role: str
    level: Optional[str] = None
    city: Optional[str] = None
    company_stage: Optional[str] = None
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    median_salary: Optional[int] = None
    sample_size: Optional[int] = None
    source: str


class SalaryDataResponse(SalaryDataBase):
    id: str
    recorded_at: datetime

    class Config:
        from_attributes = True


class MessageLogBase(BaseModel):
    user_id: str
    direction: str
    message_text: str
    intent: Optional[str] = None
    metadata: Optional[dict] = None


class MessageLogCreate(MessageLogBase):
    pass


class MessageLogResponse(MessageLogBase):
    id: str
    created_at: datetime

    class Config:
        from_attributes = True


class UserPreferencesBase(BaseModel):
    daily_job_drop_time: str = "08:00"
    max_applications_per_day: int = 20
    notify_on_status_change: bool = True
    notify_on_interview: bool = True
    weekly_digest: bool = True
    preferred_contact_method: str = "whatsapp"


class UserPreferencesResponse(UserPreferencesBase):
    user_id: str

    class Config:
        from_attributes = True


# Conversation Flow Models
class ConversationContext(BaseModel):
    user_id: str
    current_flow: str = "onboarding"
    flow_step: int = 0
    collected_data: dict = {}
    last_intent: Optional[str] = None


class IntentDetectionResult(BaseModel):
    intent: str
    confidence: float
    entities: dict = {}
    suggested_response: Optional[str] = None


class WhatsAppMessageRequest(BaseModel):
    messaging_product: str = "whatsapp"
    to: str
    type: str = "text"
    text: Optional[dict] = None
    image: Optional[dict] = None
    document: Optional[dict] = None
    interactive: Optional[dict] = None


class WhatsAppMessageResponse(BaseModel):
    messaging_product: str = "whatsapp"
    to: str
    type: str = "text"
    text: dict


class WhatsAppInteractiveButton(BaseModel):
    type: str = "reply"
    reply: dict


class WhatsAppInteractiveMessage(BaseModel):
    type: str = "button"
    body: dict
    action: dict