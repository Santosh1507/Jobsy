import httpx
import json
from typing import Optional, List, Dict, Any
from loguru import logger

from app.core.config import settings


class OutreachService:
    """Service for recruiter outreach and email discovery"""
    
    def __init__(self):
        self.apollo_api_key = settings.APOLLO_API_KEY
        self.hunter_api_key = settings.HUNTER_API_KEY
    
    async def find_recruiter_email(
        self,
        company: str,
        role: str,
        linkedin_url: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """Find recruiter email using Apollo.io or Hunter.io"""
        
        # Try Apollo.io first
        if self.apollo_api_key:
            email = await self.find_with_apollo(company, role, linkedin_url)
            if email:
                return email
        
        # Fall back to Hunter.io
        if self.hunter_api_key:
            email = await self.find_with_hunter(company)
            if email:
                return email
        
        logger.warning(f"Could not find recruiter email for {company}")
        return None
    
    async def find_with_apollo(
        self,
        company: str,
        role: str,
        linkedin_url: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """Find email using Apollo.io API"""
        
        try:
            url = "https://api.apollo.io/api/v1/mixed_companies/search"
            
            payload = {
                "api_key": self.apollo_api_key,
                "q_organization_name": company,
                "page": 1
            }
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(url, json=payload)
                
                if response.status_code == 200:
                    data = response.json()
                    organizations = data.get("organizations", [])
                    
                    if organizations:
                        org = organizations[0]
                        
                        # Find people at this company
                        people = await self.find_people_at_apollo(
                            org.get("id"),
                            role
                        )
                        
                        if people:
                            return people[0]
                            
        except Exception as e:
            logger.error(f"Apollo.io error: {e}")
        
        return None
    
    async def find_people_at_apollo(
        self,
        organization_id: str,
        role_hint: str
    ) -> List[Dict]:
        """Find people at company using Apollo"""
        
        try:
            url = "https://api.apollo.io/api/v1/mixed_people/search"
            
            payload = {
                "api_key": self.apollo_api_key,
                "organization_ids": [organization_id],
                "page": 1,
                "per_page": 5
            }
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(url, json=payload)
                
                if response.status_code == 200:
                    data = response.json()
                    people = data.get("people", [])
                    
                    results = []
                    for person in people:
                        results.append({
                            "name": person.get("name"),
                            "title": person.get("title"),
                            "email": person.get("email"),
                            "linkedin_url": person.get("linkedin_url"),
                            "company": person.get("organization", {}).get("name")
                        })
                    
                    return results
                    
        except Exception as e:
            logger.error(f"Apollo people search error: {e}")
        
        return []
    
    async def find_with_hunter(
        self,
        company: str
    ) -> Optional[Dict[str, Any]]:
        """Find email using Hunter.io API"""
        
        try:
            url = f"https://api.hunter.io/v2/domain-search"
            
            params = {
                "domain": f"{company.lower().replace(' ', '')}.com",
                "api_key": self.hunter_api_key
            }
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(url, params=params)
                
                if response.status_code == 200:
                    data = response.json()
                    email_patterns = data.get("data", {}).get("email_patterns", [])
                    
                    if email_patterns:
                        return {
                            "email": email_patterns[0],
                            "confidence": data.get("data", {}).get("confidence"),
                            "company": company
                        }
                        
        except Exception as e:
            logger.error(f"Hunter.io error: {e}")
        
        return None
    
    async def generate_outreach_email(
        self,
        recruiter_name: str,
        company: str,
        role: str,
        user_data: Dict,
        job_data: Dict
    ) -> str:
        """Generate personalized outreach email using Ollama"""
        
        from app.services.ollama_service import ollama_service
        
        prompt = f"""Write a professional cold outreach email to a recruiter.

Recruiter: {recruiter_name}
Company: {company}
Role: {role}

Candidate:
- Name: {user_data.get('name', 'Candidate')}
- Current Role: {user_data.get('target_role', '')}
- Experience: {user_data.get('experience_years', 0)} years
- Skills: {', '.join(user_data.get('skills', [])[:5])}

Job Details (if available):
- Title: {job_data.get('title', role)}
- Description: {job_data.get('description', '')[:200]}

Write a brief, compelling email (100-150 words) that:
1. Clearly states the role interest
2. Highlights relevant experience
3. Includes call to action
4. Is professional but not generic

Subject line should be: "Interest in {role} opportunity at {company}"
"""

        return await ollama_service.generate(prompt, temperature=0.7)
    
    async def send_outreach_email(
        self,
        to_email: str,
        subject: str,
        body: str,
        user_email: str
    ) -> Dict[str, Any]:
        """Send outreach email (requires OAuth integration)"""
        
        # This would use Gmail API with OAuth
        # For now, return placeholder
        
        return {
            "success": True,
            "to": to_email,
            "subject": subject,
            "sent_from": user_email,
            "timestamp": "would be actual timestamp"
        }
    
    async def generate_linkedin_message(
        self,
        recruiter_name: str,
        company: str,
        role: str,
        user_data: Dict
    ) -> str:
        """Generate LinkedIn connection message"""
        
        return f"""Hi {recruiter_name},

I'm interested in {role} opportunities at {company}. With {user_data.get('experience_years', 0)} years of experience in {', '.join(user_data.get('skills', [])[:3])}, I believe I could be a strong fit.

Would love to connect and learn more about the team!

Best regards,
{user_data.get('name', 'Candidate')}"""


# Singleton instance
outreach_service = OutreachService()