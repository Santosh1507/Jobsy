import httpx
import json
import hashlib
import asyncio
from typing import Optional, List, Dict, Any
from datetime import datetime
from loguru import logger

from app.core.config import settings
from app.models.schemas import (
    WhatsAppMessageRequest,
    WhatsAppMessageResponse,
    WhatsAppInteractiveMessage
)


class WhatsAppService:
    def __init__(self):
        self.api_url = "https://graph.facebook.com/v21.0"
        self.phone_number_id = settings.WHATSAPP_PHONE_NUMBER_ID
        self.access_token = settings.WHATSAPP_ACCESS_TOKEN
        self.headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }

    async def send_message(
        self,
        to: str,
        text: str,
        preview_url: bool = False
    ) -> Dict[str, Any]:
        """Send text message via WhatsApp API"""
        payload = {
            "messaging_product": "whatsapp",
            "to": to,
            "type": "text",
            "text": {
                "body": text,
                "preview_url": preview_url
            }
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.post(
                    f"{self.api_url}/{self.phone_number_id}/messages",
                    headers=self.headers,
                    json=payload
                )
                response.raise_for_status()
                return response.json()
            except httpx.HTTPError as e:
                logger.error(f"WhatsApp API error: {e}")
                raise

    async def send_interactive_buttons(
        self,
        to: str,
        text: str,
        buttons: List[Dict[str, str]]
    ) -> Dict[str, Any]:
        """Send interactive buttons message"""
        payload = {
            "messaging_product": "whatsapp",
            "to": to,
            "type": "interactive",
            "interactive": {
                "type": "button",
                "body": {"text": text},
                "action": {
                    "buttons": buttons
                }
            }
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.post(
                    f"{self.api_url}/{self.phone_number_id}/messages",
                    headers=self.headers,
                    json=payload
                )
                response.raise_for_status()
                return response.json()
            except httpx.HTTPError as e:
                logger.error(f"WhatsApp interactive buttons error: {e}")
                raise

    async def send_list_message(
        self,
        to: str,
        text: str,
        sections: List[Dict]
    ) -> Dict[str, Any]:
        """Send list/select message"""
        payload = {
            "messaging_product": "whatsapp",
            "to": to,
            "type": "interactive",
            "interactive": {
                "type": "list",
                "body": {"text": text},
                "action": {
                    "button": "Select Option",
                    "sections": sections
                }
            }
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.post(
                    f"{self.api_url}/{self.phone_number_id}/messages",
                    headers=self.headers,
                    json=payload
                )
                response.raise_for_status()
                return response.json()
            except httpx.HTTPError as e:
                logger.error(f"WhatsApp list message error: {e}")
                raise

    async def send_document(
        self,
        to: str,
        document_url: str,
        caption: str,
        filename: str = "resume.pdf"
    ) -> Dict[str, Any]:
        """Send document message"""
        payload = {
            "messaging_product": "whatsapp",
            "to": to,
            "type": "document",
            "document": {
                "link": document_url,
                "caption": caption,
                "filename": filename
            }
        }

        async with httpx.AsyncClient(timeout=60.0) as client:
            try:
                response = await client.post(
                    f"{self.api_url}/{self.phone_number_id}/messages",
                    headers=self.headers,
                    json=payload
                )
                response.raise_for_status()
                return response.json()
            except httpx.HTTPError as e:
                logger.error(f"WhatsApp document error: {e}")
                raise

    async def send_image(
        self,
        to: str,
        image_url: str,
        caption: Optional[str] = None
    ) -> Dict[str, Any]:
        """Send image message"""
        payload = {
            "messaging_product": "whatsapp",
            "to": to,
            "type": "image",
            "image": {
                "link": image_url,
                "caption": caption
            }
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.post(
                    f"{self.api_url}/{self.phone_number_id}/messages",
                    headers=self.headers,
                    json=payload
                )
                response.raise_for_status()
                return response.json()
            except httpx.HTTPError as e:
                logger.error(f"WhatsApp image error: {e}")
                raise

    async def send_template(
        self,
        to: str,
        template_name: str,
        components: Optional[List[Dict]] = None
    ) -> Dict[str, Any]:
        """Send template message (e.g., daily job drop)"""
        payload = {
            "messaging_product": "whatsapp",
            "to": to,
            "type": "template",
            "template": {
                "name": template_name,
                "language": {"code": "en_US"},
                "components": components or []
            }
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.post(
                    f"{self.api_url}/{self.phone_number_id}/messages",
                    headers=self.headers,
                    json=payload
                )
                response.raise_for_status()
                return response.json()
            except httpx.HTTPError as e:
                logger.error(f"WhatsApp template error: {e}")
                raise

    async def send_status_update(
        self,
        to: str,
        company: str,
        status: str,
        details: Optional[str] = None
    ) -> Dict[str, Any]:
        """Send application status update notification"""
        status_messages = {
            "viewed": f"👀 *{company}* viewed your resume",
            "shortlisted": f"✅ *{company}* shortlisted you!",
            "interview": f"🎉 *{company}* wants to interview you!",
            "offer": f"💰 *{company}* made an offer!",
            "rejected": f"😔 *{company}* moved forward with other candidates"
        }
        
        message = status_messages.get(status, f"Update from *{company}*")
        if details:
            message += f"\n\n{details}"
        
        return await self.send_message(to, message)

    async def send_daily_job_drop(
        self,
        to: str,
        jobs: List[Dict]
    ) -> Dict[str, Any]:
        """Send daily job recommendations"""
        message = "🌟 *Today's Top Job Matches*\n\n"
        
        for i, job in enumerate(jobs[:3], 1):
            match_score = job.get("match_score", 0)
            emoji = "🔥" if match_score > 80 else "✨" if match_score > 60 else "📋"
            
            message += f"{emoji} *{i}. {job['title']}*\n"
            message += f"🏢 {job['company']} | 📍 {job.get('location', 'N/A')}\n"
            if job.get("salary"):
                message += f"💰 {job['salary']}\n"
            message += f"🎯 {match_score}% match\n\n"
        
        buttons = []
        for i in range(min(3, len(jobs))):
            buttons.append({
                "type": "reply",
                "reply": {
                    "id": f"apply_{jobs[i]['id']}",
                    "title": f"Apply #{i+1}"
                }
            })
        
        buttons.append({
            "type": "reply",
            "reply": {
                "id": "more_jobs",
                "title": "More Jobs"
            }
        })
        
        return await self.send_interactive_buttons(to, message, buttons)

    def parse_incoming_message(self, payload: Dict) -> Dict[str, Any]:
        """Parse incoming WhatsApp webhook payload"""
        try:
            entry = payload.get("entry", [])[0]
            changes = entry.get("changes", [])[0]
            value = changes.get("value", {})
            
            messages = value.get("messages", [])
            if not messages:
                return {}
            
            message = messages[0]
            metadata = value.get("metadata", {})
            
            return {
                "phone_number_id": metadata.get("phone_number_id"),
                "from": message.get("from"),
                "message_id": message.get("id"),
                " timestamp": message.get("timestamp"),
                "type": message.get("type"),
                "text": message.get("text", {}).get("body", ""),
                "image": message.get("image"),
                "document": message.get("document"),
                "interactive": message.get("interactive")
            }
        except (IndexError, KeyError) as e:
            logger.error(f"Error parsing WhatsApp message: {e}")
            return {}

    def extract_button_reply(self, payload: Dict) -> Optional[Dict[str, str]]:
        """Extract button reply from interactive message"""
        try:
            entry = payload.get("entry", [])[0]
            changes = entry.get("changes", [])[0]
            value = changes.get("value", {})
            
            messages = value.get("messages", [])
            if not messages:
                return None
            
            message = messages[0]
            interactive = message.get("interactive", {})
            
            if interactive.get("type") == "button_reply":
                return interactive.get("button_reply", {})
            
            if interactive.get("type") == "list_reply":
                return interactive.get("list_reply", {})
                
        except (IndexError, KeyError):
            pass
        
        return None


# Singleton instance
whatsapp_service = WhatsAppService()