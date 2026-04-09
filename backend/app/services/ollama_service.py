import httpx
import json
from typing import Optional, List, Dict, Any
from app.core.config import settings
from loguru import logger


class OllamaService:
    def __init__(self):
        self.base_url = settings.OLLAMA_BASE_URL
        self.model = settings.OLLAMA_MODEL
        self.timeout = 120.0

    async def chat(
        self,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        stream: bool = False
    ) -> Dict[str, Any]:
        """Send chat request to Ollama"""
        full_messages = []
        
        if system_prompt:
            full_messages.append({
                "role": "system",
                "content": system_prompt
            })
        
        full_messages.extend(messages)

        payload = {
            "model": self.model,
            "messages": full_messages,
            "temperature": temperature,
            "stream": stream
        }

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.post(
                    f"{self.base_url}/api/chat",
                    json=payload
                )
                response.raise_for_status()
                return response.json()
            except httpx.HTTPError as e:
                logger.error(f"Ollama HTTP error: {e}")
                raise Exception(f"Failed to communicate with Ollama: {str(e)}")
            except Exception as e:
                logger.error(f"Ollama error: {e}")
                raise Exception(f"Ollama service error: {str(e)}")

    async def generate(
        self,
        prompt: str,
        system: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ) -> str:
        """Generate text completion from Ollama"""
        payload = {
            "model": self.model,
            "prompt": prompt,
            "temperature": temperature,
        }
        
        if max_tokens:
            payload["options"] = {"num_predict": max_tokens}

        if system:
            payload["system"] = system

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.post(
                    f"{self.base_url}/api/generate",
                    json=payload
                )
                response.raise_for_status()
                result = response.json()
                return result.get("response", "")
            except Exception as e:
                logger.error(f"Ollama generate error: {e}")
                raise

    async def extract_keywords(self, job_description: str) -> List[str]:
        """Extract keywords from job description using Ollama"""
        prompt = f"""Extract the key skills, technologies, and requirements from this job description. 
Return ONLY a JSON list of strings (no other text).

Job Description:
{job_description}

Example output: ["Python", "FastAPI", "PostgreSQL", "AWS", "Docker"]"""

        result = await self.generate(prompt, temperature=0.3)
        
        try:
            keywords = json.loads(result)
            if isinstance(keywords, list):
                return keywords
        except json.JSONDecodeError:
            # Fallback: extract keywords manually
            words = result.strip().split(",")
            return [w.strip().strip('"[] ') for w in words if w.strip()]
        
        return []

    async def tailor_resume(
        self,
        original_resume: str,
        keywords: List[str],
        job_title: str
    ) -> str:
        """Generate tailored resume content with keywords injected"""
        prompt = f"""You are an expert resume writer. Tailor the following resume for this job position.
Add relevant keywords from the job description naturally into the experience sections.
Keep the same format and structure. Only modify content where necessary.

Job Title: {job_title}
Keywords to naturally incorporate: {', '.join(keywords)}

Original Resume:
{original_resume}

Return the tailored resume in the same format."""

        return await self.generate(prompt, temperature=0.5)

    async def generate_cover_letter(
        self,
        resume: str,
        job_description: str,
        company_name: str
    ) -> str:
        """Generate personalized cover letter"""
        prompt = f"""Write a professional cover letter for this job application.
Use the resume to highlight relevant experience.
Make it concise and compelling.

Company: {company_name}

Job Description:
{job_description}

Resume:
{resume}

Return ONLY the cover letter text."""

        return await self.generate(prompt, temperature=0.7)

    async def analyze_offer(
        self,
        offer_details: str,
        salary_data: List[Dict]
    ) -> Dict[str, Any]:
        """Analyze job offer against market data"""
        prompt = f"""Analyze this job offer against market data. Provide a structured analysis.

Offer Details:
{offer_details}

Market Salary Data:
{salary_data}

Return a JSON object with:
- percentile: (below, at, above market)
- recommendation: (accept, negotiate, reject)
- negotiation_strategy: specific advice
- key_points: list of strengths and concerns

Example: {{"percentile": "at_market", "recommendation": "negotiate", "negotiation_strategy": "...", "key_points": [...]}}"""

        result = await self.generate(prompt, temperature=0.5)
        
        try:
            return json.loads(result)
        except json.JSONDecodeError:
            return {
                "percentile": "unknown",
                "recommendation": "review_manually",
                "negotiation_strategy": "Unable to analyze automatically",
                "key_points": []
            }

    async def detect_intent(self, message: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        """Detect user intent from message"""
        
        system_prompt = """You are an intent classifier for a job search assistant on WhatsApp.
Classify the user's message into one of these intents:
- onboarding_start: User says hi/starts conversation for first time
- onboarding_name: User provides their name
- onboarding_role: User specifies target role
- onboarding_experience: User provides years of experience
- onboarding_location: User specifies preferred cities
- onboarding_salary: User provides salary expectations
- onboarding_resume: User sends/upload resume
- job_request: User asks for jobs/more jobs
- job_apply: User wants to apply to a job
- job_skip: User skips a job
- status_request: User asks about application status
- status_update: User updates application status
- interview_prep: User wants interview preparation
- offer_analysis: User receives or asks about offer
- intel_request: User asks about company/salary info
- profile_update: User wants to update profile
- pause_applications: User wants to pause auto-apply
- resume_request: User wants their resume
- help: User needs help
- unknown: Cannot determine intent

Return JSON with:
- intent: the detected intent
- confidence: 0.0-1.0
- entities: any extracted data (name, role, numbers, etc.)
- suggested_response: brief response suggestion"""

        context_str = f"\n\nCurrent context: {context}" if context else ""
        full_message = message + context_str

        result = await self.chat(
            messages=[{"role": "user", "content": full_message}],
            system_prompt=system_prompt,
            temperature=0.3
        )

        try:
            content = result.get("message", {}).get("content", "{}")
            return json.loads(content)
        except (json.JSONDecodeError, KeyError):
            return {
                "intent": "unknown",
                "confidence": 0.0,
                "entities": {},
                "suggested_response": "I didn't understand that. Can you try again?"
            }

    async def generate_interview_question(
        self,
        company: str,
        role: str,
        question_type: str = "technical"
    ) -> Dict[str, Any]:
        """Generate interview question for specific company/role"""
        
        prompt = f"""Generate an interview question for {role} at {company}.
Question type: {question_type}

If technical: focus on systems design, coding, problem-solving appropriate for the role.
If behavioral: use STAR format scenario.
If company-specific: include company context.

Return JSON:
{{"question": "...", "answer_tips": "...", "what_to_look_for": "..."}}"""

        result = await self.generate(prompt, temperature=0.6)
        
        try:
            return json.loads(result)
        except json.JSONDecodeError:
            return {
                "question": "Tell me about yourself",
                "answer_tips": "Focus on relevant experience",
                "what_to_look_for": "Communication skills"
            }

    async def generate_response(
        self,
        user_message: str,
        flow_name: str,
        collected_data: Dict,
        history: List[Dict]
    ) -> str:
        """Generate natural language response based on conversation flow"""
        
        flow_prompts = {
            "onboarding": """You are Jobsy, a friendly job search assistant on WhatsApp.
Guide the user through onboarding. Be conversational, brief, and helpful.
You've already collected: {collected_data}
Respond naturally to continue the conversation.""",
            
            "job_drop": """You are Jobsy presenting job matches to the user.
Keep messages concise (under 100 words).
Use formatting for readability. End with clear action options.""",
            
            "interview_prep": """You are Jobsy helping with interview preparation.
Be encouraging but focused. Provide specific, actionable advice.
Keep responses medium length.""",
            
            "offer_analysis": """You are Jobsy analyzing a job offer.
Be factual and helpful. Present data clearly.
Give clear recommendations with reasoning."""
        }

        system_prompt = flow_prompts.get(flow_name, "You are Jobsy, a helpful job search assistant.")
        system_prompt = system_prompt.format(collected_data=collected_data)

        messages = [{"role": "user", "content": user_message}]
        if history:
            for h in history[-5:]:  # Last 5 messages
                messages.append({
                    "role": h.get("role", "user"),
                    "content": h.get("content", "")
                })

        result = await self.chat(
            messages=messages,
            system_prompt=system_prompt,
            temperature=0.7
        )

        return result.get("message", {}).get("content", "")


# Singleton instance
ollama_service = OllamaService()