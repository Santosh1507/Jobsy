import asyncio
import os
import io
from typing import Dict, List, Optional
from datetime import datetime
from playwright.async_api import async_playwright
from loguru import logger


class PDFGeneratorService:
    """Generate ATS-optimized PDF resumes using Playwright + HTML template"""

    def __init__(self):
        self.template_dir = os.path.join(os.path.dirname(__file__), "..", "..", "templates")
        self.output_dir = os.path.join(os.path.dirname(__file__), "..", "..", "output")
        
        # Ensure output directory exists
        os.makedirs(self.output_dir, exist_ok=True)

    async def generate_resume_pdf(
        self,
        user_data: Dict,
        job_data: Optional[Dict] = None,
        keywords: Optional[List[str]] = None
    ) -> bytes:
        """Generate ATS-optimized PDF resume"""
        
        # Prepare template data
        template_data = self.prepare_template_data(user_data, job_data, keywords)
        
        # Generate HTML from template
        html = self.render_html_template(template_data)
        
        # Convert to PDF using Playwright
        pdf_bytes = await self.html_to_pdf(html)
        
        return pdf_bytes

    def prepare_template_data(
        self,
        user_data: Dict,
        job_data: Optional[Dict],
        keywords: Optional[List[str]]
    ) -> Dict:
        """Prepare data for resume template"""
        
        # Extract from user_data
        name = user_data.get("name", "Your Name")
        email = user_data.get("email", "email@example.com")
        phone = user_data.get("phone", "")
        location = user_data.get("location", "")
        linkedin = user_data.get("linkedin", "")
        github = user_data.get("github", "")
        
        # Build contact row
        contact_parts = [email]
        if phone:
            contact_parts.append(phone)
        if linkedin:
            contact_parts.append(linkedin)
        
        # Skills from user profile or keywords
        skills = user_data.get("skills", [])
        if keywords:
            # Add missing keywords to skills
            for kw in keywords:
                if kw.lower() not in [s.lower() for s in skills]:
                    skills.append(kw)
        
        # Experience
        experience = user_data.get("experience", [])
        
        # Education
        education = user_data.get("education", [])
        
        # Summary - customize based on job if provided
        summary = user_data.get("summary", "")
        if job_data and keywords:
            # Generate job-specific summary
            summary = self.generate_tailored_summary(
                user_data, job_data, keywords
            )
        
        # Projects
        projects = user_data.get("projects", [])
        
        # Certifications
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
            "SUMMARY_TEXT": summary,
            "COMPETENCIES": skills,
            "EXPERIENCE": experience,
            "PROJECTS": projects,
            "EDUCATION": education,
            "CERTIFICATIONS": certifications,
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

    def generate_tailored_summary(
        self,
        user_data: Dict,
        job_data: Dict,
        keywords: List[str]
    ) -> str:
        """Generate job-specific professional summary"""
        
        role = job_data.get("title", user_data.get("target_role", "Professional"))
        experience_years = user_data.get("experience_years", 0)
        
        # Get top matching skills
        top_skills = keywords[:5] if keywords else user_data.get("skills", [])[:5]
        
        summary = f"{role} with {experience_years}+ years of experience in {', '.join(top_skills)}. "
        summary += "Proven track record of delivering high-quality solutions. "
        summary += "Looking to bring my expertise to a dynamic team."
        
        return summary

    def format_skills(self, skills: List[str]) -> str:
        """Format skills as HTML for template"""
        
        html_parts = []
        for skill in skills:
            html_parts.append(f'<span class="competency-tag">{skill}</span>')
        
        return "\n    ".join(html_parts)

    def render_html_template(self, data: Dict) -> str:
        """Render HTML from template with data"""
        
        # Use career-ops template
        template = self.get_resume_template()
        
        # Replace placeholders
        html = template
        for key, value in data.items():
            placeholder = f"{{{{{key}}}}}"
            html = html.replace(placeholder, str(value))
        
        # Handle list items (experience, projects, etc.)
        html = self.render_experience_section(html, data.get("EXPERIENCE", []))
        html = self.render_projects_section(html, data.get("PROJECTS", []))
        html = self.render_education_section(html, data.get("EDUCATION", []))
        html = self.render_certifications_section(html, data.get("CERTIFICATIONS", []))
        
        return html

    def render_experience_section(self, html: str, experience: List[Dict]) -> str:
        """Render work experience section"""
        
        if not experience:
            return html.replace("{{EXPERIENCE}}", "<p style='color:#888'>No experience listed</p>")
        
        experience_html = ""
        for exp in experience:
            period = exp.get("period", "")
            company = exp.get("company", "")
            role = exp.get("role", "")
            location = exp.get("location", "")
            bullets = exp.get("bullets", [])
            
            bullets_html = "".join([f"<li>{b}</li>" for b in bullets])
            
            experience_html += f"""
    <div class="job">
        <div class="job-header">
            <span class="job-company">{company}</span>
            <span class="job-period">{period}</span>
        </div>
        <div class="job-role">{role}</div>
        <div class="job-location">{location}</div>
        <ul>{bullets_html}</ul>
    </div>"""
        
        return html.replace("{{EXPERIENCE}}", experience_html)

    def render_projects_section(self, html: str, projects: List[Dict]) -> str:
        """Render projects section"""
        
        if not projects:
            return html.replace("{{PROJECTS}}", "")
        
        projects_html = ""
        for proj in projects:
            title = proj.get("title", "")
            description = proj.get("description", "")
            tech = proj.get("tech", "")
            
            projects_html += f"""
    <div class="project">
        <span class="project-title">{title}</span>
        <div class="project-desc">{description}</div>
        <div class="project-tech">{tech}</div>
    </div>"""
        
        return html.replace("{{PROJECTS}}", projects_html)

    def render_education_section(self, html: str, education: List[Dict]) -> str:
        """Render education section"""
        
        if not education:
            return html.replace("{{EDUCATION}}", "<p style='color:#888'>No education listed</p>")
        
        edu_html = ""
        for edu in education:
            year = edu.get("year", "")
            title = edu.get("title", "")
            org = edu.get("organization", "")
            desc = edu.get("description", "")
            
            edu_html += f"""
    <div class="edu-item">
        <div class="edu-header">
            <span class="edu-title">{title} — <span class="edu-org">{org}</span></span>
            <span class="edu-year">{year}</span>
        </div>
        <div class="edu-desc">{desc}</div>
    </div>"""
        
        return html.replace("{{EDUCATION}}", edu_html)

    def render_certifications_section(self, html: str, certifications: List[Dict]) -> str:
        """Render certifications section"""
        
        if not certifications:
            return html.replace("{{CERTIFICATIONS}}", "")
        
        cert_html = ""
        for cert in certifications:
            title = cert.get("title", "")
            org = cert.get("organization", "")
            year = cert.get("year", "")
            
            cert_html += f"""
    <div class="cert-item">
        <span class="cert-title">{title} — <span class="cert-org">{org}</span></span>
        <span class="cert-year">{year}</span>
    </div>"""
        
        return html.replace("{{CERTIFICATIONS}}", cert_html)

    def get_resume_template(self) -> str:
        """Get the resume HTML template (from career-ops)"""
        
        # Embedded template - optimized for ATS
        return """<!DOCTYPE html>
<html lang="{{LANG}}">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{{NAME}} — CV</title>
<style>
  @font-face {
    font-family: 'Space Grotesk';
    src: url('https://fonts.gstatic.com/s/spacegrotesk/v16/V8mQoQDjQSkFtoMM3T6r8E7mF71Q-gOoraIAEj62UUsjNsFjTDJK.woff2') format('woff2');
    font-weight: 300 700;
    font-style: normal;
    font-display: swap;
  }
  @font-face {
    font-family: 'DM Sans';
    src: url('https://fonts.gstatic.com/s/dmsans/v15/rP2tp2ywxg089UriI5-g4vlH9VoD8CmcqZG40F9JadbnoEwAop9hTmf3ZGMZpg.woff2') format('woff2');
    font-weight: 100 1000;
    font-style: normal;
  }
  * { margin: 0; padding: 0; box-sizing: border-box; }
  html { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
  body { font-family: 'DM Sans', sans-serif; font-size: 11px; line-height: 1.5; color: #1a1a2e; background: #ffffff; padding: 0; margin: 0; }
  .page { width: 100%; max-width: {{PAGE_WIDTH}}; margin: 0 auto; padding: 2px 0; }
  .header { margin-bottom: 20px; }
  .header h1 { font-family: 'Space Grotesk', sans-serif; font-size: 28px; font-weight: 700; color: #1a1a2e; letter-spacing: -0.02em; margin-bottom: 6px; line-height: 1.1; }
  .header-gradient { height: 2px; background: linear-gradient(to right, hsl(187, 74%, 32%), hsl(270, 70%, 45%)); border-radius: 1px; margin-bottom: 10px; }
  .contact-row { display: flex; flex-wrap: wrap; gap: 8px 14px; font-family: 'DM Sans', sans-serif; font-size: 10.5px; line-height: 1.4; color: #555; }
  .contact-row a { color: #555; text-decoration: none; }
  .contact-row .separator { color: #ccc; }
  .section { margin-bottom: 18px; }
  .section-title { font-family: 'Space Grotesk', sans-serif; font-size: 12px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.06em; color: hsl(187, 74%, 32%); border-bottom: 1.5px solid #e2e2e2; padding-bottom: 4px; margin-bottom: 10px; line-height: 1.2; }
  .summary-text { font-size: 11px; line-height: 1.7; color: #2f2f2f; }
  a { white-space: nowrap; }
  .competencies-grid { display: flex; flex-wrap: wrap; gap: 8px; }
  .competency-tag { font-family: 'DM Sans', sans-serif; font-size: 10px; font-weight: 500; color: hsl(187, 74%, 28%); background: hsl(187, 40%, 95%); padding: 4px 10px; border-radius: 3px; border: 1px solid hsl(187, 40%, 88%); }
  .job { margin-bottom: 14px; }
  .job-header { display: flex; justify-content: space-between; align-items: baseline; gap: 12px; margin-bottom: 4px; }
  .job-company { font-family: 'Space Grotesk', sans-serif; font-size: 12.5px; font-weight: 600; color: hsl(270, 70%, 45%); }
  .job-period { font-size: 10.5px; color: #777; white-space: nowrap; }
  .job-role { font-size: 11px; font-weight: 600; color: #333; margin-bottom: 6px; }
  .job-location { font-size: 10px; color: #888; }
  .job ul { padding-left: 18px; margin-top: 6px; }
  .job li { font-size: 10.5px; line-height: 1.6; color: #333; margin-bottom: 4px; }
  .job li strong { font-weight: 600; }
  .project { margin-bottom: 12px; }
  .project-title { font-family: 'Space Grotesk', sans-serif; font-size: 11.5px; font-weight: 600; color: hsl(270, 70%, 45%); }
  .project-desc { font-size: 10.5px; color: #444; margin-top: 3px; line-height: 1.55; }
  .project-tech { font-size: 9.5px; color: #888; margin-top: 3px; }
  .edu-item { margin-bottom: 8px; }
  .edu-header { display: flex; justify-content: space-between; align-items: baseline; gap: 12px; }
  .edu-title { font-weight: 600; font-size: 11px; color: #333; }
  .edu-org { color: hsl(270, 70%, 45%); font-weight: 500; }
  .edu-year { font-size: 10px; color: #777; white-space: nowrap; }
  .edu-desc { font-size: 10px; color: #666; margin-top: 2px; line-height: 1.5; }
  .cert-item { display: flex; justify-content: space-between; align-items: baseline; gap: 12px; margin-bottom: 6px; }
  .cert-title { font-size: 10.5px; font-weight: 500; color: #333; }
  .cert-org { color: hsl(270, 70%, 45%); }
  .cert-year { font-size: 10px; color: #777; white-space: nowrap; }
  .skills-grid { display: flex; flex-wrap: wrap; gap: 6px 14px; }
  .skill-item { font-size: 10.5px; color: #444; }
  .skill-category { font-weight: 600; color: #333; font-size: 10.5px; }
  @media print { body { -webkit-print-color-adjust: exact; print-color-adjust: exact; } .page { padding: 0; } }
  .avoid-break, .job, .project, .edu-item, .cert-item { break-inside: avoid; page-break-inside: avoid; }
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
    {{SKILLS}}
  </div>
</div>
</body>
</html>"""

    async def html_to_pdf(self, html: str) -> bytes:
        """Convert HTML to PDF using Playwright"""
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            
            # Set content
            await page.set_content(html, wait_until="networkidle")
            
            # Generate PDF
            pdf = await page.pdf(
                format="A4",
                margin={"top": "0", "bottom": "0", "left": "0", "right": "0"},
                print_background=True
            )
            
            await browser.close()
        
        return pdf

    async def save_resume_pdf(
        self,
        user_id: str,
        user_data: Dict,
        job_data: Optional[Dict] = None,
        keywords: Optional[List[str]] = None
    ) -> str:
        """Generate and save resume PDF to file"""
        
        pdf_bytes = await self.generate_resume_pdf(user_data, job_data, keywords)
        
        # Create filename
        company_slug = job_data.get("company", "general").lower().replace(" ", "-") if job_data else "general"
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{user_id}_{company_slug}_{timestamp}.pdf"
        filepath = os.path.join(self.output_dir, filename)
        
        # Save to file
        with open(filepath, "wb") as f:
            f.write(pdf_bytes)
        
        logger.info(f"Saved resume PDF: {filepath}")
        
        return filepath


# Singleton instance
pdf_generator = PDFGeneratorService()