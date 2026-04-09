import os
import io
from typing import Dict, List, Optional
from datetime import datetime
from loguru import logger


ATS_TEMPLATE = """<!DOCTYPE html>
<html lang="{{LANG}}">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{{NAME}} — CV</title>
<style>
  @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=DM+Sans:wght@400;500;700&display=swap');
  
  * { margin: 0; padding: 0; box-sizing: border-box; }
  html { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
  
  body {
    font-family: 'DM Sans', sans-serif;
    font-size: 11px;
    line-height: 1.5;
    color: #1a1a2e;
    background: #ffffff;
    padding: 0;
    margin: 0;
  }
  
  .page {
    width: 100%;
    max-width: {{PAGE_WIDTH}};
    margin: 0 auto;
    padding: 2px 0;
  }
  
  .header { margin-bottom: 20px; }
  .header h1 {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 28px;
    font-weight: 700;
    color: #1a1a2e;
    letter-spacing: -0.02em;
    margin-bottom: 6px;
    line-height: 1.1;
  }
  
  .header-gradient {
    height: 2px;
    background: linear-gradient(to right, hsl(187, 74%, 32%), hsl(270, 70%, 45%));
    border-radius: 1px;
    margin-bottom: 10px;
  }
  
  .contact-row {
    display: flex;
    flex-wrap: wrap;
    gap: 8px 14px;
    font-family: 'DM Sans', sans-serif;
    font-size: 10.5px;
    line-height: 1.4;
    color: #555;
  }
  
  .contact-row a { color: #555; text-decoration: none; }
  .contact-row .separator { color: #ccc; }
  
  .section { margin-bottom: 18px; }
  
  .section-title {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 12px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    color: hsl(187, 74%, 32%);
    border-bottom: 1.5px solid #e2e2e2;
    padding-bottom: 4px;
    margin-bottom: 10px;
    line-height: 1.2;
  }
  
  .summary-text {
    font-size: 11px;
    line-height: 1.7;
    color: #2f2f2f;
  }
  
  a { white-space: nowrap; }
  
  .competencies-grid {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
  }
  
  .competency-tag {
    font-family: 'DM Sans', sans-serif;
    font-size: 10px;
    font-weight: 500;
    color: hsl(187, 74%, 28%);
    background: hsl(187, 40%, 95%);
    padding: 4px 10px;
    border-radius: 3px;
    border: 1px solid hsl(187, 40%, 88%);
  }
  
  .job { margin-bottom: 14px; }
  
  .job-header {
    display: flex;
    justify-content: space-between;
    align-items: baseline;
    gap: 12px;
    margin-bottom: 4px;
  }
  
  .job-company {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 12.5px;
    font-weight: 600;
    color: hsl(270, 70%, 45%);
  }
  
  .job-period {
    font-size: 10.5px;
    color: #777;
    white-space: nowrap;
  }
  
  .job-role {
    font-size: 11px;
    font-weight: 600;
    color: #333;
    margin-bottom: 6px;
  }
  
  .job-location { font-size: 10px; color: #888; }
  
  .job ul {
    padding-left: 18px;
    margin-top: 6px;
  }
  
  .job li {
    font-size: 10.5px;
    line-height: 1.6;
    color: #333;
    margin-bottom: 4px;
  }
  
  .job li strong { font-weight: 600; }
  
  .project { margin-bottom: 12px; }
  
  .project-title {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 11.5px;
    font-weight: 600;
    color: hsl(270, 70%, 45%);
  }
  
  .project-desc {
    font-size: 10.5px;
    color: #444;
    margin-top: 3px;
    line-height: 1.55;
  }
  
  .project-tech {
    font-size: 9.5px;
    color: #888;
    margin-top: 3px;
  }
  
  .edu-item { margin-bottom: 8px; }
  
  .edu-header {
    display: flex;
    justify-content: space-between;
    align-items: baseline;
    gap: 12px;
  }
  
  .edu-title {
    font-weight: 600;
    font-size: 11px;
    color: #333;
  }
  
  .edu-org { color: hsl(270, 70%, 45%); font-weight: 500; }
  .edu-year { font-size: 10px; color: #777; white-space: nowrap; }
  .edu-desc { font-size: 10px; color: #666; margin-top: 2px; line-height: 1.5; }
  
  .cert-item {
    display: flex;
    justify-content: space-between;
    align-items: baseline;
    gap: 12px;
    margin-bottom: 6px;
  }
  
  .cert-title { font-size: 10.5px; font-weight: 500; color: #333; }
  .cert-org { color: hsl(270, 70%, 45%); }
  .cert-year { font-size: 10px; color: #777; white-space: nowrap; }
  
  .skills-grid {
    display: flex;
    flex-wrap: wrap;
    gap: 6px 14px;
  }
  
  .skill-item { font-size: 10.5px; color: #444; }
  .skill-category { font-weight: 600; color: #333; font-size: 10.5px; }
  
  @media print {
    body { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
    .page { padding: 0; }
  }
  
  .avoid-break, .job, .project, .edu-item, .cert-item {
    break-inside: avoid;
    page-break-inside: avoid;
  }
</style>
</head>
<body>
<div class="page">
  <div class="header avoid-break">
    <h1>{{NAME}}</h1>
    <div class="header-gradient"></div>
    <div class="contact-row">
      <span>{{EMAIL}}</span>
      <span class="separator">|</span>
      <span>{{PHONE}}</span>
      <span class="separator">|</span>
      <a href="{{LINKEDIN_URL}}">{{LINKEDIN_DISPLAY}}</a>
      <span class="separator">|</span>
      <a href="{{PORTFOLIO_URL}}">{{PORTFOLIO_DISPLAY}}</a>
      <span class="separator">|</span>
      <span>{{LOCATION}}</span>
    </div>
  </div>
  
  <div class="section avoid-break">
    <div class="section-title">{{SECTION_SUMMARY}}</div>
    <div class="summary-text">{{SUMMARY_TEXT}}</div>
  </div>
  
  <div class="section">
    <div class="section-title">{{SECTION_COMPETENCIES}}</div>
    <div class="competencies-grid">
      {{COMPETENCIES}}
    </div>
  </div>
  
  <div class="section">
    <div class="section-title">{{SECTION_EXPERIENCE}}</div>
    {{EXPERIENCE}}
  </div>
  
  <div class="section avoid-break">
    <div class="section-title">{{SECTION_PROJECTS}}</div>
    {{PROJECTS}}
  </div>
  
  <div class="section avoid-break">
    <div class="section-title">{{SECTION_EDUCATION}}</div>
    {{EDUCATION}}
  </div>
  
  <div class="section avoid-break">
    <div class="section-title">{{SECTION_CERTIFICATIONS}}</div>
    {{CERTIFICATIONS}}
  </div>
  
  <div class="section avoid-break">
    <div class="section-title">{{SECTION_SKILLS}}</div>
    <div class="skills-grid">
      {{SKILLS}}
    </div>
  </div>
</div>
</body>
</html>"""


