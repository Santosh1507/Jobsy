import asyncio
import random
import json
from typing import Dict, List, Optional, Any
from datetime import datetime
from loguru import logger

from app.core.config import settings


ATS_CONFIGS = {
    "greenhouse": {
        "name": "Greenhouse",
        "form_url": "{job_url}",
        "selectors": {
            "first_name": 'input[name="first_name"], input[name*="firstname"]',
            "last_name": 'input[name="last_name"], input[name*="lastname"]',
            "email": 'input[name="email"], input[type="email"]',
            "phone": 'input[name="phone"], input[name*="phone"]',
            "resume": 'input[name="resume"][type="file"], input[type="file"]',
            "cover_letter": 'textarea[name="cover_letter"], textarea[name*="cover"]',
            "submit": 'button[type="submit"], input[type="submit"], button:contains("Submit")',
            "autofirst_name": '[data-qa="first-name"]',
            "autolast_name": '[data-qa="last-name"]',
            "autoemail": '[data-qa="email"]',
            "autophone": '[data-qa="phone_number"]',
        },
        "next_button": 'button:contains("Next"), button:contains("Continue")',
    },
    "lever": {
        "name": "Lever",
        "form_url": "{job_url}",
        "selectors": {
            "first_name": 'input[name="firstname"], input[name*="firstname"]',
            "last_name": 'input[name="lastname"], input[name*="lastname"]',
            "email": 'input[name="email"], input[type="email"]',
            "phone": 'input[name="phone"], input[name*="phone"]',
            "resume": 'input[type="file"]',
            "cover_letter": 'textarea[name="cover_letter"]',
            "submit": 'button[type="submit"], button:contains("Submit Application")',
        },
        "next_button": 'button:contains("Next"), button:contains("Continue")',
    },
    "ashby": {
        "name": "Ashby",
        "form_url": "{job_url}",
        "selectors": {
            "first_name": 'input[name="firstName"], input[name*="firstName"]',
            "last_name": 'input[name="lastName"], input[name*="lastName"]',
            "email": 'input[name="email"], input[type="email"]',
            "phone": 'input[name="phone"], input[name="phoneNumber"]',
            "resume": 'input[type="file"][name*="resume"], input[type="file"]',
            "submit": 'button[type="submit"], button:contains("Apply")',
        },
        "next_button": 'button:contains("Next"), button:contains("Continue")',
    },
    "workday": {
        "name": "Workday",
        "form_url": "{job_url}",
        "selectors": {
            "first_name": 'input[name="firstName"]',
            "last_name": 'input[name="lastName"]',
            "email": 'input[name="emailAddress"]',
            "phone": 'input[name="phoneNumber"]',
            "resume": 'input[type="file"]',
            "submit": 'button[data-automation-id="submitButton"]',
        },
        "login_required": True,
    },
}


