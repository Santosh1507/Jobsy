import asyncio
import random
import json
from typing import Dict, List, Optional
from datetime import datetime
from loguru import logger


class CoverLetterGenerator:
    
    TEMPLATES = {
        "standard": {
            "structure": [
                "Dear [Hiring Manager Name],",
                "",
                "I am writing to express my strong interest in the {role} position at {company}.",
                "With my {years} years of experience in {skills} and a proven track record of {achievement},",
                "I am confident that I would be a valuable addition to your team.",
                "",
                "In my current role at {current_company}, I have:",
                "- {achievement_1}",
                "- {achievement_2}",
                "- {achievement_3}",
                "",
                "What excites me about {company} is {company_interest}.",
                "I am particularly drawn to this opportunity because {specific_interest}.",
                "",
                "I would welcome the opportunity to discuss how my background aligns with your needs.",
                "Thank you for considering my application.",
                "",
                "Best regards,",
                "{name}"
            ]
        },
        "technical": {
            "structure": [
                "Dear Hiring Manager,",
                "",
                "I am excited to apply for the {role} position at {company}.",
                "As a {skills} developer with {years} years of experience,",
                "I have developed expertise in {technical_skills}.",
                "",
                "At {current_company}, I:",
                "- Built {project_1} using {tech_1}",
                "- Optimized {system} resulting in {metric} improvement",
                "- Led a team of {team_size} engineers on {project_2}",
                "",
                "Your company's focus on {company_focus} aligns with my professional interests.",
                "I am particularly interested in {specific_project} and believe my skills would contribute to your team's success.",
                "",
                "I look forward to discussing this opportunity with you.",
                "Best regards,",
                "{name}"
            ]
        },
        "career_change": {
            "structure": [
                "Dear [Hiring Manager Name],",
                "",
                "I am writing to apply for the {role} position at {company}.",
                "Although my background is in {previous_field}, I am eager to transition into {new_field}.",
                "",
                "My transferable skills include:",
                "- {skill_1} - developed through {experience_1}",
                "- {skill_2} - demonstrated in {experience_2}",
                "- {skill_3} - refined via {experience_3}",
                "",
                "I have been actively preparing for this transition by {preparation}.",
                "Your company's {company_value} strongly resonates with my values.",
                "",
                "I am enthusiastic about the possibility of bringing my unique perspective to {company}.",
                "Thank you for your time and consideration.",
                "",
                "Sincerely,",
                "{name}"
            ]
        }
    }
    
    def __init__(self):
        self.templates = self.TEMPLATES
    
    async def generate(
        self,
        template_type: str = "standard",
        company: str = "",
        role: str = "",
        user_data: Dict = {},
        job_data: Dict = {}
    ) -> str:
        """Generate a cover letter based on template and data"""
        
        template = self.templates.get(template_type, self.templates["standard"])
        structure = template["structure"]
        
        filled_letter = []
        
        for line in structure:
            line = self._fill_placeholder(line, {
                "role": role,
                "company": company,
                "name": user_data.get("name", "Your Name"),
                "years": user_data.get("years_experience", "5"),
                "skills": ", ".join(user_data.get("skills", [])[:3]) if user_data.get("skills") else "software development",
                "achievement": user_data.get("key_achievement", "delivering impactful projects"),
                "current_company": user_data.get("current_company", "my current organization"),
                "achievement_1": user_data.get("achievement_1", "Led cross-functional teams to deliver major initiatives"),
                "achievement_2": user_data.get("achievement_2", "Improved system performance by 40%"),
                "achievement_3": user_data.get("achievement_3", "Mentored junior developers on best practices"),
                "company_interest": job_data.get("company_interest", "innovative technology solutions"),
                "specific_interest": job_data.get("specific_interest", "the opportunity to work on cutting-edge projects"),
                "technical_skills": ", ".join(user_data.get("technical_skills", user_data.get("skills", []))[:4]) if user_data.get("skills") else "Python, JavaScript, React, AWS",
                "project_1": job_data.get("project", "scalable microservices architecture"),
                "tech_1": job_data.get("tech_stack", "Python and Kubernetes"),
                "system": job_data.get("system", "database queries"),
                "metric": job_data.get("metric", "50%"),
                "team_size": user_data.get("team_size", "4"),
                "project_2": job_data.get("project_2", "API modernization initiative"),
                "company_focus": job_data.get("company_focus", "building great products"),
                "specific_project": job_data.get("specific_project", "the engineering team's technical challenges"),
                "previous_field": user_data.get("previous_field", "marketing"),
                "new_field": job_data.get("new_field", "software engineering"),
                "skill_1": user_data.get("transferable_skill_1", "communication"),
                "experience_1": user_data.get("experience_1", "managing client relationships"),
                "skill_2": user_data.get("transferable_skill_2", "project management"),
                "experience_2": user_data.get("experience_2", "coordinating cross-functional teams"),
                "skill_3": user_data.get("transferable_skill_3", "analytical thinking"),
                "experience_3": user_data.get("experience_3", "data-driven decision making"),
                "preparation": user_data.get("preparation", "completing relevant certifications and personal projects"),
                "company_value": job_data.get("company_value", "mission-driven work")
            })
            filled_letter.append(line)
        
        return "\n".join(filled_letter)
    
    def _fill_placeholder(self, text: str, values: Dict) -> str:
        for key, value in values.items():
            text = text.replace(f"{{{key}}}", str(value))
        return text
    
    def generate_custom(
        self,
        user_data: Dict,
        job_data: Dict,
        custom_sections: List[str] = []
    ) -> str:
        """Generate custom cover letter with user-defined sections"""
        
        sections = []
        
        if "intro" in custom_sections:
            sections.append(f"Dear {job_data.get('hiring_manager', 'Hiring Manager')},\n")
            sections.append(f"I am excited to apply for the {job_data.get('role', 'position')} at {job_data.get('company', 'your company')}.")
        
        if "body" in custom_sections:
            for achievement in user_data.get("achievements", []):
                sections.append(f"- {achievement}")
        
        if "closing" in custom_sections:
            sections.append("\nThank you for your consideration.\n")
            sections.append(f"Best regards,\n{user_data.get('name', 'Applicant')}")
        
        return "\n".join(sections)


cover_letter_generator = CoverLetterGenerator()