class PDFGeneratorService:
    def __init__(self):
        self.template_dir = os.path.join(os.path.dirname(__file__), "..", "..", "templates")
        self.output_dir = os.path.join(os.path.dirname(__file__), "..", "..", "output")
        os.makedirs(self.output_dir, exist_ok=True)

    def _format_job_experience(self, experience: List[Dict]) -> str:
        if not experience:
            return "<p style='color:#888'>No experience listed</p>"
        
        html = ""
        for exp in experience:
            period = exp.get("period", "")
            company = exp.get("company", "")
            role = exp.get("role", "")
            location = exp.get("location", "")
            bullets = exp.get("bullets", [])
            
            bullets_html = "".join([f"<li>{b}</li>" for b in bullets])
            
            html += f"""
    <div class="job">
        <div class="job-header">
            <span class="job-company">{company}</span>
            <span class="job-period">{period}</span>
        </div>
        <div class="job-role">{role}</div>
        <div class="job-location">{location}</div>
        <ul>{bullets_html}</ul>
    </div>"""
        
        return html

    def _format_projects(self, projects: List[Dict]) -> str:
        if not projects:
            return ""
        
        html = ""
        for proj in projects:
            title = proj.get("title", "")
            description = proj.get("description", "")
            tech = proj.get("tech", "")
            
            html += f"""
    <div class="project">
        <span class="project-title">{title}</span>
        <div class="project-desc">{description}</div>
        <div class="project-tech">{tech}</div>
    </div>"""
        
        return html

    def _format_education(self, education: List[Dict]) -> str:
        if not education:
            return "<p style='color:#888'>No education listed</p>"
        
        html = ""
        for edu in education:
            year = edu.get("year", "")
            title = edu.get("title", "")
            org = edu.get("organization", "")
            desc = edu.get("description", "")
            
            html += f"""
    <div class="edu-item">
        <div class="edu-header">
            <span class="edu-title">{title} — <span class="edu-org">{org}</span></span>
            <span class="edu-year">{year}</span>
        </div>
        <div class="edu-desc">{desc}</div>
    </div>"""
        
        return html

    def _format_certifications(self, certifications: List[Dict]) -> str:
        if not certifications:
            return ""
        
        html = ""
        for cert in certifications:
            title = cert.get("title", "")
            org = cert.get("organization", "")
            year = cert.get("year", "")
            
            html += f"""
    <div class="cert-item">
        <span class="cert-title">{title} — <span class="cert-org">{org}</span></span>
        <span class="cert-year">{year}</span>
    </div>"""
        
        return html

    def _format_skills(self, skills: List[str]) -> str:
        html_parts = []
        for skill in skills[:12]:
            html_parts.append(f'<span class="competency-tag">{skill}</span>')
        return "\n    ".join(html_parts)

    def _format_competencies(self, skills: List[str]) -> str:
        html_parts = []
        for skill in skills[:15]:
            html_parts.append(f'<span class="competency-tag">{skill}</span>')
        return "\n    ".join(html_parts)

    async def generate_resume_pdf(
        self,
        user_data: Dict,
        job_data: Optional[Dict] = None,
        keywords: Optional[List[str]] = None
    ) -> bytes:
        template_data = self.prepare_template_data(user_data, job_data, keywords)
        html = self.render_html_template(template_data)
        
        try:
            from weasyprint import HTML
            pdf_bytes = HTML(string=html).write_pdf()
            return pdf_bytes
        except ImportError:
            logger.warning("weasyprint not installed, using fallback")
            return self._html_to_pdf_simple(html)

    def _html_to_pdf_simple(self, html: str) -> bytes:
        return b"%PDF-1.4\n(Fallback - install weasyprint for proper PDF)"

    def prepare_template_data(
        self,
        user_data: Dict,
        job_data: Optional[Dict],
        keywords: Optional[List[str]]
    ) -> Dict:
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
        
        experience = user_data.get("experience", [])
        projects = user_data.get("projects", [])
        education = user_data.get("education", [])
        certifications = user_data.get("certifications", [])
        
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
            "COMPETENCIES": self._format_competencies(skills),
            "EXPERIENCE": self._format_job_experience(experience),
            "PROJECTS": self._format_projects(projects),
            "EDUCATION": self._format_education(education),
            "CERTIFICATIONS": self._format_certifications(certifications),
            "SKILLS": self._format_skills(skills),
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

    def render_html_template(self, data: Dict) -> str:
        html = ATS_TEMPLATE
        
        for key, value in data.items():
            placeholder = f"{{{{{key}}}}}"
            html = html.replace(placeholder, str(value))
        
        return html

    async def generate_tailored_resume(
        self,
        user_data: Dict,
        job_description: str,
        keywords: List[str]
    ) -> bytes:
        tailored_data = user_data.copy()
        tailored_data["summary"] = self._generate_summary(user_data, job_description)
        
        current_skills = tailored_data.get("skills", [])
        for kw in keywords:
            if kw.lower() not in [s.lower() for s in current_skills]:
                current_skills.append(kw)
        tailored_data["skills"] = current_skills
        
        return await self.generate_resume_pdf(tailored_data, None, keywords)

    def _generate_summary(self, user_data: Dict, job_description: str) -> str:
        role = user_data.get("target_role", "Professional")
        experience = user_data.get("experience_years", 0)
        skills = user_data.get("skills", [])[:3]
        
        return f"{role} with {experience}+ years of experience in {', '.join(skills)}. Proven track record of delivering high-quality solutions."

    async def save_resume_pdf(
        self,
        user_id: str,
        user_data: Dict,
        job_data: Optional[Dict] = None,
        keywords: Optional[List[str]] = None
    ) -> str:
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