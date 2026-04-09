from typing import Dict, List, Optional, Any
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from loguru import logger

from app.models.database import SalaryData


class InsiderIntelService:
    """Service for salary intelligence and company insights"""
    
    def __init__(self):
        self.cache = {}
    
    async def get_salary_data(
        self,
        company: str,
        role: str,
        db: AsyncSession,
        level: Optional[str] = None,
        city: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """Get salary data for company/role from database"""
        
        # Build query
        query = select(SalaryData).where(
            SalaryData.company.ilike(f"%{company}%"),
            SalaryData.role.ilike(f"%{role}%")
        )
        
        if level:
            query = query.where(SalaryData.level == level)
        if city:
            query = query.where(SalaryData.city == city)
        
        result = await self.db.execute(query)
        salary_record = result.scalar_one_or_none()
        
        if salary_record:
            return {
                "company": salary_record.company,
                "role": salary_record.role,
                "level": salary_record.level,
                "city": salary_record.city,
                "salary_min": salary_record.salary_min,
                "salary_max": salary_record.salary_max,
                "median": salary_record.median_salary,
                "sample_size": salary_record.sample_size,
                "source": salary_record.source
            }
        
        return None
    
    async def get_market_range(
        self,
        role: str,
        db: AsyncSession,
        level: str = "SDE-2",
        city: str = "Bangalore"
    ) -> Dict[str, Any]:
        """Get market salary range for a role"""
        
        result = await self.db.execute(
            select(
                func.avg(SalaryData.median_salary).label("avg_median"),
                func.min(SalaryData.salary_min).label("min_salary"),
                func.max(SalaryData.salary_max).label("max_salary"),
                func.count(SalaryData.id).label("count")
            )
            .where(SalaryData.role.ilike(f"%{role}%"))
            .where(SalaryData.level == level)
        )
        
        row = result.first()
        
        if row and row.count > 0:
            return {
                "role": role,
                "level": level,
                "city": city,
                "avg_median": int(row.avg_median),
                "min_salary": int(row.min_salary),
                "max_salary": int(row.max_salary),
                "companies_count": row.count,
                "recommendation": self.get_salary_recommendation(row.avg_median)
            }
        
        return {
            "role": role,
            "level": level,
            "city": city,
            "message": "No market data available"
        }
    
    def get_salary_recommendation(self, median: int) -> str:
        """Get salary recommendation based on median"""
        
        if median < 1500000:
            return "Entry-level range - negotiate for 10-15% above"
        elif median < 2500000:
            return "Mid-level range - target 20-25% above median"
        elif median < 4000000:
            return "Senior range - strong negotiation position"
        else:
            return "Leadership range - leverage competing offers"
    
    async def analyze_offer(
        self,
        offer_data: Dict,
        db: AsyncSession
    ) -> Dict[str, Any]:
        """Analyze a job offer against market data"""
        
        company = offer_data.get("company", "")
        role = offer_data.get("role", "")
        fixed_salary = offer_data.get("fixed_salary", 0)
        variable = offer_data.get("variable", 0)
        esops = offer_data.get("esops", 0)
        
        # Get market data
        salary_data = await self.get_salary_data(company, role)
        
        total_comp = fixed_salary + variable
        
        if salary_data:
            median = salary_data.get("median", 0)
            market_min = salary_data.get("salary_min", 0)
            market_max = salary_data.get("salary_max", 0)
            
            # Calculate position
            if median > 0:
                percentile = ((total_comp - market_min) / (market_max - market_min)) * 100 if market_max > market_min else 50
                percentile = min(100, max(0, percentile))
                
                if percentile < 25:
                    recommendation = "reject"
                    reason = "Below market - negotiate hard or decline"
                elif percentile < 50:
                    recommendation = "negotiate"
                    reason = "Below market - negotiate for 15-20% increase"
                elif percentile < 75:
                    recommendation = "accept"
                    reason = "At market - can negotiate small improvement"
                else:
                    recommendation = "accept"
                    reason = "Above market - strong offer"
            else:
                percentile = 50
                recommendation = "review"
                reason = "Limited market data"
        else:
            percentile = 50
            recommendation = "review"
            reason = "No market data available - research independently"
        
        # Negotiation strategy
        negotiation = await self.generate_negotiation_strategy(
            offer_data, salary_data, recommendation
        )
        
        return {
            "company": company,
            "role": role,
            "offered": {
                "fixed": fixed_salary,
                "variable": variable,
                "total": total_comp,
                "esops": esops
            },
            "market": {
                "median": salary_data.get("median") if salary_data else None,
                "range": f"{salary_data.get('salary_min') if salary_data else '?'} - {salary_data.get('salary_max') if salary_data else '?'}"
            } if salary_data else None,
            "percentile": f"{percentile:.0f}%",
            "recommendation": recommendation,
            "reason": reason,
            "negotiation": negotiation,
            "leverage_points": self.get_leverage_points(offer_data, salary_data)
        }
    
    async def generate_negotiation_strategy(
        self,
        offer_data: Dict,
        market_data: Optional[Dict],
        recommendation: str
    ) -> Dict[str, Any]:
        """Generate negotiation strategy"""
        
        strategy = {
            "primary_approach": "",
            "script": "",
            "timing": "",
            "leverage": []
        }
        
        if recommendation == "negotiate" or recommendation == "accept":
            strategy["primary_approach"] = "Professional but firm"
            
            strategy["script"] = (
                f"Thank you for the offer. Based on my experience with "
                f"{', '.join(offer_data.get('skills', [])[:3])} and market research, "
                f"I was hoping we could explore {int(offer_data.get('fixed_salary', 0) * 1.15 / 100000) * 100000 // 100000 * 100000 // 100000}L on the fixed component. "
                f"Is there any flexibility there?"
            )
            
            strategy["timing"] = "Wait 24-48 hours before responding"
            
            if market_data and market_data.get("median"):
                strategy["leverage"] = [
                    f"Market median is {market_data.get('median')/100000}L",
                    f"Range seen: {market_data.get('salary_min')/100000}-{market_data.get('salary_max')/100000}L",
                    "Express enthusiasm but don't commit immediately"
                ]
        
        return strategy
    
    def get_leverage_points(
        self,
        offer_data: Dict,
        market_data: Optional[Dict]
    ) -> List[str]:
        """Get leverage points for negotiation"""
        
        leverage = []
        
        # Add common leverage points
        if offer_data.get("competing_offers"):
            leverage.append("Multiple competing offers (if applicable)")
        
        if offer_data.get("notice_period"):
            leverage.append(f"{offer_data.get('notice_period')} month notice period")
        
        if offer_data.get("skills"):
            leverage.append(f"In-demand skills: {', '.join(offer_data.get('skills', [])[:3])}")
        
        # Market-based leverage
        if market_data:
            leverage.append(f"Market data shows {market_data.get('median', 0)/100000}L median")
        
        return leverage
    
    async def get_company_insights(
        self,
        company: str
    ) -> Dict[str, Any]:
        """Get company culture and insights"""
        
        # This would use scraped data from Glassdoor, AmbitionBox, etc.
        # Placeholder for now
        
        insights = {
            "company": company,
            "ratings": {
                "overall": 4.0,
                "work_life": 3.5,
                "salary": 3.8,
                "career_growth": 3.5
            },
            "pros": [
                "Fast growth opportunities",
                "Good work culture"
            ],
            "cons": [
                "Can be high pressure",
                "Work-life balance varies by team"
            ],
            "interview_tips": [
                "Prepare for system design",
                "Focus on problem-solving approach"
            ],
            "note": "Based on community reports - individual experiences may vary"
        }
        
        return insights


# Singleton instance
insider_intel_service = InsiderIntelService()