from app.controllers.notification_controller import NotificationController
from app.presentation.views.notifications.helpers.data.state import NotificationState


def load_notifications(state: NotificationState):
    """Seed DB types and load unread enriched notifications into *state*.

    Calls ``ensure_types_seeded`` so existing databases automatically gain
    notification types that were added after the initial setup.

    Args:
        state: The ``NotificationState`` instance to populate with notifications and types.
    """
    NotificationController.ensure_types_seeded()
    state.notifications = NotificationController.get_enriched(unread_only=True)
    types = NotificationController.get_types()
    state.notification_types = {t["id"]: t for t in types}
