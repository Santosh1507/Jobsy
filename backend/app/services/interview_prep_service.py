from typing import Dict, List, Optional, Any
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.ollama_service import ollama_service


class InterviewPrepService:
    """Interview preparation service"""

    COMPANY_INTERVIEW_PATTERNS = {
        "razorpay": {
            "rounds": 4,
            "types": ["DSA", "System Design", "Coding", "Hiring Manager"],
            "tips": ["Focus on payments domain", "System design for high throughput", "DSA heavy"]
        },
        "cred": {
            "rounds": 3,
            "types": ["Low-level coding", "Problem Solving", "Culture Fit"],
            "tips": ["Focus on clean code", "Edge cases matter", "Be ready for obscure questions"]
        },
        "swiggy": {
            "rounds": 4,
            "types": ["DSA", "Backend", "System Design", "Manager"],
            "tips": ["Delivery logistics problems", "Scale challenges", "ML basics help"]
        },
        "phonepe": {
            "rounds": 3,
            "types": ["Technical", "System Design", "Manager"],
            "tips": ["UPI payment knowledge", "High availability focus", "Fintech domain"]
        },
        "flipkart": {
            "rounds": 5,
            "types": ["DSA", "DSA", "System Design", "Domain", "Hiring Manager"],
            "tips": ["E-commerce logistics", "Inventory systems", "Scale problems"]
        },
        "amazon": {
            "rounds": 4,
            "types": ["DSA", "DSA", "System Design", "Bar Raiser"],
            "tips": ["Leadership principles mandatory", "STAR method required", "Customer obsession"]
        }
    }

    async def generate_questions(
        self,
        company: str,
        role: str,
        question_type: str = "mixed"
    ) -> Dict[str, Any]:
        """Generate interview questions for company/role"""

        # Get company-specific patterns
        company_lower = company.lower()
        pattern = None

        for key in self.COMPANY_INTERVIEW_PATTERNS:
            if key in company_lower:
                pattern = self.COMPANY_INTERVIEW_PATTERNS[key]
                break

        # Generate via Ollama
        prompt = f"""Generate interview questions for {role} at {company}.

Question type: {question_type}

{ f"Company pattern: {pattern}" if pattern else "" }

Return JSON with 5 questions, each having:
- question: the actual question
- type: technical/behavioral/system design
- difficulty: easy/medium/hard
- sample_answer: brief answer outline
- tips: what interviewers look for"""

        result = await ollama_service.generate(prompt, temperature=0.7)

        try:
            import json
            return json.loads(result)
        except:
            return {"questions": [], "error": "Could not parse questions"}

    async def start_mock_interview(
        self,
        company: str,
        role: str,
        user_data: Dict
    ) -> Dict[str, Any]:
        """Start an interactive mock interview session"""

        pattern = None
        for key, val in self.COMPANY_INTERVIEW_PATTERNS.items():
            if key in company.lower():
                pattern = val
                break

        if pattern:
            intro = f"""🎯 *Mock Interview: {role} at {company}*

Company typically has {pattern['rounds']} rounds:
{', '.join(pattern['types'])}

Tips for this company:
{chr(10).join(f"• {t}" for t in pattern['tips'])}

Let's begin with the first question. You'll answer, then I'll give feedback.

Ready? Type 'start' to begin."""
        else:
            intro = f"""🎯 *Mock Interview: {role} at {company}*

Let's practice for your interview. I'll ask questions, you answer, and I'll give feedback.

Type 'start' when ready!"""

        return {
            "intro": intro,
            "company": company,
            "role": role,
            "question_count": pattern["rounds"] if pattern else 3
        }

    async def evaluate_answer(
        self,
        question: str,
        user_answer: str,
        question_type: str
    ) -> Dict[str, Any]:
        """Evaluate user's answer and provide feedback"""

        prompt = f"""Evaluate this interview answer and provide feedback.

Question: {question}
Type: {question_type}
Answer: {user_answer}

Return JSON:
{{
    "score": 1-10,
    "strengths": ["list of what they did well"],
    "improvements": ["list of what to improve"],
    "better_answer": "improved version of their answer",
    "tip": "one actionable tip"
}}"""

        result = await ollama_service.generate(prompt, temperature=0.6)

        try:
            import json
            return json.loads(result)
        except:
            return {
                "score": 5,
                "feedback": "Good effort! Try to be more specific with examples.",
                "tip": "Use the STAR method for behavioral questions."
            }

    async def generate_star_question(self, category: str = "leadership") -> Dict[str, Any]:
        """Generate STAR-format behavioral question"""

        categories = {
            "leadership": "Describe a time you led a team through a difficult project.",
            "conflict": "Tell me about a time you disagreed with a teammate.",
            "failure": "Describe a project that didn't go as planned. What did you learn?",
            "initiative": "Tell me about something you did without being asked.",
            "problem-solving": "Describe a complex problem you solved."
        }

        question = categories.get(category, categories["leadership"])

        return {
            "question": question,
            "format": "STAR",
            "tips": [
                "S - Situation: Set the context",
                "T - Task: What was your responsibility?",
                "A - Action: What did you specifically do?",
                "R - Result: What was the outcome?"
            ]
        }


# Singleton instance
interview_prep_service = InterviewPrepService()