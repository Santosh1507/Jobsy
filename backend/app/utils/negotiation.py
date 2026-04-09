# Negotiation scripts and frameworks from career-ops

NEGOTIATION_SCRIPTS = {
    "initial_response": {
        "template": """Thank you so much for the offer! I'm really excited about the opportunity to join {company} and contribute to the team.

I'm currently reviewing the details and will get back to you by {date}.""",
        "timing": "Within 24 hours",
        "do": ["Express genuine enthusiasm", "Request time to review"],
        "dont": ["Give a final answer immediately", "Discuss salary in first response"]
    },
    
    "salary_negotiation": {
        "template": """Thank you for the offer. Based on my experience with {skills} and market research for this role, I was hoping we could explore {target_salary} on the fixed component.

I understand {company} has great products and I'm very interested in joining. Is there any flexibility there?""",
        "leverage": [
            "Market data showing {market_median} median",
            "Competing offers if available",
            "Unique skills or experience",
            "Current notice period"
        ],
        "tips": [
            "Let them respond first",
            "Be specific with numbers",
            "Stay positive and collaborative"
        ]
    },
    
    "counter_offer": {
        "template": """Thank you for the updated offer. I appreciate {company} working with me on this.

Based on the current state, I was hoping for a bit more. Specifically, {specific_request}.

Would it be possible to explore this further? I'm very excited about joining and want to make this work.""",
        "when_to_use": "After initial negotiation response"
    },
    
    "accepting": {
        "template": """Thank you so much! I'm thrilled to accept the offer and excited to join {company}.

I'm available to start on {start_date} and looking forward to meeting the team.

Please let me know if there's any paperwork or next steps I should be aware of.""",
        "tips": ["Get everything in writing", "Don't burn bridges with other companies"]
    }
}


GEOGRAPHIC_DISCOUNTS = {
    "common_pushbacks": [
        {
            "issue": "Based in lower cost of living area",
            "response": "My current location is temporary and I'm open to relocating. More importantly, my skills are valued at {market_rate} regardless of location, as shown by remote-first companies hiring at that rate."
        },
        {
            "issue": "Less experience than other candidates",
            "response": "I'd be happy to discuss specific projects and outcomes that demonstrate my capabilities. My track record of {specific_achievements} shows I deliver results quickly."
        }
    ]
}


def generate_negotiation_script(
    offer_data: dict,
    market_data: dict = None
) -> dict:
    """Generate personalized negotiation script"""
    
    company = offer_data.get("company", "the company")
    offered = offer_data.get("offered_salary", 0)
    target = offer_data.get("target_salary", offered * 1.15)
    skills = offer_data.get("skills", [])
    
    script = {
        "initial_response": NEGOTIATION_SCRIPTS["initial_response"]["template"].format(
            company=company,
            date="end of week"
        ),
        "salary_negotiation": NEGOTIATION_SCRIPTS["salary_negotiation"]["template"].format(
            company=company,
            skills=", ".join(skills[:3]),
            target_salary=f"₹{target/100000:.0f}L" if target else "higher"
        ),
        "market_context": {
            "offered": offered,
            "target": target,
            "market_median": market_data.get("median", 0) if market_data else 0,
            "leverage": _get_leverage_points(offer_data, market_data)
        }
    }
    
    return script


def _get_leverage_points(offer_data: dict, market_data: dict = None) -> list:
    """Get leverage points for negotiation"""
    
    leverage = []
    
    if offer_data.get("competing_offers"):
        leverage.append("Multiple competing offers")
    
    if offer_data.get("notice_period"):
        leverage.append(f"{offer_data.get('notice_period')} month notice period")
    
    if market_data:
        leverage.append(f"Market median is ₹{market_data.get('median', 0)/100000}L")
        leverage.append(f"Range: ₹{market_data.get('min', 0)/100000}L - ₹{market_data.get('max', 0)/100000}L")
    
    if offer_data.get("unique_skills"):
        leverage.append(f"In-demand: {', '.join(offer_data.get('unique_skills', [])[:2])}")
    
    return leverage


def get_decline_template(company: str) -> str:
    """Template for declining an offer professionally"""
    
    return f"""Thank you so much for the opportunity to join {company}. After careful consideration, I've decided to pursue another opportunity that better aligns with my current career goals.

I genuinely appreciate the time you and your team invested in me throughout the process, and I hope our paths may cross again in the future.

Wishing {company} continued success."""