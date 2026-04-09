from fastapi import APIRouter, Request, HTTPException, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, Dict, Any
from loguru import logger
import hashlib
import hmac

from app.core.database import get_db, AsyncSession
from app.models.database import User
from app.services.whatsapp_service import whatsapp_service
from app.conversation.engine import process_user_message
from sqlalchemy import select

router = APIRouter(prefix="/webhook", tags=["WhatsApp"])


class WebhookVerifyRequest(BaseModel):
    """Request model for webhook verification"""
    hub_mode: str
    hub_challenge: str
    hub_verify_token: str


async def verify_webhook(request: Request):
    """Verify webhook for Meta"""
    query_params = request.query_params
    
    mode = query_params.get("hub.mode")
    token = query_params.get("hub.verify_token")
    challenge = query_params.get("hub.challenge")
    
    # TODO: Replace with actual verify token from settings
    verify_token = "jobsy_verify_token_123"
    
    if mode == "subscribe" and token == verify_token:
        logger.info("Webhook verified successfully")
        return JSONResponse(content=int(challenge))
    
    raise HTTPException(status_code=403, detail="Verification failed")


async def verify_signature(request: Request):
    """Verify webhook signature from Meta"""
    signature = request.headers.get("x-hub-signature-256")
    
    if not signature:
        logger.warning("No signature provided")
        return
    
    # TODO: Implement proper signature verification
    # signature format: sha256=...


@router.post("/whatsapp")
async def whatsapp_webhook(request: Request, db: AsyncSession = Depends(get_db)):
    """Handle incoming WhatsApp messages"""
    
    try:
        body = await request.json()
        
        # Check if this is a verification request
        if "hub_mode" in body.get("entry", [{}])[0].get("changes", [{}])[0].get("value", {}):
            return await verify_webhook(request)
        
        # Parse incoming message
        message_data = whatsapp_service.parse_incoming_message(body)
        
        if not message_data or not message_data.get("from"):
            logger.warning("No valid message data found in webhook")
            return {"status": "ok"}
        
        from_phone = message_data["from"]
        message_id = message_data.get("message_id", "")
        
        logger.info(f"Received WhatsApp message from {from_phone}: {message_data.get('text', '')[:50]}")
        
        # Find or create user
        user_result = await db.execute(
            select(User).where(User.phone == from_phone)
        )
        user = user_result.scalar_one_or_none()
        
        if not user:
            # Create new user
            user = User(
                phone=from_phone,
                whatsapp_id=from_phone
            )
            db.add(user)
            await db.commit()
            await db.refresh(user)
        
        # Update last active
        from datetime import datetime
        user.last_active_at = datetime.utcnow()
        
        # Get message content
        message_text = message_data.get("text", "")
        message_type = message_data.get("type", "text")
        
        # Handle different message types
        if message_type == "document":
            message_text = "[Document uploaded - resume]"
        elif message_type == "image":
            message_text = "[Image uploaded]"
        
        # Process message through conversation engine
        response_text = await process_user_message(
            db=db,
            user_id=str(user.id),
            message=message_text,
            message_type=message_type,
            metadata=message_data
        )
        
        # Send response back via WhatsApp
        await whatsapp_service.send_message(
            to=from_phone,
            text=response_text
        )
        
        # Log outbound message
        from app.models.database import MessageLog
        log = MessageLog(
            user_id=user.id,
            direction="outbound",
            message_text=response_text
        )
        db.add(log)
        await db.commit()
        
        return {"status": "ok", "message_id": message_id}
    
    except Exception as e:
        logger.error(f"Error processing WhatsApp webhook: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/twilio")
async def twilio_webhook(request: Request, db: AsyncSession = Depends(get_db)):
    """Handle incoming Twilio WhatsApp messages"""
    try:
        form = await request.form()
        
        from_phone = form.get("From", "")
        message_body = form.get("Body", "")
        
        if not from_phone or not message_body:
            return {"success": True}
        
        logger.info(f"Twilio: Message from {from_phone}: {message_body[:50]}")
        
        # Process message
        response_text = await process_user_message(
            db=db,
            user_id=from_phone,
            message=message_body,
            message_type="text"
        )
        
        # Send response via Twilio
        await whatsapp_service.send_message(
            to=from_phone,
            text=response_text
        )
        
        return "<Response></Response>"
    
    except Exception as e:
        logger.error(f"Twilio webhook error: {e}")
        return "<Response></Response>"


@router.get("/twilio")
async def twilio_webhook_get():
    """Twilio webhook GET handler"""
    return {"status": "ok"}


@router.get("/whatsapp")
async def whatsapp_webhook_get(request: Request):
    """Handle WhatsApp webhook verification (GET)"""
    return await verify_webhook(request)


@router.get("/status")
async def webhook_status():
    """Health check endpoint"""
    return {
        "status": "active",
        "service": "whatsapp-webhook",
        "version": "1.0.0"
    }