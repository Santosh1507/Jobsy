# Application States - Career-ops canonical states
# Used for tracking application status across the platform

APPLICATION_STATES = {
    "evaluated": {
        "label": "Evaluated",
        "description": "Offer evaluated with report, pending decision",
        "dashboard_group": "evaluated"
    },
    "applied": {
        "label": "Applied",
        "description": "Application submitted",
        "dashboard_group": "applied"
    },
    "responded": {
        "label": "Responded",
        "description": "Company has responded (not yet interview)",
        "dashboard_group": "responded"
    },
    "interview": {
        "label": "Interview",
        "description": "Active interview process",
        "dashboard_group": "interview"
    },
    "offer": {
        "label": "Offer",
        "description": "Offer received",
        "dashboard_group": "offer"
    },
    "rejected": {
        "label": "Rejected",
        "description": "Rejected by company",
        "dashboard_group": "rejected"
    },
    "discarded": {
        "label": "Discarded",
        "description": "Discarded by candidate or offer closed",
        "dashboard_group": "discarded"
    },
    "skip": {
        "label": "SKIP",
        "description": "Doesn't fit, don't apply",
        "dashboard_group": "skip"
    }
}

# State aliases for different languages
STATE_ALIASES = {
    "evaluated": ["evaluada", "evaluated"],
    "applied": ["aplicado", "enviada", "aplicada", "sent", "applied"],
    "responded": ["respondido", "responded"],
    "interview": ["entrevista", "interview"],
    "offer": ["oferta", "offer"],
    "rejected": ["rechazado", "rechazada", "rejected"],
    "discarded": ["descartado", "descartada", "cerrada", "cancelada", "discarded"],
    "skip": ["no_aplicar", "no aplicar", "skip", "monitor", "skip"]
}


def get_state_label(state_id: str) -> str:
    """Get label for state"""
    return APPLICATION_STATES.get(state_id, {}).get("label", state_id)


def get_dashboard_group(state_id: str) -> str:
    """Get dashboard group for state"""
    return APPLICATION_STATES.get(state_id, {}).get("dashboard_group", "other")


def normalize_state(state_input: str) -> str:
    """Normalize state input to canonical state ID"""
    state_lower = state_input.lower().strip()
    
    # Direct match
    if state_lower in APPLICATION_STATES:
        return state_lower
    
    # Check aliases
    for state_id, aliases in STATE_ALIASES.items():
        if state_lower in aliases:
            return state_id
    
    # Default to applied if not found
    return "applied"