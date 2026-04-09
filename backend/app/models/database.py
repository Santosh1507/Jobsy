from sqlalchemy import Column, String, Integer, Boolean, DateTime, Text, JSON, ARRAY, ForeignKey, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
import enum

from app.core.database import Base


class SubscriptionTier(enum.Enum):
    FREE = "free"
    PRO = "pro"
    UNLIMITED = "unlimited"


class JobType(enum.Enum):
    FULL_TIME = "full-time"
    PART_TIME = "part-time"
    CONTRACT = "contract"
    INTERNSHIP = "intern"


class ApplicationStatus(enum.Enum):
    APPLIED = "applied"
    VIEWED = "viewed"
    SHORTLISTED = "shortlisted"
    INTERVIEW = "interview"
    OFFER = "offer"
    REJECTED = "rejected"
    WITHDRAWN = "withdrawn"


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    phone = Column(String(20), unique=True, nullable=False, index=True)
    whatsapp_id = Column(String(50), unique=True, index=True)
    name = Column(String(100))
    target_role = Column(String(100))
    experience_years = Column(Integer)
    current_ctc = Column(String(20))
    target_ctc = Column(String(20))
    preferred_cities = Column(ARRAY(String), default=[])
    skills = Column(ARRAY(String), default=[])
    blacklist_companies = Column(ARRAY(String), default=[])
    resume_url = Column(Text)
    resume_parsed = Column(JSON)
    subscription_tier = Column(SQLEnum(SubscriptionTier), default=SubscriptionTier.FREE)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    last_active_at = Column(DateTime(timezone=True))
    onboarding_completed = Column(Boolean, default=False)
    profile_version = Column(Integer, default=1)

    applications = relationship("Application", back_populates="user")
    message_logs = relationship("MessageLog", back_populates="user")


class Job(Base):
    __tablename__ = "jobs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    source = Column(String(50), nullable=False, index=True)
    source_job_id = Column(String(100))
    title = Column(String(200), nullable=False)
    company = Column(String(200), nullable=False)
    location = Column(String(100))
    description = Column(Text)
    requirements = Column(JSON)
    salary_min = Column(String(50))
    salary_max = Column(String(50))
    job_type = Column(SQLEnum(JobType))
    remote = Column(Boolean)
    apply_url = Column(Text)
    ats_platform = Column(String(50))
    posted_at = Column(DateTime(timezone=True))
    scraped_at = Column(DateTime(timezone=True), server_default=func.now())
    is_active = Column(Boolean, default=True)
    hash = Column(String(64), unique=True, index=True)

    applications = relationship("Application", back_populates="job")


class Application(Base):
    __tablename__ = "applications"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    job_id = Column(UUID(as_uuid=True), ForeignKey("jobs.id"), nullable=False, index=True)
    resume_version = Column(String(50), default="v1")
    status = Column(SQLEnum(ApplicationStatus), default=ApplicationStatus.APPLIED, index=True)
    applied_at = Column(DateTime(timezone=True), server_default=func.now())
    status_updated_at = Column(DateTime(timezone=True))
    ats_submission_id = Column(String(100))
    notes = Column(Text)
    follow_up_sent = Column(Boolean, default=False)
    tailored_keywords = Column(JSON)
    cover_letter = Column(Text)

    user = relationship("User", back_populates="applications")
    job = relationship("Job", back_populates="applications")


class SalaryData(Base):
    __tablename__ = "salary_data"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company = Column(String(200), nullable=False, index=True)
    role = Column(String(100), nullable=False)
    level = Column(String(50))
    city = Column(String(50))
    company_stage = Column(String(20))
    salary_min = Column(Integer)
    salary_max = Column(Integer)
    median_salary = Column(Integer)
    sample_size = Column(Integer)
    source = Column(String(50))
    recorded_at = Column(DateTime(timezone=True), server_default=func.now())


class MessageLog(Base):
    __tablename__ = "message_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    direction = Column(String(10), nullable=False)  # inbound, outbound
    message_text = Column(Text, nullable=False)
    intent = Column(String(50), index=True)
    message_meta = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="message_logs")


class UserPreferences(Base):
    __tablename__ = "user_preferences"

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), primary_key=True)
    daily_job_drop_time = Column(String(10), default="08:00")
    max_applications_per_day = Column(Integer, default=20)
    notify_on_status_change = Column(Boolean, default=True)
    notify_on_interview = Column(Boolean, default=True)
    weekly_digest = Column(Boolean, default=True)
    preferred_contact_method = Column(String(20), default="whatsapp")


class ConversationState(Base):
    __tablename__ = "conversation_states"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    current_flow = Column(String(50), default="onboarding")
    flow_step = Column(Integer, default=0)
    collected_data = Column(JSON, default={})
    last_intent = Column(String(50))
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())