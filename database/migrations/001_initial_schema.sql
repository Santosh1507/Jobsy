-- WhatsApp Job Platform Database Schema
-- Compatible with PostgreSQL/Supabase

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    phone VARCHAR(20) UNIQUE NOT NULL,
    whatsapp_id VARCHAR(50) UNIQUE,
    name VARCHAR(100),
    target_role VARCHAR(100),
    experience_years INTEGER,
    current_ctc VARCHAR(20),
    target_ctc VARCHAR(20),
    preferred_cities TEXT[] DEFAULT '{}',
    skills TEXT[] DEFAULT '{}',
    blacklist_companies TEXT[] DEFAULT '{}',
    resume_url TEXT,
    resume_parsed JSONB,
    subscription_tier VARCHAR(20) DEFAULT 'free',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    last_active_at TIMESTAMPTZ,
    onboarding_completed BOOLEAN DEFAULT FALSE,
    profile_version INTEGER DEFAULT 1
);

CREATE INDEX IF NOT EXISTS idx_users_phone ON users(phone);
CREATE INDEX IF NOT EXISTS idx_users_whatsapp_id ON users(whatsapp_id);
CREATE INDEX IF NOT EXISTS idx_users_onboarding ON users(onboarding_completed);

-- Jobs table
CREATE TABLE IF NOT EXISTS jobs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    source VARCHAR(50) NOT NULL,
    source_job_id VARCHAR(100),
    title VARCHAR(200) NOT NULL,
    company VARCHAR(200) NOT NULL,
    location VARCHAR(100),
    description TEXT,
    requirements JSONB,
    salary_min VARCHAR(50),
    salary_max VARCHAR(50),
    job_type VARCHAR(20),
    remote BOOLEAN,
    apply_url TEXT,
    ats_platform VARCHAR(50),
    posted_at TIMESTAMPTZ,
    scraped_at TIMESTAMPTZ DEFAULT NOW(),
    is_active BOOLEAN DEFAULT TRUE,
    hash VARCHAR(64) UNIQUE
);

CREATE INDEX IF NOT EXISTS idx_jobs_source ON jobs(source);
CREATE INDEX IF NOT EXISTS idx_jobs_company ON jobs(company);
CREATE INDEX IF NOT EXISTS idx_jobs_hash ON jobs(hash);
CREATE INDEX IF NOT EXISTS idx_jobs_is_active ON jobs(is_active);

-- Applications table
CREATE TABLE IF NOT EXISTS applications (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    job_id UUID REFERENCES jobs(id) ON DELETE CASCADE,
    resume_version VARCHAR(50) DEFAULT 'v1',
    status VARCHAR(30) DEFAULT 'applied',
    applied_at TIMESTAMPTZ DEFAULT NOW(),
    status_updated_at TIMESTAMPTZ,
    ats_submission_id VARCHAR(100),
    notes TEXT,
    follow_up_sent BOOLEAN DEFAULT FALSE,
    tailored_keywords JSONB,
    cover_letter TEXT
);

CREATE INDEX IF NOT EXISTS idx_applications_user_id ON applications(user_id);
CREATE INDEX IF NOT EXISTS idx_applications_job_id ON applications(job_id);
CREATE INDEX IF NOT EXISTS idx_applications_status ON applications(status);

-- Salary data table
CREATE TABLE IF NOT EXISTS salary_data (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company VARCHAR(200) NOT NULL,
    role VARCHAR(100) NOT NULL,
    level VARCHAR(50),
    city VARCHAR(50),
    company_stage VARCHAR(20),
    salary_min INTEGER,
    salary_max INTEGER,
    median_salary INTEGER,
    sample_size INTEGER,
    source VARCHAR(50),
    recorded_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_salary_data_company ON salary_data(company);
CREATE INDEX IF NOT EXISTS idx_salary_data_role ON salary_data(role);

-- Message logs table
CREATE TABLE IF NOT EXISTS message_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    direction VARCHAR(10) NOT NULL,
    message_text TEXT NOT NULL,
    intent VARCHAR(50),
    metadata JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_message_logs_user_id ON message_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_message_logs_intent ON message_logs(intent);

-- User preferences table
CREATE TABLE IF NOT EXISTS user_preferences (
    user_id UUID PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
    daily_job_drop_time VARCHAR(10) DEFAULT '08:00',
    max_applications_per_day INTEGER DEFAULT 20,
    notify_on_status_change BOOLEAN DEFAULT TRUE,
    notify_on_interview BOOLEAN DEFAULT TRUE,
    weekly_digest BOOLEAN DEFAULT TRUE,
    preferred_contact_method VARCHAR(20) DEFAULT 'whatsapp'
);

-- Conversation states table
CREATE TABLE IF NOT EXISTS conversation_states (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
    current_flow VARCHAR(50) DEFAULT 'onboarding',
    flow_step INTEGER DEFAULT 0,
    collected_data JSONB DEFAULT '{}',
    last_intent VARCHAR(50),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Triggers for updated_at
CREATE TRIGGER update_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER update_conversation_states_updated_at
    BEFORE UPDATE ON conversation_states
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at();

-- Sample salary data (India-specific)
INSERT INTO salary_data (company, role, level, city, company_stage, salary_min, salary_max, median_salary, sample_size, source) VALUES
('Razorpay', 'Senior Backend Engineer', 'SDE-2', 'Bangalore', 'series-c', 2000000, 2600000, 2300000, 45, 'grapevine'),
('Razorpay', 'Staff Engineer', 'SDE-3', 'Bangalore', 'series-c', 3500000, 5000000, 4200000, 20, 'grapevine'),
('Cred', 'Senior Backend Engineer', 'SDE-2', 'Bangalore', 'series-d', 2200000, 2800000, 2500000, 35, 'grapevine'),
('Meesho', 'Backend Engineer', 'SDE-1', 'Bangalore', 'series-c', 1200000, 1800000, 1500000, 50, 'grapevine'),
('Meesho', 'Senior Backend Engineer', 'SDE-2', 'Bangalore', 'series-c', 1800000, 2400000, 2100000, 40, 'grapevine'),
('PhonePe', 'Senior Backend Engineer', 'SDE-2', 'Bangalore', 'public', 2000000, 2600000, 2300000, 55, 'grapevine'),
('Swiggy', 'Senior Backend Engineer', 'SDE-2', 'Bangalore', 'series-i', 1800000, 2400000, 2100000, 30, 'grapevine'),
('Unacademy', 'Senior Backend Engineer', 'SDE-2', 'Bangalore', 'series-g', 1600000, 2200000, 1900000, 25, 'grapevine'),
('CoinDCX', 'Backend Engineer', 'SDE-1', 'Bangalore', 'series-b', 1000000, 1500000, 1250000, 20, 'grapevine'),
('Groww', 'Senior Backend Engineer', 'SDE-2', 'Bangalore', 'series-d', 2200000, 2800000, 2500000, 35, 'grapevine');

-- Grant necessary permissions (for Supabase)
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO postgres;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO postgres;