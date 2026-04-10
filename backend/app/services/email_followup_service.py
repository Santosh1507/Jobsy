import asyncio
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from loguru import logger


FOLLOW_UP_TEMPLATES = {
    "initial_followup": {
        "subject": "Following up on my application for {role}",
        "body": """
Hi {recruiter_name},

I hope this email finds you well. I wanted to follow up on my application for the {role} position at {company}.

I remain very excited about this opportunity and would love to learn more about the role and your team.

Please let me know if you need any additional information from me.

Thank you for your time and consideration.

Best regards,
{name}
""",
        "send_after_days": 5,
        "max_followups": 2
    },
    "interview_followup": {
        "subject": "Thank you for the interview - {role}",
        "body": """
Hi {recruiter_name},

Thank you for taking the time to speak with me today about the {role} position. I really enjoyed learning more about the role and your team at {company}.

Our conversation reinforced my enthusiasm for the position. I was particularly excited to hear about {specific_topic_1} and {specific_topic_2}.

Please let me know if there's anything else I can provide to help with your decision-making process.

Looking forward to hearing from you.

Best regards,
{name}
""",
        "send_after_days": 1,
        "max_followups": 1
    },
    "second_followup": {
        "subject": "Checking in - {role} position",
        "body": """
Hi {recruiter_name},

I wanted to check in again on the {role} position. I understand that hiring processes take time, and I remain very interested in this opportunity.

If there are any updates you can share, I would appreciate the chance to hear from you.

Thank you again for your consideration.

Best regards,
{name}
""",
        "send_after_days": 7,
        "max_followups": 1
    },
    "offer_followup": {
        "subject": "Excited about the offer - {role}",
        "body": """
Hi {recruiter_name},

Thank you for extending the offer! I'm very excited about the opportunity to join {company} as {role}.

I wanted to confirm that I've received all the details and will review them promptly. Please let me know if you need any additional information from me.

I'm looking forward to starting this new chapter with your team.

Best regards,
{name}
""",
        "send_after_days": 1,
        "max_followups": 0
    }
}


class EmailFollowUpService:
    
    def __init__(self):
        self.templates = FOLLOW_UP_TEMPLATES
        self.followups: Dict[str, List[dict]] = {}
    
    def create_followup(
        self,
        user_id: str,
        application_id: str,
        template_type: str,
        company: str,
        role: str,
        recruiter_name: Optional[str] = None,
        custom_fields: Optional[Dict] = None
    ) -> Dict:
        
        template = self.templates.get(template_type, self.templates["initial_followup"])
        
        if not recruiter_name:
            recruiter_name = "Hiring Manager"
        
        custom = custom_fields or {}
        
        subject = template["subject"].format(
            role=role,
            company=company,
            recruiter_name=recruiter_name
        )
        
        body = template["body"].format(
            recruiter_name=recruiter_name,
            role=role,
            company=company,
            name=custom.get("name", "Your Name"),
            specific_topic_1=custom.get("specific_topic_1", "the team's technical approach"),
            specific_topic_2=custom.get("specific_topic_2", "the company's growth plans")
        )
        
        followup_id = f"fu_{user_id}_{application_id}_{template_type}_{datetime.now().timestamp()}"
        
        followup = {
            "id": followup_id,
            "user_id": user_id,
            "application_id": application_id,
            "template_type": template_type,
            "company": company,
            "role": role,
            "recruiter_email": custom.get("recruiter_email"),
            "recruiter_name": recruiter_name,
            "subject": subject,
            "body": body,
            "scheduled_date": datetime.now() + timedelta(days=template["send_after_days"]),
            "status": "scheduled",
            "max_followups": template["max_followups"],
            "send_count": 0
        }
        
        key = f"{user_id}_{application_id}"
        if key not in self.followups:
            self.followups[key] = []
        self.followups[key].append(followup)
        
        return {
            "followup_id": followup_id,
            "template_type": template_type,
            "scheduled_date": followup["scheduled_date"].isoformat(),
            "subject": subject,
            "preview": body[:200] + "..."
        }
    
    def get_scheduled_followups(self, user_id: str) -> List[Dict]:
        
        result = []
        for key, followups in self.followups.items():
            if key.startswith(user_id):
                for fu in followups:
                    if fu["status"] == "scheduled":
                        result.append({
                            "id": fu["id"],
                            "company": fu["company"],
                            "role": fu["role"],
                            "template_type": fu["template_type"],
                            "scheduled_date": fu["scheduled_date"].isoformat()
                        })
        return result
    
    def mark_sent(self, followup_id: str) -> bool:
        
        for key, followups in self.followups.items():
            for fu in followups:
                if fu["id"] == followup_id:
                    fu["status"] = "sent"
                    fu["sent_date"] = datetime.now()
                    fu["send_count"] += 1
                    return True
        return False
    
    def cancel_followup(self, followup_id: str) -> bool:
        
        for key, followups in self.followups.items():
            for fu in followups:
                if fu["id"] == followup_id:
                    fu["status"] = "cancelled"
                    return True
        return False
    
    def get_template_preview(self, template_type: str, company: str = "Company", role: str = "Role") -> Dict:
        
        template = self.templates.get(template_type, self.templates["initial_followup"])
        
        return {
            "template_type": template_type,
            "subject": template["subject"].format(role=role, company=company),
            "body": template["body"],
            "send_after_days": template["send_after_days"],
            "max_followups": template["max_followups"]
        }
    
    def list_templates(self) -> List[Dict]:
        
        return [
            {
                "type": key,
                "send_after_days": val["send_after_days"],
                "max_followups": val["max_followups"]
            }
            for key, val in self.templates.items()
        ]


email_followup_service = EmailFollowUpService()