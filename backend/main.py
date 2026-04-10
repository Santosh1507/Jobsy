from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
import sys

from app.core.config import settings
from app.core.database import init_db
from app.api import whatsapp, jobs, applications, subscriptions, tools

# Configure logging
logger.remove()
logger.add(
    sys.stdout,
    colorize=True,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>"
)

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    description="WhatsApp-native job automation platform",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Startup event
@app.on_event("startup")
async def startup_event():
    logger.info("Starting Jobsy WhatsApp Job Platform...")
    
    from app.core.config import settings
    logger.info(f"Twilio SID: {settings.TWILIO_ACCOUNT_SID[:10] if settings.TWILIO_ACCOUNT_SID else 'NOT SET'}")
    logger.info(f"Twilio Auth: {settings.TWILIO_AUTH_TOKEN[:5] if settings.TWILIO_AUTH_TOKEN else 'NOT SET'}...")
    logger.info(f"Twilio Phone: {settings.TWILIO_PHONE_NUMBER}")
    
    # Initialize database
    try:
        await init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.warning(f"Database initialization skipped: {e}")
    
    # Start background workers
    try:
        from app.workers.scheduler import start_all_workers
        await start_all_workers()
    except Exception as e:
        logger.warning(f"Workers skipped: {e}")
    
    logger.info("Application started successfully")


# Root endpoint
@app.get("/")
async def root():
    return {
        "name": settings.APP_NAME,
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
        "webhook": "/webhook/twilio"
    }


@app.get("/test-webhook")
async def test_webhook():
    """Direct test endpoint"""
    from app.services.whatsapp_service import whatsapp_service
    
    # Send to user's WhatsApp number
    result = await whatsapp_service.send_message(
        to="whatsapp:+918688439658", 
        text="Hello from Jobsy! Your WhatsApp bot is working!"
    )
    return {"test": "sent", "result": result}
        "sid": settings.TWILIO_ACCOUNT_SID,
        "token": settings.TWILIO_AUTH_TOKEN[:5] + "..." if settings.TWILIO_AUTH_TOKEN else None,
        "phone": settings.TWILIO_PHONE_NUMBER
    }}


# Health check
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "database": "connected",
        "whatsapp_api": "configured"
    }


# Include routers
app.include_router(whatsapp.router, prefix="/webhook")
app.include_router(jobs.router, prefix="/api/v1")
app.include_router(applications.router, prefix="/api/v1")
app.include_router(subscriptions.router, prefix="/api/v1")
app.include_router(tools.router, prefix="/api/v1")


# Error handlers
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Global exception: {exc}")
    return {
        "error": "Internal server error",
        "detail": str(exc)
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )