from datetime import datetime

def get_session_info(session_context=None):
    """Generate session information string"""
    if not session_context:
        return "New session (no prior context)"
    
    info = []
    if "department" in session_context:
        info.append(f"Department: {session_context['department']}")
    if "created_at" in session_context:
        created = datetime.fromisoformat(session_context["created_at"])
        info.append(f"Session started: {created.strftime('%Y-%m-%d %H:%M')}")
    
    return "; ".join(info) if info else "No session details available"