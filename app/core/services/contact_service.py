import re

from app.core.db.engine import SessionLocal
from app.core.db.models.contact import ContactModel
from app.core.db.models.user import UserModel
from app.utils.log_utils import log_exception, log_operation


class ContactService:
    """
    Service class for contact-message business logic.

    Business rules:
    - Contacts are enriched with the author's username for display.
    - Only admins may resolve (delete) contact messages; enforcement is the
      caller's responsibility (validated at the controller layer via session).
    """

    @staticmethod
    def get_all_enriched() -> list:
        """
        Retrieve all contact messages enriched with the author's username.

        Each returned dict includes: ``id``, ``title``, ``message``,
        ``userId``, and ``username`` for direct use by the view layer.

        Returns:
            list: Enriched contact dicts, ordered by insertion (DB default).
        """
        try:
            with SessionLocal() as session:
                contacts = ContactModel.get_all(session)
                result = []
                for c in contacts:
                    user = UserModel.get_by_id(session, c["userId"])
                    username = user["username"] if user else "Unknown"
                    result.append(
                        {
                            "id": c["id"],
                            "title": c["title"],
                            "message": c["message"],
                            "userId": c["userId"],
                            "username": username,
                            "createdAt": c.get("createdAt"),
                        }
                    )
                return result
        except Exception as e:
            log_exception("contact.get_all_enriched", e)
            return []

    @staticmethod
    def resolve_contact(contact_id: int) -> bool:
        """
        Delete (resolve) a contact message by ID.

        Args:
            contact_id: Primary key of the contact message to delete.

        Returns:
            bool: True if deleted, False if the record was not found.
        """
        try:
            with SessionLocal() as session:
                result = ContactModel.delete_by_id(session, contact_id)
                session.commit()
            if result:
                log_operation(
                    "contact.resolve_contact",
                    "success",
                    f"Resolved contact {contact_id}",
                )
            else:
                log_operation(
                    "contact.resolve_contact",
                    "validation_error",
                    f"Contact {contact_id} not found",
                )
            return result
        except Exception as e:
            log_exception(
                "contact.resolve_contact", e, context={"contact_id": contact_id}
            )
            return False

    @staticmethod
    def create_contact(title: str, message: str, user_id: int) -> bool:
        """
        Create a new contact message from a user.

        Business rules enforced here:
        - Title must contain only letters (A–Z, a–z) — no spaces, digits, or
          special characters.
        - Title must not exceed 75 characters.
        - Message body must not exceed 255 characters.
        - Title must be unique (case-insensitive) — checked via
          ``ContactModel.title_exists`` before attempting the insert.

        Args:
            title: Subject of the message (should already be stripped).
            message: Body of the message (should already be stripped).
            user_id: Primary key of the submitting user.

        Returns:
            bool: True on success.

        Raises:
            ValueError: If any business rule is violated.
        """
        if not re.fullmatch(r"[A-Za-z]+", title):
            raise ValueError(
                "Title must contain only letters (A-Z, a-z) with no spaces "
                "or special characters."
            )
        if len(title) > 75:
            raise ValueError("Title too long (max 75 characters).")
        if len(message) > 255:
            raise ValueError("Message too long (max 255 characters).")

        try:
            with SessionLocal() as session:
                if ContactModel.title_exists(session, title):
                    raise ValueError("A message with this title already exists.")
                ContactModel.create(
                    session, title=title, message=message, userId=user_id
                )
                session.commit()
            log_operation(
                "contact.create_contact",
                "success",
                f"Contact created by user {user_id}",
                user_id=user_id,
            )
            return True
        except ValueError:
            raise
        except Exception as e:
            log_exception(
                "contact.create_contact",
                e,
                context={"user_id": user_id},
            )
            raise
