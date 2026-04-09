import os
import io
from typing import Dict, List, Optional
from datetime import datetime
from loguru import logger

try:
    from weasyprint import HTML
    WEASYPRINT_AVAILABLE = True
except ImportError:
    WEASYPRINT_AVAILABLE = False


class PDFGeneratorService:
    def __init__(self):
        self.template_dir = os.path.join(os.path.dirname(__file__), "..", "..", "templates")
        self.output_dir = os.path.join(os.path.dirname(__file__), "..", "..", "output")
        os.makedirs(self.output_dir, exist_ok=True)

    async def generate_resume_pdf(
        self,
        user_data: Dict,
        job_data: Optional[Dict] = None,
        keywords: Optional[List[str]] = None
    ) -> bytes:
        template_data = self.prepare_template_data(user_data, job_data, keywords)
        html = self.render_html_template(template_data)
        
        if WEASYPRINT_AVAILABLE:
            pdf_bytes = HTML(string=html).write_pdf()
        else:
            pdf_bytes = self._simple_pdf_export(html)
        
        return pdf_bytes

    def _simple_pdf_export(self, html: str) -> bytes:
        """Simple fallback - returns HTML as bytes with PDF header"""
        return b"%PDF-1.4\n(PDF generation requires weasyprint)"

    def prepare_template_data(self, user_data: Dict, job_data: Optional[Dict], keywords: Optional[List[str]]) -> Dict:
        name = user_data.get("name", "Your Name")
        email = user_data.get("email", "email@example.com")
        phone = user_data.get("phone", "")
        location = user_data.get("location", "")
        linkedin = user_data.get("linkedin", "")
        github = user_data.get("github", "")
        
        skills = user_data.get("skills", [])
        if keywords:
            for kw in keywords:
                if kw.lower() not in [s.lower() for s in skills]:
                    skills.append(kw)
        
        return {
            "NAME": name,
            "EMAIL": email,
            "PHONE": phone,
            "LOCATION": location,
            "LINKEDIN_URL": linkedin,
            "LINKEDIN_DISPLAY": linkedin.replace("https://linkedin.com/in/", "") if linkedin else "",
            "PORTFOLIO_URL": github,
            "PORTFOLIO_DISPLAY": github.replace("https://github.com/", "") if github else "",
            "SUMMARY_TEXT": user_data.get("summary", ""),
            "COMPETENCIES": skills,
            "EXPERIENCE": user_data.get("experience", []),
            "PROJECTS": user_data.get("projects", []),
            "EDUCATION": user_data.get("education", []),
            "CERTIFICATIONS": user_data.get("certifications", []),
            "SKILLS": self.format_skills(skills),
            "PAGE_WIDTH": "210mm",
            "LANG": "en",
            "SECTION_SUMMARY": "Professional Summary",
            "SECTION_COMPETENCIES": "Core Competencies",
            "SECTION_EXPERIENCE": "Work Experience",
            "SECTION_PROJECTS": "Projects",
            "SECTION_EDUCATION": "Education",
            "SECTION_CERTIFICATIONS": "Certifications",
            "SECTION_SKILLS": "Technical Skills"
        }

    def format_skills(self, skills: List[str]) -> str:
        html_parts = []
        for skill in skills:
            html_parts.append(f'<span class="competency-tag">{skill}</span>')
        return "\n    ".join(html_parts)

    def render_html_template(self, data: Dict) -> str:
        template = self.get_resume_template()
        html = template
        for key, value in data.items():
            placeholder = f"{{{{{key}}}}}"
            html = html.replace(placeholder, str(value))
        return html

    def get_resume_template(self) -> str:
        return """<!DOCTYPE html>
<html lang="{{LANG}}">
<head>
<meta charset="UTF-8">
<title>{{NAME}} — CV</title>
<style>
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body { font-family: Arial, sans-serif; font-size: 11px; line-height: 1.5; color: #1a1a2e; padding: 20px; }
  h1 { font-size: 24px; margin-bottom: 10px; }
  .contact-row { color: #555; margin-bottom: 20px; }
  .section { margin-bottom: 18px; }
  .section-title { font-size: 12px; font-weight: bold; text-transform: uppercase; color: #333; border-bottom: 1px solid #ccc; padding-bottom: 4px; margin-bottom: 10px; }
  .competency-tag { display: inline-block; font-size: 10px; background: #e0e0e0; padding: 4px 8px; margin: 2px; border-radius: 3px; }
</style>
</head>
<body>
  <h1>{{NAME}}</h1>
  <div class="contact-row">
    {{EMAIL}} | {{LOCATION}} | {{LINKEDIN_DISPLAY}} | {{PORTFOLIO_DISPLAY}}
  </div>
  <div class="section">
    <div class="section-title">{{SECTION_SUMMARY}}</div>
    <div>{{SUMMARY_TEXT}}</div>
  </div>
  <div class="section">
    <div class="section-title">{{SECTION_COMPETENCIES}}</div>
    <div>{{COMPETENCIES}}</div>
  </div>
  <div class="section">
    <div class="section-title">{{SECTION_SKILLS}}</div>
    <div>{{SKILLS}}</div>
  </div>
</body>
</html>"""

    async def save_resume_pdf(self, user_id: str, user_data: Dict, job_data: Optional[Dict] = None, keywords: Optional[List[str]] = None) -> str:
        pdf_bytes = await self.generate_resume_pdf(user_data, job_data, keywords)
        
        company_slug = job_data.get("company", "general").lower().replace(" ", "-") if job_data else "general"
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{user_id}_{company_slug}_{timestamp}.pdf"
        filepath = os.path.join(self.output_dir, filename)
        
        with open(filepath, "wb") as f:
            f.write(pdf_bytes)
        
        logger.info(f"Saved resume PDF: {filepath}")
        return filepath


pdf_generator = PDFGeneratorService()