import asyncio
import random
import json
from typing import Dict, List, Optional, Any
from datetime import datetime
from playwright.async_api import async_playwright, Browser, Page, Playwright
from loguru import logger

from app.core.config import settings
from app.services.ollama_service import ollama_service


class ApplyEngine:
    """Auto-apply engine using Playwright for browser automation"""
    
    def __init__(self):
        self.playwright: Optional[Playwright] = None
        self.browser: Optional[Browser] = None
        self.context = None
        self.max_applications_per_day = settings.MAX_APPLICATIONS_PER_DAY
        
        # ATS platform configurations
        self.ats_configs = {
            "greenhouse": {
                "login_required": False,
                "form_selectors": {
                    "resume": 'input[type="file"][name*="resume"]',
                    "name": 'input[name*="name"]',
                    "email": 'input[name*="email"]',
                    "phone": 'input[name*="phone"]',
                    "submit": 'button[type="submit"], input[type="submit"]'
                }
            },
            "lever": {
                "login_required": False,
                "form_selectors": {
                    "resume": 'input[type="file"]',
                    "name": 'input[name="name"]',
                    "email": 'input[name="email"]',
                    "submit": 'button[type="submit"]'
                }
            },
            "workday": {
                "login_required": True,
                "form_selectors": {
                    "resume": 'input[id*="resume"]',
                    "submit": 'button[data-automation-id="submitButton"]'
                }
            },
            "keka": {
                "login_required": True,
                "form_selectors": {
                    "resume": 'input[type="file"]',
                    "submit": 'button:has-text("Submit")'
                }
            },
            "darwinbox": {
                "login_required": True,
                "form_selectors": {
                    "resume": 'input[type="file"]',
                    "submit": 'button[type="submit"]'
                }
            },
            "direct": {
                "login_required": False,
                "form_selectors": {}
            }
        }
    
    async def initialize(self):
        """Initialize Playwright browser"""
        try:
            self.playwright = await async_playwright().start()
            self.browser = await self.playwright.chromium.launch(
                headless=True,
                args=['--no-sandbox', '--disable-dev-shm-usage']
            )
            self.context = await self.browser.new_context(
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            )
            logger.info("Playwright browser initialized")
        except Exception as e:
            logger.error(f"Failed to initialize Playwright: {e}")
            raise
    
    async def apply_to_job(
        self,
        user_data: Dict,
        job_data: Dict,
        tailored_resume: Optional[bytes] = None
    ) -> Dict[str, Any]:
        """Apply to a job using Playwright automation"""
        
        if not self.browser:
            await self.initialize()
        
        result = {
            "success": False,
            "job_id": str(job_data.get("id", "")),
            "company": job_data.get("company", ""),
            "platform": job_data.get("ats_platform", "direct"),
            "submission_id": None,
            "error": None,
            "timestamp": datetime.utcnow()
        }
        
        try:
            # Detect ATS platform
            apply_url = job_data.get("apply_url", "")
            ats_platform = self.detect_ats_platform(apply_url)
            result["platform"] = ats_platform
            
            # Create new page
            page = await self.context.new_page()
            
            # Navigate to apply URL
            await page.goto(apply_url, timeout=30000)
            
            # Add random delay to avoid bot detection
            await self.random_delay(2, 5)
            
            # Fill application form based on ATS platform
            if ats_platform == "greenhouse":
                success = await self.fill_greenhouse_form(page, user_data, tailored_resume)
            elif ats_platform == "lever":
                success = await self.fill_lever_form(page, user_data, tailored_resume)
            elif ats_platform == "workday":
                success = await self.fill_workday_form(page, user_data, tailored_resume)
            else:
                success = await self.fill_generic_form(page, user_data, tailored_resume)
            
            if success:
                result["success"] = True
                result["submission_id"] = f"auto_{datetime.utcnow().timestamp()}"
                logger.info(f"Successfully applied to {job_data.get('company')}")
            else:
                result["error"] = "Form submission failed"
            
            await page.close()
            
            # Add delay between applications
            await self.random_delay(30, 120)
            
        except Exception as e:
            logger.error(f"Application error: {e}")
            result["error"] = str(e)
        
        return result
    
    def detect_ats_platform(self, url: str) -> str:
        """Detect ATS platform from URL"""
        url_lower = url.lower()
        
        if "greenhouse" in url_lower:
            return "greenhouse"
        elif "lever" in url_lower:
            return "lever"
        elif "workday" in url_lower:
            return "workday"
        elif "keka" in url_lower:
            return "keka"
        elif "darwinbox" in url_lower:
            return "darwinbox"
        elif "recruiter" in url_lower:
            return "smartrecruiters"
        else:
            return "direct"
    
    async def fill_greenhouse_form(
        self,
        page: Page,
        user_data: Dict,
        resume: Optional[bytes]
    ) -> bool:
        """Fill Greenhouse application form"""
        
        try:
            # Fill name
            name_input = page.locator('input[name*="name"], input[id*="name"]')
            if await name_input.count() > 0:
                await name_input.first.fill(user_data.get("name", ""))
            
            # Fill email
            email_input = page.locator('input[name*="email"], input[type="email"]')
            if await email_input.count() > 0:
                await email_input.first.fill(user_data.get("email", ""))
            
            # Fill phone
            phone_input = page.locator('input[name*="phone"], input[type="tel"]')
            if await phone_input.count() > 0:
                await phone_input.first.fill(user_data.get("phone", ""))
            
            # Upload resume if available
            if resume:
                resume_input = page.locator('input[type="file"]')
                if await resume_input.count() > 0:
                    # Note: Playwright can't directly upload from bytes
                    # Would need to save to temp file
                    pass
            
            # Submit form
            submit_btn = page.locator('button[type="submit"], input[type="submit"]')
            if await submit_btn.count() > 0:
                await submit_btn.first.click()
                await page.wait_for_load_state()
                return True
            
        except Exception as e:
            logger.error(f"Greenhouse form error: {e}")
        
        return False
    
    async def fill_lever_form(
        self,
        page: Page,
        user_data: Dict,
        resume: Optional[bytes]
    ) -> bool:
        """Fill Lever application form"""
        
        try:
            # Similar to Greenhouse but with Lever-specific selectors
            await page.wait_for_selector('form', timeout=10000)
            
            # Fill fields
            name = page.locator('input[name="name"]')
            if await name.count() > 0:
                await name.fill(user_data.get("name", ""))
            
            email = page.locator('input[name="email"]')
            if await email.count() > 0:
                await email.fill(user_data.get("email", ""))
            
            # Submit
            submit = page.locator('button[type="submit"]')
            if await submit.count() > 0:
                await submit.click()
                await page.wait_for_load_state()
                return True
                
        except Exception as e:
            logger.error(f"Lever form error: {e}")
        
        return False
    
    async def fill_workday_form(
        self,
        page: Page,
        user_data: Dict,
        resume: Optional[bytes]
    ) -> bool:
        """Fill Workday application form"""
        
        try:
            # Workday forms often require login first
            # This would need authentication handling
            
            await page.wait_for_selector('[data-automation-id="fileUpload"]', timeout=15000)
            
            # Handle Workday file upload
            upload_btn = page.locator('[data-automation-id="fileUpload"]')
            if await upload_btn.count() > 0:
                await upload_btn.first.click()
            
            return True
            
        except Exception as e:
            logger.error(f"Workday form error: {e}")
        
        return False
    
    async def fill_generic_form(
        self,
        page: Page,
        user_data: Dict,
        resume: Optional[bytes]
    ) -> bool:
        """Fill generic job application form"""
        
        try:
            # Wait for page to be interactive
            await page.wait_for_load_state("domcontentloaded")
            await asyncio.sleep(2)
            
            # Try common field patterns
            field_patterns = [
                ('input[name="name"]', user_data.get("name", "")),
                ('input[name="first_name"]', user_data.get("name", "").split()[0] if user_data.get("name") else ""),
                ('input[name="last_name"]', user_data.get("name", "").split()[-1] if user_data.get("name") else ""),
                ('input[type="email"]', user_data.get("email", "")),
                ('input[name="email"]', user_data.get("email", "")),
                ('input[type="tel"]', user_data.get("phone", "")),
                ('input[name="phone"]', user_data.get("phone", ""))
            ]
            
            for selector, value in field_patterns:
                try:
                    field = page.locator(selector)
                    if await field.count() > 0:
                        await field.first.fill(str(value))
                except:
                    pass
            
            # Look for submit button
            submit_selectors = [
                'button[type="submit"]',
                'input[type="submit"]',
                'button:has-text("Submit")',
                'button:has-text("Apply")',
                'a:has-text("Submit")',
                '[role="button"]:has-text("Submit")'
            ]
            
            for selector in submit_selectors:
                btn = page.locator(selector)
                if await btn.count() > 0:
                    await btn.first.click()
                    await page.wait_for_load_state()
                    return True
            
        except Exception as e:
            logger.error(f"Generic form error: {e}")
        
        return False
    
    async def handle_screening_questions(
        self,
        page: Page,
        job_data: Dict,
        user_data: Dict
    ) -> List[str]:
        """Answer screening questions using AI"""
        
        answers = []
        
        try:
            # Find all questions on the page
            questions = await page.query_selector_all('label, [data-question]')
            
            for question in questions[:10]:  # Limit to 10 questions
                question_text = await question.inner_text()
                
                # Use Ollama to generate appropriate answer
                prompt = f"""Answer this job screening question concisely:

Question: {question_text}

User profile:
- Role: {user_data.get('target_role', 'Not specified')}
- Experience: {user_data.get('experience_years', 0)} years
- Skills: {', '.join(user_data.get('skills', []))}

Provide a short 1-2 sentence answer."""

                answer = await ollama_service.generate(prompt, temperature=0.5)
                answers.append({
                    "question": question_text,
                    "answer": answer
                })
                
                # Fill the answer if there's an input field
                try:
                    input_field = question.locator('input, textarea, select')
                    if await input_field.count() > 0:
                        await input_field.first.fill(answer)
                except:
                    pass
                    
        except Exception as e:
            logger.error(f"Screening questions error: {e}")
        
        return answers
    
    async def random_delay(self, min_seconds: int = 1, max_seconds: int = 3):
        """Add random delay to avoid bot detection"""
        delay = random.randint(min_seconds, max_seconds)
        await asyncio.sleep(delay)
    
    async def check_for_captcha(self, page: Page) -> bool:
        """Check if page has CAPTCHA"""
        
        captcha_indicators = [
            "captcha",
            "verify you're human",
            "i'm not a robot",
            "recaptcha"
        ]
        
        page_text = await page.content()
        page_text_lower = page_text.lower()
        
        for indicator in captcha_indicators:
            if indicator in page_text_lower:
                logger.warning("CAPTCHA detected")
                return True
        
        return False
    
    async def close(self):
        """Clean up browser resources"""
        
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
        
        logger.info("Apply engine closed")


# Singleton instance
apply_engine = ApplyEngine()


async def submit_application(
    user_data: Dict,
    job_data: Dict,
    tailored_resume: Optional[bytes] = None
) -> Dict[str, Any]:
    """Entry point for submitting job application"""
    
    return await apply_engine.apply_to_job(user_data, job_data, tailored_resume)