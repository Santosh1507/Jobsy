import json
from typing import Dict, List, Optional, Any
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from app.models.database import User, ConversationState
from app.models.schemas import IntentDetectionResult
from app.services.ollama_service import ollama_service
from app.services.whatsapp_service import whatsapp_service


class ConversationEngine:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.flow_handlers = {
            "onboarding": self.handle_onboarding,
            "job_drop": self.handle_job_drop,
            "job_apply": self.handle_apply,
            "status": self.handle_status,
            "interview_prep": self.handle_interview_prep,
            "offer_analysis": self.handle_offer_analysis,
            "intel": self.handle_intel,
            "profile_update": self.handle_profile_update,
            "help": self.handle_help
        }

    async def process_message(
        self,
        user_id: str,
        message: str,
        message_type: str = "text",
        metadata: Optional[Dict] = None
    ) -> str:
        """Main entry point for processing user messages"""
        
        # Get or create conversation state
        state = await self.get_or_create_state(user_id)
        
        # Detect intent using Ollama
        intent_result = await self.detect_intent(message, state)
        
        # Update state with intent
        state.last_intent = intent_result["intent"]
        
        # Route to appropriate handler
        flow = self.determine_flow(state, intent_result)
        state.current_flow = flow
        
        # Get conversation history for context
        history = await self.get_recent_history(user_id, limit=5)
        
        # Execute flow handler
        response = await self.execute_flow(
            flow,
            message,
            state.collected_data,
            history,
            intent_result.get("entities", {})
        )
        
        # Update conversation state
        await self.update_state(state, intent_result)
        
        # Log message
        await self.log_message(user_id, "inbound", message, intent_result["intent"])
        await self.log_message(user_id, "outbound", response, intent_result["intent"])
        
        return response

    async def detect_intent(
        self,
        message: str,
        state: ConversationState
    ) -> IntentDetectionResult:
        """Use Ollama to detect user intent"""
        
        context = {
            "current_flow": state.current_flow,
            "flow_step": state.flow_step,
            "collected_data": state.collected_data
        }
        
        return await ollama_service.detect_intent(message, context)

    def determine_flow(
        self,
        state: ConversationState,
        intent_result: Dict
    ) -> str:
        """Determine which flow to execute based on state and intent"""
        
        intent = intent_result.get("intent", "")
        
        # Check if in middle of onboarding
        if state.current_flow == "onboarding" and not state.collected_data.get("onboarding_completed"):
            if intent.startswith("onboarding_"):
                return "onboarding"
        
        # Map intents to flows
        intent_to_flow = {
            "onboarding_start": "onboarding",
            "onboarding_name": "onboarding",
            "onboarding_role": "onboarding",
            "onboarding_experience": "onboarding",
            "onboarding_location": "onboarding",
            "onboarding_salary": "onboarding",
            "onboarding_resume": "onboarding",
            "job_request": "job_drop",
            "job_apply": "job_apply",
            "status_request": "status",
            "interview_prep": "interview_prep",
            "offer_analysis": "offer_analysis",
            "intel_request": "intel",
            "profile_update": "profile_update",
            "help": "help"
        }
        
        return intent_to_flow.get(intent, state.current_flow or "onboarding")

    async def execute_flow(
        self,
        flow: str,
        message: str,
        collected_data: Dict,
        history: List[Dict],
        entities: Dict
    ) -> str:
        """Execute the appropriate conversation flow"""
        
        handler = self.flow_handlers.get(flow, self.handle_unknown)
        
        try:
            return await handler(message, collected_data, history, entities)
        except Exception as e:
            logger.error(f"Flow handler error ({flow}): {e}")
            return "Something went wrong. Let's try again. What would you like to do?"

    async def handle_onboarding(
        self,
        message: str,
        collected_data: Dict,
        history: List[Dict],
        entities: Dict
    ) -> str:
        """Handle onboarding conversation flow"""
        
        step = collected_data.get("onboarding_step", 0)
        
        # Step 0: Welcome and name collection
        if step == 0:
            return (
                "Hey! 👋 I'm Jobsy, your AI job search assistant.\n\n"
                "I'll help you find and apply to jobs directly through WhatsApp.\n\n"
                "Let's get started - what's your full name?"
            )
        
        # Step 1: Store name, ask for target role
        if step == 1:
            collected_data["name"] = message
            collected_data["onboarding_step"] = 2
            
            return (
                f"Nice to meet you, {message}! 🎉\n\n"
                "What kind of roles are you targeting?\n"
                "e.g., 'Backend Engineer', 'Product Manager', 'Data Scientist'"
            )
        
        # Step 2: Store role, ask for experience
        if step == 2:
            collected_data["target_role"] = message
            collected_data["onboarding_step"] = 3
            
            return "How many years of experience do you have?"

        # Step 3: Store experience, ask for location
        if step == 3:
            try:
                exp = int(message.strip())
                collected_data["experience_years"] = exp
            except ValueError:
                pass
            
            collected_data["onboarding_step"] = 4
            
            return (
                "Which cities work for you? (or type 'remote' if you're open to it)\n\n"
                "You can list multiple like: 'Bangalore, Hyderabad, Remote'"
            )

        # Step 4: Store cities, ask for salary
        if step == 4:
            cities = [c.strip() for c in message.split(",")]
            collected_data["preferred_cities"] = cities
            collected_data["onboarding_step"] = 5
            
            return "What's your current CTC and target salary?\n\ne.g., '14 LPA, looking for 20-25 LPA'"

        # Step 5: Store salary, ask for resume
        if step == 5:
            collected_data["current_ctc"] = message
            collected_data["onboarding_step"] = 6
            
            return (
                "Great! Now please send me your resume as a PDF.\n\n"
                "This is the only file I'll ever ask for - I'll use it to apply to jobs for you."
            )

        # Step 6: Store resume, complete onboarding
        if step == 6:
            # Resume would be handled via document upload
            collected_data["onboarding_completed"] = True
            collected_data["onboarding_step"] = 0
            
            skills = collected_data.get("skills", [])
            skills_text = ", ".join(skills) if skills else "I'll extract them from your resume"
            
            return (
                f"Perfect! Your profile is set up:\n\n"
                f"🎯 Role: {collected_data.get('target_role')}\n"
                f"📍 Locations: {', '.join(collected_data.get('preferred_cities', []))}\n"
                f"💰 Target: {collected_data.get('current_ctc')}\n"
                f"🛠️ Skills: {skills_text}\n\n"
                "Your first job matches will arrive tomorrow at 8 AM!\n\n"
                "Reply 'jobs' anytime to get matches now, or 'help' for options."
            )

        return "Let's continue your profile setup. What would you like to update?"

    async def handle_job_drop(
        self,
        message: str,
        collected_data: Dict,
        history: List[Dict],
        entities: Dict
    ) -> str:
        """Handle job request and job drop display"""
        
        # This would fetch jobs from database and display them
        # Placeholder for now
        return (
            "🔍 Finding your perfect job matches...\n\n"
            "Here are today's top recommendations:\n\n"
            "1. *Senior Backend Engineer* at Razorpay\n"
            "   📍 Bangalore (Remote OK) | 💰 20-26 LPA\n"
            "   🎯 94% match - Your Python + Kafka skills match!\n\n"
            "2. *Backend Engineer* at Cred\n"
            "   📍 Bangalore | 💰 18-22 LPA\n"
            "   🎯 89% match\n\n"
            "3. *SDE-2* at Meesho\n"
            "   📍 Bangalore | 💰 18-24 LPA\n"
            "   🎯 85% match\n\n"
            "Reply with the number to apply (e.g., '1'), or 'more' for more options."
        )

    async def handle_apply(
        self,
        message: str,
        collected_data: Dict,
        history: List[Dict],
        entities: Dict
    ) -> str:
        """Handle job application process"""
        
        job_id = entities.get("job_id") or message.strip()
        
        return (
            f"🚀 Applying to job #{job_id}...\n\n"
            "Optimizing your resume with job-specific keywords...\n"
            "Submitting application...\n\n"
            "✅ Done! Application sent to Razorpay.\n\n"
            "I'll notify you when your resume is viewed!"
        )

    async def handle_status(
        self,
        message: str,
        collected_data: Dict,
        history: List[Dict],
        entities: Dict
    ) -> str:
        """Handle application status queries"""
        
        # Would fetch from database
        return (
            "📋 *Your Application Status*\n\n"
            "1. Razorpay - Senior BE | Status: Resume Viewed 👀\n"
            "2. Cred - Backend | Status: Applied ✅\n"
            "3. Meesho - SDE-2 | Status: Interview Scheduled 🎉\n\n"
            "Reply with the number for details, or 'stats' for weekly summary."
        )

    async def handle_interview_prep(
        self,
        message: str,
        collected_data: Dict,
        history: List[Dict],
        entities: Dict
    ) -> str:
        """Handle interview preparation"""
        
        return (
            "🎯 *Interview Prep*\n\n"
            "Which company are you preparing for?\n\n"
            "1. Razorpay - Typical: System Design + DSA\n"
            "2. Cred - Typical: Low-level + Problem Solving\n"
            "3. PhonePe - Typical: Backend + Scale\n\n"
            "Reply with the company name or number."
        )

    async def handle_offer_analysis(
        self,
        message: str,
        collected_data: Dict,
        history: List[Dict],
        entities: Dict
    ) -> str:
        """Handle job offer analysis"""
        
        return (
            "💰 *Offer Analysis*\n\n"
            "Enter the offer details:\n"
            "- Company name\n"
            "- Fixed salary\n"
            "- Variable/bonus\n"
            "- ESOPs (if any)\n\n"
            "I'll compare against market data and give you negotiation tips!"
        )

    async def handle_intel(
        self,
        message: str,
        collected_data: Dict,
        history: List[Dict],
        entities: Dict
    ) -> str:
        """Handle company/salary intelligence queries"""
        
        company = entities.get("company") or message
        
        return (
            f"🏢 *Intel on {company}*\n\n"
            "💰 Median SDE-2: 23.5 LPA\n"
            "📈 Growth: Series C\n"
            "👥 Reviews: 4.2/5 (Glassdoor)\n"
            "⏱️ Interview Process: 4 rounds\n\n"
            "Want me to generate a reach-out script for their recruiter?"
        )

    async def handle_profile_update(
        self,
        message: str,
        collected_data: Dict,
        history: List[Dict],
        entities: Dict
    ) -> str:
        """Handle profile update requests"""
        
        return (
            "✏️ *Update Your Profile*\n\n"
            "What would you like to update?\n\n"
            "1. Target role\n"
            "2. Preferred cities\n"
            "3. Skills\n"
            "4. Salary expectations\n"
            "5. Resume\n\n"
            "Reply with the number or tell me what to change."
        )

    async def handle_help(
        self,
        message: str,
        collected_data: Dict,
        history: List[Dict],
        entities: Dict
    ) -> str:
        """Handle help requests"""
        
        return (
            "ℹ️ *Jobsy Commands*\n\n"
            "• jobs - Get job recommendations\n"
            "• apply - Apply to a job\n"
            "• status - Check application status\n"
            "• prep - Interview preparation\n"
            "• offer - Analyze a job offer\n"
            "• intel - Company/salary research\n"
            "• profile - Update your profile\n"
            "• pause - Pause auto-applications\n"
            "• resume - Get your current resume\n\n"
            "Or just ask me anything!"
        )

    async def handle_unknown(
        self,
        message: str,
        collected_data: Dict,
        history: List[Dict],
        entities: Dict
    ) -> str:
        """Handle unrecognized messages"""
        
        return (
            "I'm not sure I understood that. 🤔\n\n"
            "Try these commands:\n"
            "• 'jobs' - Get job recommendations\n"
            "• 'status' - Check your applications\n"
            "• 'help' - See all options\n\n"
            "Or tell me what you need in simple words!"
        )

    async def get_or_create_state(self, user_id: str) -> ConversationState:
        """Get or create conversation state for user"""
        
        from sqlalchemy import select
        
        result = await self.db.execute(
            select(ConversationState).where(ConversationState.user_id == user_id)
        )
        state = result.scalar_one_or_none()
        
        if not state:
            # Create new user if doesn't exist
            from sqlalchemy import insert
            from app.models.database import User
            
            # Check if user exists
            user_result = await self.db.execute(
                select(User).where(User.id == user_id)
            )
            user = user_result.scalar_one_or_none()
            
            if not user:
                # Would need phone number from WhatsApp
                user = User(phone=f"whatsapp_{user_id[:8]}")
                self.db.add(user)
                await self.db.commit()
            
            state = ConversationState(user_id=user_id)
            self.db.add(state)
            await self.db.commit()
            await self.db.refresh(state)
        
        return state

    async def update_state(self, state: ConversationState, intent_result: Dict):
        """Update conversation state after processing"""
        
        state.last_intent = intent_result.get("intent")
        
        await self.db.commit()
        await self.db.refresh(state)

    async def get_recent_history(self, user_id: str, limit: int = 5) -> List[Dict]:
        """Get recent message history for context"""
        
        from sqlalchemy import select, desc
        from app.models.database import MessageLog
        
        result = await self.db.execute(
            select(MessageLog)
            .where(MessageLog.user_id == user_id)
            .order_by(desc(MessageLog.created_at))
            .limit(limit)
        )
        
        logs = result.scalars().all()
        return [{"role": log.direction, "content": log.message_text} for log in reversed(logs)]

    async def log_message(
        self,
        user_id: str,
        direction: str,
        text: str,
        intent: Optional[str] = None
    ):
        """Log message to database"""
        
        from app.models.database import MessageLog
        
        log = MessageLog(
            user_id=user_id,
            direction=direction,
            message_text=text,
            intent=intent
        )
        
        self.db.add(log)
        await self.db.commit()


async def process_user_message(
    db: AsyncSession,
    user_id: str,
    message: str,
    message_type: str = "text",
    metadata: Optional[Dict] = None
) -> str:
    """Entry point for processing user messages"""
    
    engine = ConversationEngine(db)
    return await engine.process_message(user_id, message, message_type, metadata)