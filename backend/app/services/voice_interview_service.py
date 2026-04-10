import asyncio
import json
import random
from typing import Dict, List, Optional
from datetime import datetime

COMPANY_VOICE_PATTERNS = {
    "google": {
        "focus": ["system design", "data structures", "algorithmic thinking"],
        "tone": "analytical and collaborative",
        "common_questions": [
            "Design a system that scales to millions of users",
            "Explain the trade-offs between different data structures",
            "How would you optimize a slow database query?"
        ]
    },
    "meta": {
        "focus": ["product sense", "scalability", "technical depth"],
        "tone": "direct and product-focused",
        "common_questions": [
            "Design Instagram search feature",
            "How would you handle 10x traffic growth?",
            "Explain your most complex technical project"
        ]
    },
    "amazon": {
        "focus": ["leadership principles", "customer obsession", "ownership"],
        "tone": "structured and principle-driven",
        "common_questions": [
            "Tell me about a time you had a disagreement with a stakeholder",
            "Describe a situation where you had to meet a tight deadline",
            "Give an example of when you took ownership of a problem"
        ]
    },
    "apple": {
        "focus": ["product quality", "attention to detail", "privacy"],
        "tone": "minimalist and quality-focused",
        "common_questions": [
            "How do you ensure quality in your code?",
            "Describe your design process for a feature",
            "How do you handle user privacy concerns?"
        ]
    },
    "default": {
        "focus": ["problem-solving", "communication", "teamwork"],
        "tone": "professional and collaborative",
        "common_questions": [
            "Tell me about yourself",
            "Why do you want to work here?",
            "Describe a challenging project you worked on"
        ]
    }
}

INTERVIEW_TYPES = {
    "behavioral": {
        "duration_minutes": 15,
        "questions_count": 5,
        "focus": "STAR-based questions about past experiences"
    },
    "technical": {
        "duration_minutes": 30,
        "questions_count": 4,
        "focus": "Coding and system design questions"
    },
    "mixed": {
        "duration_minutes": 25,
        "questions_count": 5,
        "focus": "Both behavioral and technical questions"
    },
    "cultural_fit": {
        "duration_minutes": 15,
        "questions_count": 5,
        "focus": "Company values and team dynamics"
    }
}


class VoiceMockInterviewService:
    
    def __init__(self):
        self.sessions: Dict[str, dict] = {}
    
    def start_interview(
        self,
        user_id: str,
        company: str,
        role: str,
        interview_type: str = "mixed"
    ) -> dict:
        """Start a new mock interview session"""
        
        company_key = company.lower() if company.lower() in COMPANY_VOICE_PATTERNS else "default"
        company_pattern = COMPANY_VOICE_PATTERNS.get(company_key, COMPANY_VOICE_PATTERNS["default"])
        type_config = INTERVIEW_TYPES.get(interview_type, INTERVIEW_TYPES["mixed"])
        
        session_id = f"interview_{user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        questions = self._generate_questions(company_pattern, type_config, interview_type)
        
        session = {
            "session_id": session_id,
            "user_id": user_id,
            "company": company,
            "role": role,
            "interview_type": interview_type,
            "questions": questions,
            "current_question_index": 0,
            "answers": [],
            "start_time": datetime.now().isoformat(),
            "status": "in_progress",
            "company_pattern": company_pattern
        }
        
        self.sessions[session_id] = session
        
        return {
            "session_id": session_id,
            "company": company,
            "role": role,
            "interview_type": interview_type,
            "duration_minutes": type_config["duration_minutes"],
            "questions_count": type_config["questions_count"],
            "first_question": questions[0],
            "tips": self._get_interview_tips(company_pattern)
        }
    
    def _generate_questions(self, company_pattern: dict, type_config: dict, interview_type: str) -> List[dict]:
        """Generate interview questions based on company and type"""
        
        questions = []
        
        if interview_type in ["behavioral", "mixed"]:
            behavioral_questions = [
                {
                    "type": "behavioral",
                    "category": "leadership",
                    "question": "Tell me about a time you demonstrated leadership in a difficult situation.",
                    "star_framework": "Situation: Describe the context\nTask: What needed to be done\nAction: What you specifically did\nResult: The outcome and what you learned",
                    "sample_answer": "When our team was facing a critical deadline, I stepped up to coordinate...",
                    "time_guidance": "Aim for 2-3 minutes"
                },
                {
                    "type": "behavioral",
                    "category": "problem_solving",
                    "question": "Describe a complex problem you faced and how you solved it.",
                    "star_framework": "Situation: Set the context\nTask: Your responsibility\nAction: Specific steps you took\nResult: Measurable outcomes",
                    "sample_answer": "Our production system was experiencing intermittent failures...",
                    "time_guidance": "Aim for 2-3 minutes"
                },
                {
                    "type": "behavioral",
                    "category": "collaboration",
                    "question": "Tell me about a time you had to work with a difficult team member or stakeholder.",
                    "star_framework": "Situation: The context\nTask: Your role\nAction: How you approached the relationship\nResult: Outcome and lessons learned",
                    "sample_answer": "I was working with a team member who had different priorities...",
                    "time_guidance": "Aim for 2 minutes"
                },
                {
                    "type": "behavioral",
                    "category": "failure",
                    "question": "Tell me about a time you failed or made a mistake. How did you handle it?",
                    "star_framework": "Situation: What happened\nTask: Your responsibility\nAction: How you addressed it\nResult: What you learned and changed",
                    "sample_answer": "I once pushed code that caused a production outage...",
                    "time_guidance": "Be honest - focus on learning"
                },
                {
                    "type": "behavioral",
                    "category": "initiative",
                    "question": "Describe a time you took initiative on a project without being asked.",
                    "star_framework": "Situation: The opportunity\nTask: What needed doing\nAction: What you did proactively\nResult: Impact and recognition",
                    "sample_answer": "I noticed our deployment process was manual and time-consuming...",
                    "time_guidance": "Aim for 2 minutes"
                }
            ]
            questions.extend(behavioral_questions[:3])
        
        if interview_type in ["technical", "mixed"]:
            technical_questions = [
                {
                    "type": "technical",
                    "category": "system_design",
                    "question": f"Design a {random.choice(['photo sharing', 'url shortener', 'chat system', 'video streaming', 'e-commerce'])} system that handles millions of users.",
                    "framework": "1. Clarify requirements\n2. High-level architecture\n3. Data model\n4. Key components\n5. Scaling considerations\n6. Trade-offs",
                    "prep_time": "10-15 minutes",
                    "time_guidance": "Think out loud, explain your reasoning"
                },
                {
                    "type": "technical",
                    "category": "coding",
                    "question": random.choice([
                        "Implement a function to find the longest substring without repeating characters",
                        "Design an LRU cache with O(1) get and put operations",
                        "Write code to serialize and deserialize a binary tree",
                        "Implement a function to merge two sorted linked lists"
                    ]),
                    "framework": "1. Understand the problem\n2. Think of approaches\n3. Choose best approach\n4. Implement\n5. Test with edge cases",
                    "prep_time": "15-20 minutes",
                    "time_guidance": "Run through examples on paper first"
                },
                {
                    "type": "technical",
                    "category": "architecture",
                    "question": "Explain the architecture of a system you built. What decisions did you make and why?",
                    "framework": "1. System overview\n2. Key components\n3. Data flow\n4. Decisions and trade-offs\n5. What you would improve",
                    "prep_time": "5-10 minutes",
                    "time_guidance": "Pick a real project you know well"
                }
            ]
            questions.extend(technical_questions[:2])
        
        if interview_type == "cultural_fit":
            cultural_questions = [
                {
                    "type": "cultural",
                    "category": "values",
                    "question": "What values are most important to you in a workplace?",
                    "prep_tips": "Research the company's stated values and align your answer",
                    "time_guidance": "1-2 minutes"
                },
                {
                    "type": "cultural",
                    "category": "growth",
                    "question": "Where do you see yourself in 5 years?",
                    "prep_tips": "Be realistic but show ambition aligned with the role",
                    "time_guidance": "1-2 minutes"
                },
                {
                    "type": "cultural",
                    "category": "teamwork",
                    "question": "How do you prefer to receive feedback?",
                    "prep_tips": "Show openness to growth and constructive criticism",
                    "time_guidance": "1-2 minutes"
                },
                {
                    "type": "cultural",
                    "category": "motivation",
                    "question": "What gets you excited about coming to work each day?",
                    "prep_tips": "Be authentic - show genuine enthusiasm",
                    "time_guidance": "1-2 minutes"
                },
                {
                    "type": "cultural",
                    "category": "conflict",
                    "question": "How do you handle disagreements with teammates?",
                    "prep_tips": "Show you can collaborate while maintaining professionalism",
                    "time_guidance": "1-2 minutes"
                }
            ]
            questions.extend(cultural_questions)
        
        random.shuffle(questions)
        return questions[:type_config["questions_count"]]
    
    def _get_interview_tips(self, company_pattern: dict) -> List[str]:
        """Get company-specific interview tips"""
        
        tips = [
            "Speak clearly and at a moderate pace",
            "Take a moment to think before answering",
            "Use the STAR framework for behavioral questions",
            "Ask clarifying questions if needed",
            "It's okay to say 'That's a great question, let me think about that'"
        ]
        
        focus_areas = company_pattern.get("focus", [])
        if "system design" in focus_areas:
            tips.append("For system design: start with requirements, then high-level architecture")
        if "leadership principles" in focus_areas:
            tips.append("Amazon: Prepare specific stories for each leadership principle")
        if "product sense" in focus_areas:
            tips.append("Meta: Be ready to discuss product metrics and user impact")
            
        return tips
    
    def get_next_question(self, session_id: str) -> Optional[dict]:
        """Get the next question in the interview"""
        
        session = self.sessions.get(session_id)
        if not session or session["status"] != "in_progress":
            return None
        
        index = session["current_question_index"]
        if index >= len(session["questions"]):
            return None
        
        return {
            "question_number": index + 1,
            "total_questions": len(session["questions"]),
            "question": session["questions"][index],
            "progress": f"{index}/{len(session['questions'])}"
        }
    
    def submit_answer(self, session_id: str, answer: str, time_taken_seconds: int) -> dict:
        """Submit an answer to the current question"""
        
        session = self.sessions.get(session_id)
        if not session or session["status"] != "in_progress":
            return {"error": "Session not found or completed"}
        
        index = session["current_question_index"]
        current_question = session["questions"][index]
        
        session["answers"].append({
            "question": current_question["question"],
            "answer": answer,
            "time_taken_seconds": time_taken_seconds,
            "timestamp": datetime.now().isoformat()
        })
        
        session["current_question_index"] += 1
        
        has_more = session["current_question_index"] < len(session["questions"])
        
        return {
            "submitted": True,
            "question_number": index + 1,
            "has_more_questions": has_more,
            "progress": f"{session['current_question_index']}/{len(session['questions'])}",
            "next_question": self.get_next_question(session_id) if has_more else None
        }
    
    def complete_interview(self, session_id: str) -> dict:
        """Complete the interview and get feedback"""
        
        session = self.sessions.get(session_id)
        if not session:
            return {"error": "Session not found"}
        
        session["status"] = "completed"
        session["end_time"] = datetime.now().isoformat()
        
        feedback = self._generate_feedback(session)
        
        return {
            "session_id": session_id,
            "status": "completed",
            "total_questions": len(session["questions"]),
            "total_answers": len(session["answers"]),
            "duration_minutes": self._calculate_duration(session),
            "feedback": feedback,
            "summary": self._generate_summary(session)
        }
    
    def _generate_feedback(self, session: dict) -> dict:
        """Generate AI-powered feedback on the interview"""
        
        answers = session["answers"]
        questions = session["questions"]
        company_pattern = session.get("company_pattern", {})
        
        behavioral_score = 0
        technical_score = 0
        
        behavioral_answers = [a for q in questions[:3] if q["type"] == "behavioral" for a in answers if a["question"] == q["question"]]
        technical_answers = [a for q in questions if q["type"] == "technical" for a in answers if a["question"] == q["question"]]
        
        if behavioral_answers:
            avg_length = sum(len(a["answer"].split()) for a in behavioral_answers) / len(behavioral_answers)
            behavioral_score = min(10, max(1, avg_length / 30))
        
        if technical_answers:
            avg_length = sum(len(a["answer"].split()) for a in technical_answers) / len(technical_answers)
            technical_score = min(10, max(1, avg_length / 50))
        
        feedback = {
            "overall_score": round((behavioral_score + technical_score) / 2, 1),
            "behavioral_score": round(behavioral_score, 1),
            "technical_score": round(technical_score, 1),
            "strengths": self._get_strengths(answers, questions),
            "areas_for_improvement": self._get_improvements(answers, questions),
            "company_specific_tips": self._get_company_tips(company_pattern),
            "estimated_grade": self._get_grade(behavioral_score + technical_score / 2)
        }
        
        return feedback
    
    def _get_strengths(self, answers: list, questions: list) -> List[str]:
        """Identify strengths in the answers"""
        
        strengths = []
        
        for answer in answers:
            word_count = len(answer["answer"].split())
            if word_count > 100:
                strengths.append("Detailed and comprehensive answers")
            if "I" in answer["answer"] and "we" in answer["answer"]:
                strengths.append("Balanced personal and team contributions")
            if any(word in answer["answer"].lower() for word in ["result", "impact", "outcome", "improved", "increased"]):
                strengths.append("Outcome-focused responses")
        
        if len(answers) >= 3:
            strengths.append("Consistent engagement throughout")
            
        return list(set(strengths))[:3] if strengths else ["Completed all questions"]
    
    def _get_improvements(self, answers: list, questions: list) -> List[str]:
        """Identify areas for improvement"""
        
        improvements = []
        
        for answer in answers:
            word_count = len(answer["answer"].split())
            if word_count < 50:
                improvements.append("Provide more specific examples and details")
            if answer["time_taken_seconds"] < 30:
                improvements.append("Take more time to elaborate on your points")
        
        if not improvements:
            improvements = [
                "Practice with more STAR framework examples",
                "Prepare specific stories for common question themes"
            ]
            
        return list(set(improvements))[:3]
    
    def _get_company_tips(self, company_pattern: dict) -> List[str]:
        """Get company-specific tips"""
        
        focus = company_pattern.get("focus", [])
        tone = company_pattern.get("tone", "professional")
        
        tips = []
        
        if "system design" in focus:
            tips.append("Practice system design with focus on scalability")
        if "leadership principles" in focus:
            tips.append("Map your stories to Amazon's 14 leadership principles")
        if "product sense" in focus:
            tips.append("Be ready to discuss metrics and user impact")
        if "privacy" in focus:
            tips.append("Emphasize security and privacy in your examples")
            
        tips.append(f"Maintain a {tone} tone throughout")
        
        return tips
    
    def _get_grade(self, score: float) -> str:
        """Convert score to letter grade"""
        
        if score >= 9:
            return "A"
        elif score >= 8:
            return "A-"
        elif score >= 7:
            return "B+"
        elif score >= 6:
            return "B"
        elif score >= 5:
            return "B-"
        elif score >= 4:
            return "C+"
        else:
            return "C"
    
    def _calculate_duration(self, session: dict) -> int:
        """Calculate interview duration in minutes"""
        
        start = datetime.fromisoformat(session["start_time"])
        end = datetime.fromisoformat(session.get("end_time", datetime.now().isoformat()))
        return int((end - start).total_seconds() / 60)
    
    def _generate_summary(self, session: dict) -> dict:
        """Generate interview summary"""
        
        return {
            "company": session["company"],
            "role": session["role"],
            "type": session["interview_type"],
            "completed_at": session.get("end_time", datetime.now().isoformat()),
            "questions_answered": len(session["answers"]),
            "status": session["status"]
        }
    
    def get_session_status(self, session_id: str) -> Optional[dict]:
        """Get current session status"""
        
        session = self.sessions.get(session_id)
        if not session:
            return None
        
        return {
            "session_id": session_id,
            "status": session["status"],
            "current_question": session["current_question_index"] + 1,
            "total_questions": len(session["questions"]),
            "progress": f"{session['current_question_index']}/{len(session['questions'])}"
        }


voice_mock_interview = VoiceMockInterviewService()