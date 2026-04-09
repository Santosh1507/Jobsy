import json
from typing import Dict, List, Optional, Any
from loguru import logger

from app.services.ollama_service import ollama_service


class JobEvaluatorService:
    """Job evaluation using career-ops A-F scoring system"""

    ARCHETYPES = {
        "fde": {
            "name": "Forward Deployed Engineer",
            "description": "Customer-facing engineers who deploy and integrate solutions",
            "proof_points": ["delivery speed", "client-facing", "integration", "technical sales"]
        },
        "sa": {
            "name": "Solutions Architect",
            "description": "Designs technical solutions for complex customer problems",
            "proof_points": ["system design", "architecture decisions", " integrations", "technical leadership"]
        },
        "pm": {
            "name": "Product Manager",
            "description": "Owns product strategy and execution",
            "proof_points": ["product discovery", "metrics", "roadmap", "stakeholder management"]
        },
        "llmops": {
            "name": "LLM/MLOps Engineer",
            "description": "Operationalizes ML/LLM models in production",
            "proof_points": ["evals", "observability", "pipelines", "model optimization"]
        },
        "agentic": {
            "name": "Agentic/AI Engineer",
            "description": "Builds AI agents and autonomous systems",
            "proof_points": ["multi-agent", "HITL", "orchestration", "error handling"]
        },
        "transformation": {
            "name": "Transformation/Automation Lead",
            "description": "Leads organizational change through automation",
            "proof_points": ["change management", "adoption", "scaling", "stakeholder alignment"]
        }
    }

    async def evaluate_job(
        self,
        job_data: Dict,
        user_data: Dict,
        cv_text: str = ""
    ) -> Dict[str, Any]:
        """Perform full A-F evaluation of a job"""

        # Step 0: Detect archetype
        archetype = await self.detect_archetype(job_data)

        # Block A: Role Summary
        block_a = await self.generate_block_a(job_data, archetype)

        # Block B: CV Match
        block_b = await self.generate_block_b(job_data, user_data, cv_text, archetype)

        # Block C: Level & Strategy
        block_c = await self.generate_block_c(job_data, user_data, archetype)

        # Block D: Compensation & Demand
        block_d = await self.generate_block_d(job_data)

        # Block E: Personalization Plan
        block_e = await self.generate_block_e(job_data, user_data)

        # Block F: Interview Plan
        block_f = await self.generate_block_f(job_data, archetype)

        # Calculate overall score
        score = self.calculate_score(block_b, block_d)

        return {
            "archetype": archetype,
            "blocks": {
                "a": block_a,
                "b": block_b,
                "c": block_c,
                "d": block_d,
                "e": block_e,
                "f": block_f
            },
            "score": score,
            "recommendation": self.get_recommendation(score)
        }

    async def detect_archetype(self, job_data: Dict) -> Dict[str, Any]:
        """Detect job archetype from title and description"""

        prompt = f"""Classify this job into one of these archetypes:
- fde (Forward Deployed Engineer)
- sa (Solutions Architect)
- pm (Product Manager)
- llmops (LLM/MLOps Engineer)
- agentic (Agentic/AI Engineer)
- transformation (Transformation/Automation Lead)

Job Title: {job_data.get('title', '')}
Company: {job_data.get('company', '')}
Description: {job_data.get('description', '')[:500]}

Return JSON:
{{"archetype": "one of the above", "confidence": 0.0-1.0, "reasoning": "brief explanation"}}"""

        result = await ollama_service.generate(prompt, temperature=0.3)

        try:
            return json.loads(result)
        except:
            return {"archetype": "fde", "confidence": 0.5, "reasoning": "Default"}

    async def generate_block_a(self, job_data: Dict, archetype: Dict) -> Dict[str, Any]:
        """Block A: Role Summary"""

        return {
            "archetype_detected": archetype.get("archetype", "unknown"),
            "domain": self.extract_domain(job_data),
            "function": self.extract_function(job_data),
            "seniority": self.extract_seniority(job_data),
            "remote": job_data.get("remote", False),
            "team_size": job_data.get("team_size"),
            "tldr": f"{job_data.get('title', 'Role')} at {job_data.get('company', 'Company')}"
        }

    async def generate_block_b(
        self,
        job_data: Dict,
        user_data: Dict,
        cv_text: str,
        archetype: Dict
    ) -> Dict[str, Any]:
        """Block B: CV Match with requirements"""

        requirements = job_data.get("requirements", {})
        if isinstance(requirements, str):
            requirements = {"text": requirements}

        prompt = f"""Analyze how well the candidate matches job requirements.

Job Requirements: {requirements.get('text', job_data.get('description', ''))[:1000]}

Candidate Skills: {', '.join(user_data.get('skills', []))}
Candidate Experience: {user_data.get('experience_years', 0)} years
CV Text: {cv_text[:1000] if cv_text else 'Not provided'}

Return JSON:
{{
    "matched_requirements": ["list of requirements that match"],
    "gaps": ["list of gaps with mitigation strategy"],
    "match_percentage": 0-100
}}"""

        result = await ollama_service.generate(prompt, temperature=0.4)

        try:
            return json.loads(result)
        except:
            return {"matched_requirements": [], "gaps": [], "match_percentage": 50}

    async def generate_block_c(
        self,
        job_data: Dict,
        user_data: Dict,
        archetype: Dict
    ) -> Dict[str, Any]:
        """Block C: Level and Strategy"""

        job_level = self.extract_seniority(job_data)
        user_level = user_data.get("target_level", "mid")

        return {
            "job_level": job_level,
            "user_level": user_level,
            "strategy": self.get_level_strategy(job_level, user_level),
            "sell_senior_tips": self.get_senior_selling_tips(archetype),
            "downlevel_plan": self.get_downlevel_plan()
        }

    async def generate_block_d(self, job_data: Dict) -> Dict[str, Any]:
        """Block D: Compensation and Demand"""

        salary = job_data.get("salary_min", "")
        if not salary and job_data.get("salary"):
            salary = job_data.get("salary")

        return {
            "salary_range": salary,
            "company_stage": job_data.get("company_stage", "unknown"),
            "demand_level": "high",  # Would use web search in production
            "sources": ["market data"]
        }

    async def generate_block_e(
        self,
        job_data: Dict,
        user_data: Dict
    ) -> Dict[str, Any]:
        """Block E: Personalization Plan"""

        prompt = f"""Suggest top 5 changes to CV and LinkedIn to maximize match.

Job: {job_data.get('title')} at {job_data.get('company')}
Requirements: {job_data.get('description', '')[:500]}
Current Skills: {', '.join(user_data.get('skills', []))}

Return JSON:
{{
    "cv_changes": ["change 1", "change 2", ...],
    "linkedin_changes": ["change 1", "change 2", ...]
}}"""

        result = await ollama_service.generate(prompt, temperature=0.5)

        try:
            return json.loads(result)
        except:
            return {"cv_changes": [], "linkedin_changes": []}

    async def generate_block_f(
        self,
        job_data: Dict,
        archetype: Dict
    ) -> Dict[str, Any]:
        """Block F: Interview Plan with STAR stories"""

        prompt = f"""Generate interview preparation plan for this role.

Job: {job_data.get('title')} at {job_data.get('company')}
Archetype: {archetype.get('archetype', 'fde')}

Include:
- 3-5 key topics to prepare
- 2 STAR story suggestions
- Any company-specific tips

Return JSON:
{{
    "topics": ["topic 1", ...],
    "star_stories": [{{"scenario": "...", "task": "...", "action": "...", "result": "...", "reflection": "..."}}],
    "company_tips": ["tip 1", ...]
}}"""

        result = await ollama_service.generate(prompt, temperature=0.6)

        try:
            return json.loads(result)
        except:
            return {"topics": [], "star_stories": [], "company_tips": []}

    def calculate_score(self, block_b: Dict, block_d: Dict) -> float:
        """Calculate overall score (1-5)"""

        match_pct = block_b.get("match_percentage", 50) / 100
        demand = block_d.get("demand_level", "medium")

        # Score formula
        base_score = 2 + (match_pct * 2)  # 2-4 based on match
        if demand == "high":
            base_score += 0.5
        elif demand == "low":
            base_score -= 0.5

        return min(5.0, max(1.0, base_score))

    def get_recommendation(self, score: float) -> str:
        """Get recommendation based on score"""

        if score >= 4.5:
            return "strong_apply"
        elif score >= 3.5:
            return "apply"
        elif score >= 2.5:
            return "consider"
        else:
            return "skip"

    def extract_domain(self, job_data: Dict) -> str:
        """Extract domain from job"""
        desc = job_data.get("description", "").lower()
        
        if any(x in desc for x in ["agent", "llm", "genai", "gpt", "ai model"]):
            return "agentic"
        elif any(x in desc for x in ["llmops", "mlops", "ml ", "machine learning"]):
            return "llmops"
        elif any(x in desc for x in ["platform", "infrastructure", "backend"]):
            return "platform"
        elif any(x in desc for x in ["enterprise", "b2b", "saas"]):
            return "enterprise"
        return "general"

    def extract_function(self, job_data: Dict) -> str:
        """Extract function type"""
        title = job_data.get("title", "").lower()
        
        if any(x in title for x in ["deploy", "forward", "customer"]):
            return "deploy"
        elif any(x in title for x in ["architect", "solution", "design"]):
            return "consult"
        elif any(x in title for x in ["manage", "product", "owner"]):
            return "manage"
        return "build"

    def extract_seniority(self, job_data: Dict) -> str:
        """Extract seniority level"""
        title = job_data.get("title", "").lower()
        
        if any(x in title for x in ["staff", "principal", "director", "head", "vp"]):
            return "senior"
        elif any(x in title for x in ["senior", "lead", "sr"]):
            return "mid-senior"
        elif any(x in title for x in ["junior", "jr", "intern", "entry"]):
            return "junior"
        return "mid"

    def get_level_strategy(self, job_level: str, user_level: str) -> Dict[str, str]:
        """Get strategy for level matching"""
        
        strategies = {
            ("senior", "senior"): {"approach": "standard", "tips": "Highlight relevant achievements"},
            ("senior", "mid"): {"approach": "sell_senior", "tips": "Position experience as equivalent"},
            ("mid", "senior"): {"approach": "downlevel", "tips": "Be prepared to negotiate level"},
            ("mid", "mid"): {"approach": "standard", "tips": "Strong match, emphasize growth"},
        }
        
        return strategies.get((job_level, user_level), {"approach": "standard", "tips": "Apply normally"})

    def get_senior_selling_tips(self, archetype: Dict) -> List[str]:
        """Get tips for selling seniority"""
        
        archetype_id = archetype.get("archetype", "fde")
        
        tips_map = {
            "fde": ["Emphasize delivery speed", "Client-facing success stories", "Quick ramp-up time"],
            "sa": ["System design experience", "Architecture decisions", "Customer technical deep-dives"],
            "pm": ["Product metrics", "Roadmap delivery", "Stakeholder management"],
            "llmops": ["Production deployments", "Evals & monitoring", "Pipeline optimization"],
            "agentic": ["Multi-agent systems", "Error handling patterns", "HITL workflows"],
            "transformation": ["Adoption metrics", "Change management", "Scaling success"]
        }
        
        return tips_map.get(archetype_id, ["Highlight relevant achievements"])

    def get_downlevel_plan(self) -> Dict[str, str]:
        """Get plan for if downleveled"""
        
        return {
            "accept_if_fair": "Compensation should match level expectations",
            "negotiate_review": "Request 6-month performance review",
            "clear_criteria": "Get clear promotion criteria in writing"
        }


# Singleton instance
job_evaluator = JobEvaluatorService()