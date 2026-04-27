from datetime import datetime, timezone


def format_timestamp(dt: datetime) -> str:
    """
    Return a human-readable relative time string (e.g. '2 days ago').

    Example outputs:
    - "just now" (0-59 seconds)
    - "5 minutes ago" (1-59 minutes)
    - "3 hours ago" (1-23 hours)
    - "10 days ago" (1-29 days)

    Args:
        dt: The datetime to format. Should be timezone-aware or UTC.

    Returns:
        str: A human-readable relative time string.
    """
    if dt is None:
        return ""
    try:
        now = datetime.now(timezone.utc)
        if not dt.tzinfo:
            dt = dt.replace(tzinfo=timezone.utc)
        secs = int((now - dt).total_seconds())
        if secs < 60:
            return "just now"
        mins = secs // 60
        if mins < 60:
            return f"{mins} minute{'s' if mins != 1 else ''} ago"
        hrs = mins // 60
        if hrs < 24:
            return f"{hrs} hour{'s' if hrs != 1 else ''} ago"
        days = hrs // 24
        if days < 30:
            return f"{days} day{'s' if days != 1 else ''} ago"
        months = days // 30
        if months < 12:
            return f"{months} month{'s' if months != 1 else ''} ago"
        years = months // 12
        return f"{years} year{'s' if years != 1 else ''} ago"
    except Exception:
        return str(dt)
