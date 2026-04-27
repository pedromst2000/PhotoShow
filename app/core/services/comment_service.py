from typing import List, Optional, Tuple

from app.core.db.engine import SessionLocal
from app.core.db.models.comment import CommentModel
from app.core.db.models.user import UserModel
from app.utils.log_utils import log_exception, log_operation


class CommentService:
    """
    Service for comment business logic.

    Business rules enforced:
    - Comment text must be non-empty and at most 255 characters.
    - Only the comment author or an admin can delete a comment.
    """

    _MAX_LEN = 255

    @staticmethod
    def get_comments_for_photo(photo_id: int) -> List[dict]:
        """
        Return all comments for a photo, enriched with author username and avatar.

        Args:
            photo_id: The ID of the photo.

        Returns:
            List[dict]: Ordered list of enriched comment dicts (oldest first).

        Raises:
            Exception: Any database error is caught and logged; empty list returned.
        """
        try:
            with SessionLocal() as session:
                comments = CommentModel.get_by_photo(session, photo_id)
                if not comments:
                    return []

                author_ids = list({c["authorId"] for c in comments})
                users = UserModel.get_by_ids(session, author_ids)

            enriched = []
            for c in comments:
                author = users.get(c["authorId"], {})
                enriched.append(
                    {
                        **c,
                        "author_username": author.get("username", "Unknown"),
                        "author_avatar": author.get("avatar"),
                        "author_role": author.get("role", "regular"),
                    }
                )
            log_operation(
                "comment.get_comments_for_photo",
                "success",
                f"Retrieved {len(enriched)} comments for photo {photo_id}",
            )
            return enriched
        except Exception as e:
            log_exception(
                "comment.get_comments_for_photo", e, context={"photo_id": photo_id}
            )
            return []

    @staticmethod
    def add_comment(
        user_id: int, photo_id: int, text: str
    ) -> Tuple[bool, str, Optional[dict]]:
        """
        Add a comment to a photo.

        Business rules:
        - Text must be non-empty after trimming.
        - Text must be at most 255 characters.

        Args:
            user_id: The ID of the commenting user.
            photo_id: The ID of the target photo.
            text: The comment content.

        Returns:
            Tuple[bool, str, Optional[dict]]:
                (success, message, enriched_comment_dict or None)

        Raises:
            Exception: Any database error is caught and logged; (False, msg, None) returned.
        """
        clean = text.strip() if text else ""
        if not clean:
            return False, "Comment cannot be empty.", None
        if len(clean) > CommentService._MAX_LEN:
            return (
                False,
                f"Comment must be at most {CommentService._MAX_LEN} characters.",
                None,
            )

        try:
            with SessionLocal() as db:
                comment = CommentModel.create(
                    db, authorId=user_id, comment=clean, photoId=photo_id
                )
                author = UserModel.get_by_id(db, user_id)
                db.commit()

            enriched = {  # enrich with author info for convenience, even though the controller could do this in a batch
                **comment,
                "author_username": (
                    author.get("username", "Unknown") if author else "Unknown"
                ),
                "author_avatar": author.get("avatar") if author else None,
                "author_role": author.get("role", "regular") if author else "regular",
            }
            log_operation(
                "comment.add_comment",
                "success",
                f"Comment added to photo {photo_id}",
                user_id=user_id,
            )
            return True, "Comment added.", enriched
        except Exception as e:
            log_exception(
                "comment.add_comment",
                e,
                user_id=user_id,
                context={"photo_id": photo_id},
            )
            return False, "Something went wrong. Please try again later.", None

    @staticmethod
    def delete_comment(
        requesting_user_id: int, comment_id: int, is_admin: bool
    ) -> Tuple[bool, str]:
        """
        Delete a comment if the requesting user owns it or is an admin.

        Business rules:
        - A user can only delete their own comments.
        - An admin can delete any comment.

        Args:
            requesting_user_id: The ID of the user requesting the deletion.
            comment_id: The ID of the comment to delete.
            is_admin: Whether the requesting user is an admin.

        Returns:
            Tuple[bool, str]: (success, message)

        Raises:
            Exception: Any database error is caught and logged; (False, msg) returned.
        """
        try:
            with SessionLocal() as db:
                comment = CommentModel.get_by_id(db, comment_id)
                if comment is None:
                    return False, "Comment not found."
                if not is_admin and comment["authorId"] != requesting_user_id:
                    return False, "You do not have permission to delete this comment."
                CommentModel.delete(db, comment_id)
                db.commit()
            log_operation(
                "comment.delete_comment",
                "success",
                f"Comment {comment_id} deleted",
                user_id=requesting_user_id,
            )
            return True, "Comment deleted."
        except Exception as e:
            log_exception(
                "comment.delete_comment",
                e,
                user_id=requesting_user_id,
                context={"comment_id": comment_id},
            )
            return False, "Something went wrong. Please try again later."
