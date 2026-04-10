import asyncio
import json
from typing import Dict, List, Optional
from datetime import datetime
from loguru import logger


JOB_ALERT_KEYWORDS = {
    "software_engineer": ["software engineer", "software developer", "full stack", "backend", "frontend", "web developer"],
    "data_science": ["data scientist", "data analyst", "machine learning", "ml engineer", "ai engineer"],
    "devops": ["devops", "sre", "site reliability", "cloud engineer", "infrastructure"],
    "product": ["product manager", "product owner", "program manager"],
    "leadership": ["staff engineer", "principal engineer", "engineering manager", "director"]
}


JOB_ALERT_SOURCES = {
    "linkedin": {"enabled": True, "priority": "high"},
    "indeed": {"enabled": True, "priority": "medium"},
    "glassdoor": {"enabled": False, "priority": "low"},
    "custom": {"enabled": True, "priority": "custom"}
}


class JobAlertService:
    
    def __init__(self):
        self.alerts: Dict[str, List[dict]] = {}
        self.keywords = JOB_ALERT_KEYWORDS
        self.sources = JOB_ALERT_SOURCES
        self.notification_queue: List[dict] = []
    
    def create_alert(
        self,
        user_id: str,
        phone: str,
        keywords: List[str],
        locations: List[str] = [],
        salary_min: Optional[int] = None,
        remote_only: bool = False,
        companies: List[str] = [],
        alert_type: str = "immediate"
    ) -> Dict:
        
        alert_id = f"alert_{user_id}_{datetime.now().timestamp()}"
        
        alert = {
            "id": alert_id,
            "user_id": user_id,
            "phone": phone,
            "keywords": keywords,
            "locations": locations,
            "salary_min": salary_min,
            "remote_only": remote_only,
            "companies": companies,
            "alert_type": alert_type,
            "frequency": "immediate" if alert_type == "immediate" else "daily" if alert_type == "daily" else "weekly",
            "created_at": datetime.now().isoformat(),
            "status": "active",
            "matches_count": 0,
            "last_notified": None
        }
        
        if user_id not in self.alerts:
            self.alerts[user_id] = []
        self.alerts[user_id].append(alert)
        
        return {
            "alert_id": alert_id,
            "status": "active",
            "keywords": keywords,
            "frequency": alert["frequency"],
            "match_count": 0
        }
    
    def update_alert(
        self,
        user_id: str,
        alert_id: str,
        updates: Dict
    ) -> bool:
        
        if user_id not in self.alerts:
            return False
        
        for alert in self.alerts[user_id]:
            if alert["id"] == alert_id:
                for key, value in updates.items():
                    if key in alert:
                        alert[key] = value
                return True
        return False
    
    def delete_alert(self, user_id: str, alert_id: str) -> bool:
        
        if user_id not in self.alerts:
            return False
        
        self.alerts[user_id] = [a for a in self.alerts[user_id] if a["id"] != alert_id]
        return True
    
    def get_alerts(self, user_id: str) -> List[Dict]:
        
        return self.alerts.get(user_id, [])
    
    def check_job_match(self, job: Dict, alert: Dict) -> bool:
        
        job_title = job.get("title", "").lower()
        job_description = job.get("description", "").lower()
        job_company = job.get("company", "").lower()
        
        keyword_match = False
        for keyword in alert.get("keywords", []):
            keyword_lower = keyword.lower()
            if keyword_lower in job_title or keyword_lower in job_description:
                keyword_match = True
                break
        
        if not keyword_match:
            return False
        
        if alert.get("remote_only") and not job.get("remote", False):
            return False
        
        if alert.get("salary_min"):
            job_salary = job.get("salary", 0)
            if job_salary < alert["salary_min"]:
                return False
        
        if alert.get("companies"):
            company_match = False
            for company in alert["companies"]:
                if company.lower() in job_company:
                    company_match = True
                    break
            if not company_match:
                return False
        
        if alert.get("locations"):
            location_match = False
            job_location = job.get("location", "").lower()
            for location in alert["locations"]:
                if location.lower() in job_location:
                    location_match = True
                    break
            if not location_match and alert.get("locations"):
                return False
        
        return True
    
    def match_jobs(self, user_id: str, jobs: List[Dict]) -> Dict:
        
        alerts = self.get_alerts(user_id)
        matches = {}
        
        for alert in alerts:
            alert_matches = []
            for job in jobs:
                if self.check_job_match(job, alert):
                    alert_matches.append({
                        "job_id": job.get("id"),
                        "title": job.get("title"),
                        "company": job.get("company"),
                        "location": job.get("location"),
                        "salary": job.get("salary"),
                        "url": job.get("url")
                    })
            
            matches[alert["id"]] = alert_matches
            alert["matches_count"] = len(alert_matches)
        
        return matches
    
    def format_whatsapp_notification(self, job: Dict) -> str:
        
        message = f"🔔 *New Job Alert!*\n\n"
        message += f"*{job.get('title', 'Position')}*\n"
        message += f"🏢 {job.get('company', 'Company')}\n"
        
        if job.get("location"):
            message += f"📍 {job['location']}\n"
        
        if job.get("salary"):
            message += f"💰 {job['salary']}\n"
        
        if job.get("url"):
            message += f"\n[View Job]({job['url']})"
        
        return message
    
    def queue_notification(
        self,
        user_id: str,
        phone: str,
        jobs: List[Dict],
        alert_id: str
    ) -> Dict:
        
        notification = {
            "id": f"notif_{datetime.now().timestamp()}",
            "user_id": user_id,
            "phone": phone,
            "alert_id": alert_id,
            "jobs": jobs,
            "created_at": datetime.now().isoformat(),
            "status": "pending"
        }
        
        self.notification_queue.append(notification)
        
        return {
            "notification_id": notification["id"],
            "jobs_count": len(jobs),
            "status": "queued"
        }
    
    def get_pending_notifications(self) -> List[Dict]:
        
        return [n for n in self.notification_queue if n["status"] == "pending"]
    
    def mark_notification_sent(self, notification_id: str) -> bool:
        
        for notif in self.notification_queue:
            if notif["id"] == notification_id:
                notif["status"] = "sent"
                notif["sent_at"] = datetime.now().isoformat()
                return True
        return False
    
    def get_notification_history(self, user_id: str, limit: int = 10) -> List[Dict]:
        
        user_notifs = [n for n in self.notification_queue if n["user_id"] == user_id]
        return sorted(user_notifs, key=lambda x: x["created_at"], reverse=True)[:limit]


job_alert_service = JobAlertService()