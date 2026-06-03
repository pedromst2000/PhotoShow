from typing import Optional

from app.core.db.engine import SessionLocal
from app.core.db.models.album import AlbumModel
from app.core.db.models.avatar import AvatarModel
from app.core.db.models.follow import FollowModel
from app.core.db.models.photo import PhotoModel
from app.core.db.models.role import RoleModel
from app.core.db.models.user import UserModel
from app.core.services.notification_service import NotificationService
from app.utils.log_utils import log_exception, log_operation


class UserService:
    """
    Service class for user management business logic.

    Business rules enforced in this service:
    - User listing for admin management excludes admin users and returns only essential fields.
    - Avatar updates create a new avatar record and associate it with the user.
    - Role changes validate that the new role is a valid assignable role.
    - Blocking/unblocking users checks current status to prevent redundant operations.
    - User filtering by username/email is case-insensitive and excludes admin users.
    - Follow/unfollow operations check for existing relationships to prevent duplicates or errors.
    - When retrieving followers/following, full user profiles are returned for display purposes.
    - All methods that modify data enforce necessary validation and business rules.
    """

    @staticmethod
    def get_profile_stats(user_id: int) -> dict:
        """
        Get profile statistics combining follower count and photo count.

        Combines FollowModel, AlbumModel, and PhotoModel in one session —
        a real use-case representing the data needed for the profile page.

        Raises:
            Exception: Any database error is caught and logged; defaults returned.
        """
        try:
            with SessionLocal() as session:
                follower_count = FollowModel.count_followers(session, user_id)
                albums = AlbumModel.get_by_creator(session, user_id)
                photo_count = sum(
                    len(PhotoModel.get_by_album(session, a["id"])) for a in albums
                )
            log_operation(
                "user.get_profile_stats",
                "success",
                f"Retrieved stats for user {user_id}",
                user_id=user_id,
            )
            return {"follower_count": follower_count, "photo_count": photo_count}
        except Exception as e:
            log_exception("user.get_profile_stats", e, user_id=user_id)
            return {"follower_count": 0, "photo_count": 0}

    @staticmethod
    def get_user_list_for_admin() -> list:
        """
        Get a filtered list of users for admin management.
        Excludes admin users and returns only essential fields.

        Returns:
            list: List of user dicts with userID, username, email, role, avatar, isBlocked.

        Raises:
            Exception: Any database error is caught and logged; empty list returned.
        """
        try:
            with SessionLocal() as session:
                users = [
                    {
                        "id": user["id"],
                        "username": user["username"],
                        "email": user["email"],
                        "role": user["role"],
                        "avatar": user["avatar"],
                        "isBlocked": user["isBlocked"],
                    }
                    for user in UserModel.get_all(session)
                    if user["role"] != "admin"
                ]
            log_operation(
                "user.get_user_list_for_admin",
                "success",
                f"Retrieved {len(users)} users for admin",
            )
            return users
        except Exception as e:
            log_exception("user.get_user_list_for_admin", e)
            return []

    @staticmethod
    def update_avatar(user_id: int, avatar_filename: str) -> bool:
        """
        Update a user's avatar.

        Args:
            user_id: The user's ID.
            avatar_filename: The new avatar filename (not full path).

        Returns:
            bool: True if updated successfully, False otherwise.

        Raises:
            Exception: Any database error is caught and logged; False returned.
        """
        try:
            avatar_path = f"assets/images/local_cloud_media/latest/profile_avatars/{avatar_filename}"
            with SessionLocal() as session:
                result = AvatarModel.update(session, user_id, avatar_path)
                session.commit()
            if result:
                log_operation(
                    "user.update_avatar",
                    "success",
                    f"Updated avatar for user {user_id}",
                    user_id=user_id,
                )
            else:
                log_operation(
                    "user.update_avatar",
                    "validation_error",
                    f"Avatar not found for user {user_id}",
                    user_id=user_id,
                )
            return result is not None
        except Exception as e:
            log_exception(
                "user.update_avatar",
                e,
                user_id=user_id,
                context={
                    "filename": avatar_filename
                },  # Log the filename for debugging purposes
            )
            return False

    @staticmethod
    def change_role(username: str, new_role: str) -> bool:
        """
        Change a user's role.

        Args:
            username: The username of the user.
            new_role: The new role to assign.

        Returns:
            bool: True if role was changed successfully, False otherwise.

        Raises:
            ValueError: If new_role is not a valid assignable role.
            Exception: Any database error is caught and logged; False returned.
        """
        try:
            VALID_ROLES = ["regular", "unsigned"]
            if new_role not in VALID_ROLES:
                log_operation(
                    "user.change_role", "validation_error", f"Invalid role: {new_role}"
                )
                raise ValueError(
                    f"Invalid role. Must be one of: {', '.join(VALID_ROLES)}"
                )

            with SessionLocal() as session:
                user = UserModel.get_by_username(session, username)
                if not user:
                    log_operation(
                        "user.change_role",
                        "validation_error",
                        f"User '{username}' not found",
                    )
                    return False
                role = RoleModel.get_by_name(session, new_role)
                if not role:
                    log_operation(
                        "user.change_role",
                        "validation_error",
                        f"Role '{new_role}' not found",
                    )
                    return False
                UserModel.update(session, {**user, "roleId": role["id"]})
                session.commit()
            log_operation(
                "user.change_role",
                "success",
                f"Changed role for user '{username}' to '{new_role}'",
                user_id=user["id"],
            )
            return True
        except ValueError:
            raise
        except Exception as e:
            log_exception(
                "user.change_role",
                e,
                context={"username": username, "new_role": new_role},
            )
            return False

    @staticmethod
    def block_user(username: str) -> bool:
        """
        Block a user by username.

        Args:
            username: The username of the user to block.

        Returns:
            bool: True if blocked successfully, False otherwise.

        Raises:
            ValueError: If user is already blocked.
            Exception: Any database error is caught and logged; False returned.
        """
        try:
            with SessionLocal() as session:
                user = UserModel.get_by_username(session, username)
                if not user:
                    log_operation(
                        "user.block_user",
                        "validation_error",
                        f"User '{username}' not found",
                    )
                    return False
                if user["isBlocked"]:
                    log_operation(
                        "user.block_user",
                        "validation_error",
                        f"User '{username}' is already blocked",
                        user_id=user["id"],
                    )
                    raise ValueError(f'"{username}" is already blocked.')
                result = UserModel.set_blocked(session, user["id"], True)
                session.commit()
            log_operation(
                "user.block_user",
                "success",
                f"Blocked user '{username}'",
                user_id=user["id"],
            )
            return result
        except ValueError:
            raise
        except Exception as e:
            log_exception("user.block_user", e, context={"username": username})
            return False

    @staticmethod
    def unblock_user(username: str) -> bool:
        """
        Unblock a user by username.

        Args:
            username: The username of the user to unblock.

        Returns:
            bool: True if unblocked successfully, False otherwise.

        Raises:
            ValueError: If user is already unblocked.
            Exception: Any database error is caught and logged; False returned.
        """
        try:
            with SessionLocal() as session:
                user = UserModel.get_by_username(session, username)
                if not user:
                    log_operation(
                        "user.unblock_user",
                        "validation_error",
                        f"User '{username}' not found",
                    )
                    return False
                if not user["isBlocked"]:
                    log_operation(
                        "user.unblock_user",
                        "validation_error",
                        f"User '{username}' is already unblocked",
                        user_id=user["id"],
                    )
                    raise ValueError(f'"{username}" is already unblocked.')
                result = UserModel.set_blocked(session, user["id"], False)
                session.commit()
            log_operation(
                "user.unblock_user",
                "success",
                f"Unblocked user '{username}'",
                user_id=user["id"],
            )
            return result
        except ValueError:
            raise
        except Exception as e:
            log_exception("user.unblock_user", e, context={"username": username})
            return False

    @staticmethod
    def filter_users(
        username: str,
        email: str,
        role: str = "",
        status: str = "",
    ) -> list:
        """
        Filter users by username, email, role, and/or blocked status.
        Admin users are always excluded.

        Args:
            username: Username prefix to filter by (empty string to skip).
            email: Email prefix to filter by (empty string to skip).
            role: Role name to filter by, e.g. ``"regular"`` or ``"unsigned"``
                  (empty string to skip).
            status: ``"blocked"`` or ``"active"`` to filter by blocked state
                    (empty string to skip).

        Returns:
            list: Filtered list of user dictionaries.
        """
        with SessionLocal() as session:
            users = [u for u in UserModel.get_all(session) if u["role"] != "admin"]

        if username:
            users = [
                u for u in users if u["username"].lower().startswith(username.lower())
            ]

        if email:
            users = [u for u in users if u["email"].lower().startswith(email.lower())]

        if role:
            users = [u for u in users if u["role"] == role]

        if status == "blocked":
            users = [u for u in users if u["isBlocked"]]
        elif status == "active":
            users = [u for u in users if not u["isBlocked"]]

        return users

    @staticmethod
    def follow_user(follower_id: int, followed_id: int) -> bool:
        """
        Make follower_id follow followed_id.

        Args:
            follower_id: The ID of the user doing the following.
            followed_id: The ID of the user being followed.

        Returns:
            bool: True if the follow was created, False if already following.
        """
        with SessionLocal() as session:
            result = FollowModel.follow(session, follower_id, followed_id)
            session.commit()
        if result is not None:
            NotificationService.send(
                "new_follower",
                "started following you",
                user_id=followed_id,
                sender_id=follower_id,
            )
            return True
        return False

    @staticmethod
    def unfollow_user(follower_id: int, followed_id: int) -> bool:
        """
        Make follower_id unfollow followed_id and remove the related notification.

        Args:
            follower_id: The ID of the user doing the unfollowing.
            followed_id: The ID of the user being unfollowed.

        Returns:
            bool: True if the relationship was removed, False if it didn't exist.
        """
        with SessionLocal() as session:
            result = FollowModel.unfollow(session, follower_id, followed_id)
            session.commit()
        # Remove the new_follower notification when user unfollows
        if result:
            NotificationService.delete_by_follow(follower_id, followed_id)

        return result

    @staticmethod
    def is_following(follower_id: int, followed_id: int) -> bool:
        """
        Check whether follower_id is currently following followed_id.

        Args:
            follower_id: The ID of the user who may be following.
            followed_id: The ID of the user who may be followed.
        Returns:
            bool: True if the follow relationship exists.
        """
        with SessionLocal() as session:
            return FollowModel.is_following(session, follower_id, followed_id)

    @staticmethod
    def get_profile(user_id: int) -> Optional[dict]:
        """
        Retrieve a user's profile information by ID.

        Args:
            user_id: The ID of the user whose profile to retrieve.

        Returns:
            dict or None: The user's profile data as a dictionary, or None if not found.
        """
        with SessionLocal() as session:
            return UserModel.get_by_id(session, user_id)

    @staticmethod
    def refresh_user_session(user_id: int) -> Optional[dict]:
        """
        Refresh and retrieve the latest user data from the database.

        Args:
            user_id: The ID of the user to refresh.

        Returns:
            dict or None: The updated user's data, or None if user not found.
        """
        with SessionLocal() as session:
            return UserModel.get_by_id(session, user_id)