class ApplyEngine:
    def __init__(self):
        self.max_applications_per_day = settings.MAX_APPLICATIONS_PER_DAY
        self.ats_configs = ATS_CONFIGS
        self.playwright = None
        self.browser = None

    def _detect_ats(self, url: str) -> str:
        url_lower = url.lower()
        
        if "greenhouse" in url_lower or "boards.greenhouse.io" in url_lower:
            return "greenhouse"
        elif "lever.co" in url_lower or "jobs.lever.co" in url_lower:
            return "lever"
        elif "ashby" in url_lower or "jobs.ashbyhq.com" in url_lower:
            return "ashby"
        elif "workday" in url_lower:
            return "workday"
        else:
            return "generic"

    async def apply_to_job(
        self,
        user_id: str,
        job_id: str,
        resume_data: Dict,
        cover_letter: Optional[str] = None
    ) -> Dict[str, Any]:
        
        job_url = resume_data.get("apply_url", "")
        if not job_url:
            return {"success": False, "message": "No apply URL provided"}
        
        ats_type = self._detect_ats(job_url)
        
        if ats_type == "generic":
            return {
                "success": False,
                "message": "Unsupported ATS platform. Please apply manually.",
                "apply_url": job_url
            }
        
        try:
            return await self._apply_via_ats(
                ats_type=ats_type,
                job_url=job_url,
                user_data=resume_data,
                cover_letter=cover_letter
            )
        except Exception as e:
            logger.error(f"Auto-apply failed: {e}")
            return {
                "success": False,
                "message": str(e),
                "apply_url": job_url
            }

    async def _apply_via_ats(
        self,
        ats_type: str,
        job_url: str,
        user_data: Dict,
        cover_letter: Optional[str]
    ) -> Dict[str, Any]:
        
        config = self.ats_configs.get(ats_type, {})
        selectors = config.get("selectors", {})
        
        try:
            from playwright.async_api import async_playwright
            
            async with async_playwright() as p:
                browser = await p.chromium.launch(
                    headless=True,
                    args=["--disable-blink-features=AutomationControlled"]
                )
                page = await browser.new_page(
                    viewport={"width": 1280, "height": 720},
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                )
                
                await page.goto(job_url, wait_until="domcontentloaded", timeout=30000)
                await asyncio.sleep(random.uniform(1, 3))
                
                first_name = user_data.get("first_name", user_data.get("name", "").split()[0] if user_data.get("name") else "")
                last_name = user_data.get("last_name", " ".join(user_data.get("name", "").split()[1:]) if user_data.get("name") else "")
                email = user_data.get("email", "")
                phone = user_data.get("phone", "")
                
                await self._fill_field(page, selectors.get("first_name", 'input[name="first_name"]'), first_name)
                await asyncio.sleep(random.uniform(0.2, 0.5))
                
                await self._fill_field(page, selectors.get("last_name", 'input[name="last_name"]'), last_name)
                await asyncio.sleep(random.uniform(0.2, 0.5))
                
                await self._fill_field(page, selectors.get("email", 'input[name="email"]'), email)
                await asyncio.sleep(random.uniform(0.2, 0.5))
                
                await self._fill_field(page, selectors.get("phone", 'input[name="phone"]'), phone)
                await asyncio.sleep(random.uniform(0.2, 0.5))
                
                resume_file = user_data.get("resume_file")
                if resume_file:
                    try:
                        await page.set_input_files(selectors.get("resume", 'input[type="file"]'), resume_file)
                    except Exception as e:
                        logger.warning(f"Resume upload failed: {e}")
                
                if cover_letter:
                    await self._fill_field(page, selectors.get("cover_letter", 'textarea[name="cover_letter"]'), cover_letter)
                    await asyncio.sleep(random.uniform(0.2, 0.5))
                
                try:
                    submit_btn = page.locator(selectors.get("submit", 'button[type="submit"]'))
                    await submit_btn.click()
                    await asyncio.sleep(random.uniform(2, 4))
                    
                    confirmation = await page.text_content("body")
                    if "thank" in confirmation.lower() or "success" in confirmation.lower() or "applied" in confirmation.lower():
                        await browser.close()
                        return {
                            "success": True,
                            "message": "Application submitted successfully",
                            "ats_type": ats_type
                        }
                except Exception as e:
                    logger.warning(f"Submit failed: {e}")
                
                await browser.close()
                
                return {
                    "success": False,
                    "message": "Application form could not be submitted automatically",
                    "apply_url": job_url,
                    "suggestion": "Please apply manually"
                }
                
        except ImportError:
            return {
                "success": False,
                "message": "Playwright not installed. Install with: pip install playwright && npx playwright install chromium",
                "apply_url": job_url
            }
        except Exception as e:
            logger.error(f"Auto-apply error: {e}")
            return {
                "success": False,
                "message": f"Application failed: {str(e)}",
                "apply_url": job_url
            }

    async def _fill_field(self, page, selector: str, value: str):
        if not value:
            return
        
        try:
            field = page.locator(selector)
            if await field.count() > 0:
                await field.first.fill(value)
        except Exception:
            pass

    async def apply_batch(
        self,
        applications: List[Dict],
        user_id: str
    ) -> List[Dict]:
        """Apply to multiple jobs"""
        results = []
        
        for app in applications[:self.max_applications_per_day]:
            result = await self.apply_to_job(
                user_id=user_id,
                job_id=app.get("job_id", ""),
                resume_data=app,
                cover_letter=app.get("cover_letter")
            )
            results.append(result)
            
            await asyncio.sleep(random.uniform(30, 90))
        
        return results


apply_engine = ApplyEngine()