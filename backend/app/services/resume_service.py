import io
import re
import json
from typing import Dict, List, Optional, Any
from datetime import datetime
import pdfplumber
from loguru import logger

from app.services.ollama_service import ollama_service


class ResumeService:
    """Service for parsing, optimizing, and generating resumes"""
    
    def __init__(self):
        self.skill_patterns = {
            "programming_languages": [
                "Python", "Java", "JavaScript", "TypeScript", "Go", "Rust", "C++", "C#", "Ruby", "PHP", "Swift", "Kotlin", "Scala"
            ],
            "frameworks": [
                "React", "Angular", "Vue", "Node.js", "Django", "FastAPI", "Flask", "Spring", "Rails", "Express", "Next.js", "NestJS"
            ],
            "databases": [
                "PostgreSQL", "MySQL", "MongoDB", "Redis", "Elasticsearch", "Cassandra", "SQLite", "DynamoDB", "SQL Server"
            ],
            "cloud": [
                "AWS", "GCP", "Azure", "Docker", "Kubernetes", "Terraform", "CloudFormation", "Serverless", "Lambda"
            ],
            "tools": [
                "Git", "Jenkins", "CircleCI", "GitHub Actions", "Jira", "Confluence", "Slack", "Postman", "Insomnia"
            ]
        }
    
    async def parse_resume(self, file_content: bytes, filename: str) -> Dict[str, Any]:
        """Parse resume from PDF or other format"""
        
        extracted_data = {
            "name": None,
            "email": None,
            "phone": None,
            "linkedin": None,
            "github": None,
            "skills": [],
            "experience": [],
            "education": [],
            "summary": None,
            "raw_text": ""
        }
        
        try:
            if filename.lower().endswith(".pdf"):
                extracted_data = await self.parse_pdf(file_content)
            elif filename.lower().endswith(".docx"):
                extracted_data = await self.parse_docx(file_content)
            else:
                logger.warning(f"Unsupported file format: {filename}")
                
        except Exception as e:
            logger.error(f"Resume parsing error: {e}")
        
        return extracted_data
    
    async def parse_pdf(self, file_content: bytes) -> Dict[str, Any]:
        """Parse PDF resume using pdfplumber"""
        
        extracted = {
            "name": None,
            "email": None,
            "phone": None,
            "linkedin": None,
            "github": None,
            "skills": [],
            "experience": [],
            "education": [],
            "summary": None,
            "raw_text": ""
        }
        
        try:
            with pdfplumber.open(io.BytesIO(file_content)) as pdf:
                text = ""
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
                
                extracted["raw_text"] = text
                
                # Extract contact info
                extracted["email"] = self.extract_email(text)
                extracted["phone"] = self.extract_phone(text)
                extracted["linkedin"] = self.extract_linkedin(text)
                extracted["github"] = self.extract_github(text)
                extracted["name"] = self.extract_name(text)
                
                # Extract skills
                extracted["skills"] = self.extract_skills(text)
                
                # Extract experience
                extracted["experience"] = self.extract_experience(text)
                
                # Extract education
                extracted["education"] = self.extract_education(text)
                
                # Extract summary
                extracted["summary"] = self.extract_summary(text)
                
        except Exception as e:
            logger.error(f"PDF parsing error: {e}")
        
        return extracted
    
    async def parse_docx(self, file_content: bytes) -> Dict[str, Any]:
        """Parse DOCX resume"""
        
        try:
            from docx import Document
            
            doc = Document(io.BytesIO(file_content))
            text = "\n".join([p.text for p in doc.paragraphs])
            
            extracted = {
                "raw_text": text,
                "email": self.extract_email(text),
                "phone": self.extract_phone(text),
                "linkedin": self.extract_linkedin(text),
                "github": self.extract_github(text),
                "name": self.extract_name(text),
                "skills": self.extract_skills(text),
                "experience": self.extract_experience(text),
                "education": self.extract_education(text),
                "summary": self.extract_summary(text)
            }
            
            return extracted
            
        except Exception as e:
            logger.error(f"DOCX parsing error: {e}")
            return {}
    
    def extract_email(self, text: str) -> Optional[str]:
        """Extract email address from text"""
        pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        match = re.search(pattern, text)
        return match.group(0) if match else None
    
    def extract_phone(self, text: str) -> Optional[str]:
        """Extract phone number from text"""
        patterns = [
            r'\b\+91[6-9]\d{9}\b',  # Indian format
            r'\b\d{10}\b',
            r'\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b',
            r'\(\d{3}\)\s*\d{3}[-.\s]?\d{4}'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(0)
        return None
    
    def extract_linkedin(self, text: str) -> Optional[str]:
        """Extract LinkedIn URL"""
        pattern = r'linkedin\.com/in/[a-zA-Z0-9-]+'
        match = re.search(pattern, text, re.IGNORECASE)
        return f"https://{match.group(0)}" if match else None
    
    def extract_github(self, text: str) -> Optional[str]:
        """Extract GitHub URL"""
        pattern = r'github\.com/[a-zA-Z0-9-]+'
        match = re.search(pattern, text, re.IGNORECASE)
        return f"https://{match.group(0)}" if match else None
    
    def extract_name(self, text: str) -> Optional[str]:
        """Extract name (usually first line or after common patterns)"""
        lines = text.strip().split("\n")
        
        # First non-empty line is often the name
        for line in lines[:5]:
            line = line.strip()
            if line and len(line) < 50:
                # Check if it looks like a name (no numbers, reasonable length)
                if not re.search(r'\d', line) and not "@" in line:
                    return line
        
        return None
    
    def extract_skills(self, text: str) -> List[str]:
        """Extract technical skills from text"""
        text_lower = text.lower()
        found_skills = []
        
        for category, skills in self.skill_patterns.items():
            for skill in skills:
                if skill.lower() in text_lower:
                    if skill not in found_skills:
                        found_skills.append(skill)
        
        return found_skills
    
    def extract_experience(self, text: str) -> List[Dict]:
        """Extract work experience"""
        experience = []
        
        # Look for common patterns
        patterns = [
            r'(?:Work Experience|Employment|Experience)[:\n](.*?)(?:Education|Skills|$)',
            r'(?:Company|Organization)[:\s]*([^\n]+)',
            r'(?:Position|Role|Job Title)[:\s]*([^\n]+)',
            r'(\d{4}\s*[-–]\s*(?:\d{4}|Present))'
        ]
        
        # This is a simplified version - in production would use more sophisticated parsing
        # or LLM-based extraction
        
        return experience
    
    def extract_education(self, text: str) -> List[Dict]:
        """Extract education details"""
        education = []
        
        # Look for degree patterns
        degrees = ["B.Tech", "B.E", "M.Tech", "M.S", "B.Sc", "M.Sc", "Ph.D", "MBA"]
        
        for line in text.split("\n"):
            for degree in degrees:
                if degree in line:
                    education.append({
                        "degree": degree,
                        "details": line.strip()
                    })
        
        return education
    
    def extract_summary(self, text: str) -> Optional[str]:
        """Extract professional summary"""
        
        # Look for summary/objective section
        patterns = [
            r'(?:Summary|Objective|Profile)[:\n](.*?)(?:Experience|Skills|Education|$)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if match:
                summary = match.group(1).strip()[:200]
                return summary
        
        return None
    
    async def optimize_for_ats(
        self,
        resume_data: Dict,
        job_description: str,
        job_title: str
    ) -> Dict[str, Any]:
        """Optimize resume for ATS using job description"""
        
        # Extract keywords from job description
        keywords = await ollama_service.extract_keywords(job_description)
        
        # Calculate match score
        resume_skills = set(s.lower() for s in resume_data.get("skills", []))
        job_skills = set(s.lower() for s in keywords)
        
        matching_skills = resume_skills.intersection(job_skills)
        match_score = len(matching_skills) / len(job_skills) * 100 if job_skills else 0
        
        # Tailor resume content
        tailored_content = await ollama_service.tailor_resume(
            original_resume=resume_data.get("raw_text", ""),
            keywords=keywords,
            job_title=job_title
        )
        
        return {
            "match_score": round(match_score, 2),
            "matching_keywords": list(matching_skills),
            "missing_keywords": list(job_skills - resume_skills),
            "tailored_content": tailored_content,
            "tips": self.generate_optimization_tips(match_score, keywords, resume_skills)
        }
    
    def generate_optimization_tips(
        self,
        match_score: float,
        keywords: List[str],
        resume_skills: set
    ) -> List[str]:
        """Generate tips for resume optimization"""
        
        tips = []
        
        if match_score < 50:
            tips.append("Add more keywords from the job description to your skills section")
        
        if match_score < 70:
            tips.append("Consider rewording your experience to include more job-specific terminology")
        
        # Format tips
        tips.extend([
            "Use standard section headings (Experience, Education, Skills)",
            "Avoid tables and columns as ATS may not parse them correctly",
            "Use standard font sizes (10-12pt) and standard fonts (Arial, Calibri)",
            "Submit in .pdf format for best ATS compatibility"
        ])
        
        return tips
    
    async def generate_cover_letter(
        self,
        resume_data: Dict,
        job_data: Dict
    ) -> str:
        """Generate cover letter for job application"""
        
        return await ollama_service.generate_cover_letter(
            resume=resume_data.get("raw_text", ""),
            job_description=job_data.get("description", ""),
            company_name=job_data.get("company", "")
        )
    
    def validate_ats_format(self, text: str) -> Dict[str, Any]:
        """Validate resume format for ATS compatibility"""
        
        issues = []
        
        # Check for problematic elements
        if text.count("\t") > 5:
            issues.append("Too many tabs - use spaces instead")
        
        if len(text) > 50000:
            issues.append("Resume too long - keep under 2 pages")
        
        if "http" in text.lower() and text.count("http") > 5:
            issues.append("Too many links - include only relevant URLs")
        
        # Check for contact info
        if "@" not in text:
            issues.append("No email address found")
        
        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "score": max(0, 100 - len(issues) * 15)
        }


# Singleton instance
resume_service = ResumeService()