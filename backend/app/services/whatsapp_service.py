import httpx
import json
import asyncio
import base64
from typing import Optional, List, Dict, Any
from datetime import datetime
from loguru import logger

from app.core.config import settings


class WhatsAppService:
    def __init__(self):
        self.account_sid = settings.TWILIO_ACCOUNT_SID
        self.auth_token = settings.TWILIO_AUTH_TOKEN
        self.phone_number = settings.TWILIO_PHONE_NUMBER
        self.api_url = f"https://api.twilio.com/2010-04-01/Accounts/{self.account_sid}"
        
    def _get_auth(self) -> str:
        credentials = f"{self.account_sid}:{self.auth_token}"
        return base64.b64encode(credentials.encode()).decode()

    async def send_message(self, to: str, text: str) -> Dict[str, Any]:
        """Send text message via Twilio WhatsApp"""
        if not self.account_sid or not self.auth_token:
            return {"success": False, "error": "Twilio not configured"}
        
        to = to.strip().replace("+", "").replace(" ", "")
        if not to.startswith("whatsapp:"):
            to = f"whatsapp:{to}"
        
        payload = {
            "From": self.phone_number or "whatsapp:+14155238888",
            "To": to,
            "Body": text
        }
        
        headers = {
            "Authorization": f"Basic {self._get_auth()}",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.post(
                    f"{self.api_url}/Messages.json",
                    headers=headers,
                    data=payload
                )
                if response.status_code == 201:
                    return {"success": True, "data": response.json()}
                return {"success": False, "error": response.text}
            except Exception as e:
                logger.error(f"Twilio error: {e}")
                return {"success": False, "error": str(e)}

    async def send_template(
        self,
        to: str,
        template: str,
        params: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """Send templated message"""
        body = template
        if params:
            for key, val in params.items():
                body = body.replace(f"{{{key}}}", val)
        return await self.send_message(to, body)

    async def send_list_message(
        self,
        to: str,
        title: str,
        items: List[str]
    ) -> Dict[str, Any]:
        """Send list message"""
        text = f"*{title}*\n\n"
        for i, item in enumerate(items, 1):
            text += f"{i}. {item}\n"
        return await self.send_message(to, text)

    async def send_job_card(
        self,
        to: str,
        job: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Send job details as formatted message"""
        text = f"""*{job.get('title', 'Job')}*
🏢 {job.get('company', 'Company')}
📍 {job.get('location', 'N/A')}
💰 {job.get('salary', 'N/A')}
🔗 {job.get('apply_url', 'N/A')}

{job.get('description', '')[:200]}..."""
        return await self.send_message(to, text)

    async def send_interactive_buttons(
        self,
        to: str,
        text: str,
        buttons: List[Dict[str, str]]
    ) -> Dict[str, Any]:
        """Send interactive buttons message"""
        text += "\n\n"
        for btn in buttons:
            text += f"• {btn.get('title')}\n"
        return await self.send_message(to, text)

    async def send_job_alert(
        self,
        to: str,
        jobs: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Send job alert with multiple jobs"""
        if not jobs:
            return await self.send_message(to, "No new jobs matching your alerts today! 🔍")
        
        text = f"🔔 *{len(jobs)} New Job Matches!*\n\n"
        
        for i, job in enumerate(jobs[:5], 1):
            text += f"{i}. *{job.get('title', 'Position')}*\n"
            text += f"   🏢 {job.get('company', 'Company')}\n"
            if job.get('location'):
                text += f"   📍 {job['location']}\n"
            if job.get('salary'):
                text += f"   💰 {job['salary']}\n"
            text += "\n"
        
        if len(jobs) > 5:
            text += f"_+{len(jobs) - 5} more jobs_"
        
        text += "\n\nReply with number to apply, or 'more' for more options."
        
        return await self.send_message(to, text)

    async def send_interview_reminder(
        self,
        to: str,
        company: str,
        role: str,
        time: str
    ) -> Dict[str, Any]:
        """Send interview reminder"""
        text = (
            f"🎯 *Interview Reminder!*\n\n"
            f"📋 {role} at {company}\n"
            f"⏰ {time}\n\n"
            f"Want me to help you prepare? Reply 'prep {company}'"
        )
        return await self.send_message(to, text)

    async def send_application_confirmation(
        self,
        to: str,
        job_title: str,
        company: str
    ) -> Dict[str, Any]:
        """Send application confirmation"""
        text = (
            f"✅ *Application Sent!*\n\n"
            f"🎯 {job_title} at {company}\n\n"
            f"I'll notify you when they view your resume!\n\n"
            f"Reply 'status' to see all your applications."
        )
        return await self.send_message(to, text)

    async def send_cover_letter(
        self,
        to: str,
        company: str,
        role: str,
        cover_letter: str
    ) -> Dict[str, Any]:
        """Send generated cover letter"""
        text = (
            f"📝 *Cover Letter for {role}*\n\n"
            f"_{cover_letter}_\n\n"
            f"Want me to:\n"
            f"• Generate a different style\n"
            f"• Save this for later\n"
            f"• Apply now with this"
        )
        return await self.send_message(to, text)


whatsapp_service = WhatsAppService()