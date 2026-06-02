from datetime import datetime, timezone


def format_time_ago(dt: object) -> str:
    """Return a human-readable relative time string (e.g. '2h ago').

    Args:
        dt: A ``datetime`` object (or anything else — falls back to ``str``).

    Returns:
        str: Relative time like ``'Just now'``, ``'5m ago'``, ``'3h ago'``, ``'2d ago'``.
    """
    if dt is None:
        return "—"
    if not isinstance(dt, datetime):
        return str(dt)
    now = datetime.now(timezone.utc)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    delta = now - dt
    s = int(delta.total_seconds())
    if s < 60:
        return "Just now"
    if s < 3_600:
        return f"{s // 60}m ago"
    if s < 86_400:
        return f"{s // 3_600}h ago"
    return f"{s // 86_400}d ago"


def format_time_full(dt: object) -> str:
    """Return a full date-time string like ``'29 May 2026  14:35'``.

    Args:
        dt: A ``datetime`` object (or anything else — falls back to ``str``).

    Returns:
        str: Formatted date-time string or ``'—'`` when *dt* is ``None``.
    """
    if dt is None:
        return "—"
    if not isinstance(dt, datetime):
        return str(dt)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.strftime("%d %b %Y  %H:%M")


def format_notification_message(n: dict) -> str:
    """Return a complete message for a notification.

    Concatenates sender username with the stored message.
    For admin notifications, just returns the message as-is.

    Args:
        n: Enriched notification dict (must contain ``message``,
           ``sender_username``, and optionally ``type_key``).

    Returns:
        str: Human-readable message, e.g. ``'alice commented on your photo'``.
    """
    message = n.get("message", "You have a new notification")
    sender = n.get("sender_username", "Unknown")
    type_key = n.get("type_key", "")

    # Admin notifications already include context in the message
    if type_key in ("admin_delete_comment", "admin_delete_photo"):
        return message

    # For user-triggered notifications, prepend sender name
    return f"{sender} {message}"


def notification_row_label(n: dict) -> str:
    """Return the listbox display label for a single notification dict.

    Args:
        n: Enriched notification dict (must contain ``typeId``, ``sender_username``,
           ``type_key``, and optionally ``createdAt``).

    Returns:
        str: Label string in the form ``'  5m ago  ·  alice commented on your photo'``.
    """
    time_str = format_time_ago(n.get("createdAt"))
    message = format_notification_message(n)
    short_msg = message[:50] + "…" if len(message) > 50 else message
    return f"  {time_str}  ·  {short_msg}"
