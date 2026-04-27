from typing import List, Optional, Tuple

from app.core.services.comment_service import CommentService
from app.core.state.session import session
from app.utils.log_utils import log_exception


class CommentController:
    """
    Controller for comment operations.

    Coordinates between views and services for:
    - Listing comments for a photo (direct model read — no business logic)
    - Adding a comment to a photo (delegates to service)
    - Deleting a comment (delegates to service)
    """

    @staticmethod
    def get_comments(photo_id: int) -> List[dict]:
        """
        Return all enriched comments for a photo.

        This is a simple read: Controller → Service → Model.

        Args:
            photo_id: The ID of the photo.

        Returns:
            List[dict]: Enriched comment dicts with author info.
        """
        return CommentService.get_comments_for_photo(photo_id)

    @staticmethod
    def add_comment(photo_id: int, text: str) -> Tuple[bool, str, Optional[dict]]:
        """
        Add a comment to a photo as the current session user.

        Args:
            photo_id: The ID of the target photo.
            text: The comment text.

        Returns:
            Tuple[bool, str, Optional[dict]]:
                (success, message, enriched_comment_dict or None)
        """
        user_id = session.user_id
        assert user_id is not None, "User must be authenticated to add a comment"
        try:
            success, message, comment = CommentService.add_comment(
                user_id, photo_id, text
            )
            return success, message, comment
        except Exception as e:
            log_exception("comment.add_comment", e, user_id=user_id)
            return False, "Something went wrong. Please try again later.", None

    @staticmethod
    def delete_comment(comment_id: int) -> Tuple[bool, str]:
        """
        Delete a comment as the current session user.

        Admins can delete any comment; regular users can only delete their own.

        Args:
            comment_id: The ID of the comment to delete.

        Returns:
            Tuple[bool, str]: (success, message)
        """
        user_id = session.user_id
        assert user_id is not None, "User must be authenticated to delete a comment"
        try:
            return CommentService.delete_comment(
                requesting_user_id=user_id,
                comment_id=comment_id,
                is_admin=session.is_admin,
            )
        except Exception as e:
            log_exception("comment.delete_comment", e, user_id=user_id)
            return False, "Something went wrong. Please try again later."
