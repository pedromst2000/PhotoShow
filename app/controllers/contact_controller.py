from typing import Tuple

from app.core.services.contact_service import ContactService
from app.core.state.session import session
from app.utils.log_utils import log_exception, log_operation


class ContactController:
    """
    Controller for contact-message operations.

    Routes:
    - Read (enriched list) → Service (multi-model join required).
    - Resolve (delete)     → Service (business operation with logging).
    """

    @staticmethod
    def get_all_enriched() -> list[dict]:
        """
        Return all contact messages enriched with the author's username.

        Returns:
            list: Dicts with ``id``, ``title``, ``message``, ``userId``,
                  and ``username``.
        """
        return ContactService.get_all_enriched()

    @staticmethod
    def resolve(contact_id: int) -> Tuple[bool, str]:
        """
        Admin-only: mark a contact message as resolved by deleting it.

        Args:
            contact_id: Primary key of the contact message.

        Returns:
            Tuple[bool, str]: (success, human-readable message).
        """
        try:
            if ContactService.resolve_contact(contact_id):
                log_operation(
                    "contact.resolve",
                    "success",
                    f"Contact {contact_id} resolved",
                    user_id=session.user_id,
                )
                return True, "Contact message resolved and removed."
            log_operation(
                "contact.resolve",
                "validation_error",
                f"Contact {contact_id} not found",
                user_id=session.user_id,
            )
            return False, "Contact message not found."
        except Exception as e:
            log_exception(
                "contact.resolve",
                e,
                user_id=session.user_id,
                context={"contact_id": contact_id},
            )
            return False, "Something went wrong. Please try again later."

    @staticmethod
    def create(title: str, message: str) -> Tuple[bool, str]:
        """
        Submit a contact message to the admin from the currently logged-in user.

        The service layer enforces business rules (title uniqueness, message
        length).  No role check is performed here — the UI already restricts
        access to the appropriate users.

        Args:
            title: Subject of the message.
            message: Body of the message.

        Returns:
            Tuple[bool, str]: (success, human-readable message).
        """
        user_id = session.user_id
        if user_id is None:
            log_operation(
                "contact.create",
                "validation_error",
                "Unable to identify user",
            )
            return False, "Unable to identify user."

        title_clean = title.strip()
        message_clean = message.strip()

        try:
            ContactService.create_contact(title_clean, message_clean, user_id)
            log_operation(
                "contact.create",
                "success",
                f"Contact created by user {user_id}",
                user_id=user_id,
            )
            return True, "Your message has been sent to the admin."
        except ValueError as e:
            log_operation(
                "contact.create",
                "validation_error",
                str(e),
                user_id=user_id,
            )
            return False, str(e)
        except Exception as e:
            log_exception(
                "contact.create",
                e,
                user_id=user_id,
                context={"title": title_clean},
            )
            return False, "Something went wrong. Please try again later."
