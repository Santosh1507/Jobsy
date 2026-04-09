# Portal Scanner Configuration
# Pre-configured companies from career-ops for job scanning

PORTAL_CONFIG = {
    "title_filter": {
        "positive": [
            "AI", "ML", "LLM", "Agent", "Agentic", "GenAI", "Generative AI",
            "NLP", "LLMOps", "MLOps", "Voice AI", "Conversational AI",
            "Platform Engineer", "Solutions Architect", "Solutions Engineer",
            "Forward Deployed", "Deployed Engineer", "Customer Engineer",
            "Product Manager", "Technical PM", "Automation", "Backend"
        ],
        "negative": [
            "Junior", "Intern", ".NET", "Java ", "iOS", "Android", "PHP",
            "Ruby", "Embedded", "Firmware", "FPGA", "ASIC", "Blockchain",
            "Web3", "Crypto", "Salesforce Admin", "SAP ", "Oracle", "Mainframe"
        ]
    },
    
    "tracked_companies": [
        # AI Labs
        {"name": "Anthropic", "careers_url": "https://job-boards.greenhouse.io/anthropic", "api": "https://boards-api.greenhouse.io/v1/boards/anthropic/jobs", "enabled": True},
        {"name": "OpenAI", "careers_url": "https://openai.com/careers", "scan_method": "websearch", "enabled": True},
        {"name": "Cohere", "careers_url": "https://jobs.ashbyhq.com/cohere", "enabled": True},
        {"name": "Mistral AI", "careers_url": "https://jobs.lever.co/mistral", "enabled": True},
        
        # Voice AI
        {"name": "ElevenLabs", "careers_url": "https://jobs.ashbyhq.com/elevenlabs", "enabled": True},
        {"name": "Deepgram", "careers_url": "https://jobs.ashbyhq.com/deepgram", "enabled": True},
        {"name": "Vapi", "careers_url": "https://jobs.ashbyhq.com/vapi", "enabled": True},
        {"name": "Hume AI", "careers_url": "https://job-boards.greenhouse.io/humeai", "enabled": True},
        
        # AI Platforms
        {"name": "Retool", "careers_url": "https://retool.com/careers", "enabled": True},
        {"name": "Airtable", "careers_url": "https://job-boards.greenhouse.io/airtable", "enabled": True},
        {"name": "Vercel", "careers_url": "https://job-boards.greenhouse.io/vercel", "enabled": True},
        {"name": "Temporal", "careers_url": "https://job-boards.greenhouse.io/temporal", "enabled": True},
        {"name": "LangChain", "careers_url": "https://jobs.ashbyhq.com/langchain", "enabled": True},
        {"name": "Pinecone", "careers_url": "https://jobs.ashbyhq.com/pinecone", "enabled": True},
        
        # LLMOps
        {"name": "Langfuse", "careers_url": "https://langfuse.com/careers", "enabled": True},
        {"name": "Arize AI", "careers_url": "https://job-boards.greenhouse.io/arizeai", "enabled": True},
        
        # Contact Center AI
        {"name": "Intercom", "careers_url": "https://job-boards.greenhouse.io/intercom", "enabled": True},
        {"name": "Ada", "careers_url": "https://job-boards.greenhouse.io/ada", "enabled": True},
        {"name": "Sierra", "careers_url": "https://jobs.ashbyhq.com/sierra", "enabled": True},
        
        # Enterprise
        {"name": "Twilio", "careers_url": "https://www.twilio.com/en-us/company/jobs", "enabled": True},
        {"name": "Salesforce", "careers_url": "https://careers.salesforce.com", "enabled": True},
        {"name": "Gong", "careers_url": "https://www.gong.io/careers", "enabled": True},
        
        # No-Code/Automation
        {"name": "n8n", "careers_url": "https://jobs.ashbyhq.com/n8n", "enabled": True},
        {"name": "Zapier", "careers_url": "https://jobs.ashbyhq.com/zapier", "enabled": True},
        
        # India-specific (from PRD)
        {"name": "Razorpay", "careers_url": "https://razorpay.com/careers", "enabled": True},
        {"name": "Cred", "careers_url": "https://cred.boss.job", "enabled": True},
        {"name": "Meesho", "careers_url": "https://meesho.com/careers", "enabled": True},
        {"name": "PhonePe", "careers_url": "https://phonepe.com/careers", "enabled": True},
        {"name": "Swiggy", "careers_url": "https://swiggy.com/careers", "enabled": True},
        {"name": "Flipkart", "careers_url": "https://flipkart.com/careers", "enabled": True},
        {"name": "Unacademy", "careers_url": "https://unacademy.com/careers", "enabled": True},
        {"name": "Groww", "careers_url": "https://groww.in/careers", "enabled": True},
        {"name": "CoinDCX", "careers_url": "https://coindcx.com/careers", "enabled": True},
    ]
}

# Company-specific interview patterns (from career-ops)
COMPANY_INTERVIEW_PATTERNS = {
    "razorpay": {"rounds": 4, "types": ["DSA", "System Design", "Coding", "Hiring Manager"], "tips": ["Focus on payments", "System design for high throughput"]},
    "cred": {"rounds": 3, "types": ["Low-level coding", "Problem Solving", "Culture Fit"], "tips": ["Focus on clean code", "Edge cases matter"]},
    "amazon": {"rounds": 4, "types": ["DSA", "DSA", "System Design", "Bar Raiser"], "tips": ["Leadership principles mandatory", "STAR method required"]},
    "flipkart": {"rounds": 5, "types": ["DSA", "DSA", "System Design", "Domain", "Hiring Manager"], "tips": ["E-commerce logistics", "Scale problems"]},
    "google": {"rounds": 4, "types": ["DSA", "DSA", "System Design", "Googlyness"], "tips": ["Think out loud", "Edge cases"]},
    "microsoft": {"rounds": 4, "types": ["DSA", "Low-level", "System Design", "Hiring Manager"], "tips": ["Focus on scalability"]},
    "meta": {"rounds": 4, "types": ["DSA", "DSA", "System Design", "Hiring Manager"], "tips": ["Think about scaling", "Common patterns"]},
}


def get_portal_config() -> dict:
    """Get portal scanner configuration"""
    return PORTAL_CONFIG


def get_company_pattern(company_name: str) -> dict:
    """Get interview pattern for a company"""
    company_lower = company_name.lower()
    for key, pattern in COMPANY_INTERVIEW_PATTERNS.items():
        if key in company_lower:
            return pattern
    return {"rounds": 3, "types": ["Technical", "System Design", "Manager"], "tips": ["Prepare for technical questions"]}


def get_enabled_companies() -> list:
    """Get list of enabled companies"""
    return [c for c in PORTAL_CONFIG["tracked_companies"] if c.get("enabled", False)]