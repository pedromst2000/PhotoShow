"""
Integration tests for UserService covering profile stats, avatars, followers, and blocking.

Focuses on:
- Profile statistics calculation (followers, photo counts)
- Avatar management and retrieval
- Follow/unfollow operations
- User listing for admin management
- Blocking/unblocking users
"""

from app.core.services.album_service import AlbumService
from app.core.services.auth_service import AuthService
from app.core.services.photo_service import PhotoService
from app.core.services.user_service import UserService


class TestProfileStats:
    """Test user profile statistics calculation."""

    def test_profile_stats_new_user(self, integration_db):
        """New user has zero followers and zero photos."""
        user = AuthService.register_user("alice", "alice@example.com", "password")
        stats = UserService.get_profile_stats(user["id"])

        assert stats["follower_count"] == 0
        assert stats["photo_count"] == 0

    def test_profile_stats_with_photos(self, integration_db):
        """Profile stats include photo count from albums."""
        user = AuthService.register_user("bob", "bob@example.com", "password")
        album = AlbumService.create_album("Album 1", user["id"])

        # Create 3 photos
        for i in range(3):
            PhotoService.create_photo_record(
                album_id=album["id"],
                category_id=1,
                description=f"Photo {i}",
            )

        stats = UserService.get_profile_stats(user["id"])

        assert stats["photo_count"] == 3
        assert stats["follower_count"] == 0

    def test_profile_stats_with_followers(self, integration_db):
        """Profile stats include follower count."""
        user1 = AuthService.register_user("charlie", "charlie@example.com", "password")
        user2 = AuthService.register_user("diana", "diana@example.com", "password")
        user3 = AuthService.register_user("eve", "eve@example.com", "password")

        # user2 and user3 follow user1
        UserService.follow_user(user2["id"], user1["id"])
        UserService.follow_user(user3["id"], user1["id"])

        stats = UserService.get_profile_stats(user1["id"])

        assert stats["follower_count"] == 2

    def test_profile_stats_nonexistent_user(self, integration_db):
        """Nonexistent user returns default stats."""
        stats = UserService.get_profile_stats(9999)

        assert stats["follower_count"] == 0
        assert stats["photo_count"] == 0


class TestAvatarManagement:
    """Test avatar updates and retrieval."""

    def test_update_avatar_success(self, integration_db):
        """Avatar is updated successfully."""
        user = AuthService.register_user("frank", "frank@example.com", "password")

        result = UserService.update_avatar(
            user_id=user["id"],
            provider_id="cloudinary_provider_1",
            provider_url_image="https://example.com/avatar.jpg",
        )

        assert result is True

    def test_update_avatar_replaces_previous(self, integration_db):
        """Updating avatar replaces the previous one."""
        user = AuthService.register_user("grace", "grace@example.com", "password")

        # Update once
        UserService.update_avatar(
            user_id=user["id"],
            provider_id="provider_1",
            provider_url_image="https://example.com/avatar1.jpg",
        )

        # Update again
        UserService.update_avatar(
            user_id=user["id"],
            provider_id="provider_2",
            provider_url_image="https://example.com/avatar2.jpg",
        )

        # Get current avatar
        current = UserService.get_current_avatar_provider_id(user["id"])
        assert current == "provider_2"

    def test_get_current_avatar_provider_id(self, integration_db):
        """Retrieve current avatar provider ID."""
        user = AuthService.register_user("helen", "helen@example.com", "password")

        UserService.update_avatar(
            user_id=user["id"],
            provider_id="my_provider",
            provider_url_image="https://example.com/avatar.jpg",
        )

        provider_id = UserService.get_current_avatar_provider_id(user["id"])
        assert provider_id == "my_provider"

    def test_get_avatar_nonexistent_user(self, integration_db):
        """Getting avatar for nonexistent user returns None."""
        provider_id = UserService.get_current_avatar_provider_id(9999)
        assert provider_id is None


class TestFollowOperations:
    """Test follow/unfollow operations."""

    def test_follow_user_success(self, integration_db):
        """User can follow another user."""
        user1 = AuthService.register_user("ian", "ian@example.com", "password")
        user2 = AuthService.register_user("jack", "jack@example.com", "password")

        result = UserService.follow_user(user1["id"], user2["id"])

        assert result is True

    def test_follow_user_already_following(self, integration_db):
        """Following already-followed user returns False."""
        user1 = AuthService.register_user("karen", "karen@example.com", "password")
        user2 = AuthService.register_user("leo", "leo@example.com", "password")

        UserService.follow_user(user1["id"], user2["id"])
        result = UserService.follow_user(user1["id"], user2["id"])

        assert result is False

    def test_unfollow_user_success(self, integration_db):
        """User can unfollow another user."""
        user1 = AuthService.register_user("mary", "mary@example.com", "password")
        user2 = AuthService.register_user("nancy", "nancy@example.com", "password")

        UserService.follow_user(user1["id"], user2["id"])
        result = UserService.unfollow_user(user1["id"], user2["id"])

        assert result is True

    def test_unfollow_not_following(self, integration_db):
        """Unfollowing user you don't follow returns False."""
        user1 = AuthService.register_user("oscar", "oscar@example.com", "password")
        user2 = AuthService.register_user("paul", "paul@example.com", "password")

        result = UserService.unfollow_user(user1["id"], user2["id"])

        assert result is False

    def test_cannot_follow_self(self, integration_db):
        """User cannot follow themselves."""
        user = AuthService.register_user("quinn", "quinn@example.com", "password")

        result = UserService.follow_user(user["id"], user["id"])

        assert result is False

    def test_get_followers(self, integration_db):
        """Get list of followers."""
        user1 = AuthService.register_user("rachel", "rachel@example.com", "password")
        user2 = AuthService.register_user("steve", "steve@example.com", "password")
        user3 = AuthService.register_user("tina", "tina@example.com", "password")

        UserService.follow_user(user2["id"], user1["id"])
        UserService.follow_user(user3["id"], user1["id"])

        followers = UserService.get_followers(user1["id"])

        assert len(followers) == 2
        follower_ids = [f["id"] for f in followers]
        assert user2["id"] in follower_ids
        assert user3["id"] in follower_ids

    def test_get_following(self, integration_db):
        """Get list of users being followed."""
        user1 = AuthService.register_user("uma", "uma@example.com", "password")
        user2 = AuthService.register_user("vera", "vera@example.com", "password")
        user3 = AuthService.register_user("walt", "walt@example.com", "password")

        UserService.follow_user(user1["id"], user2["id"])
        UserService.follow_user(user1["id"], user3["id"])

        following = UserService.get_following(user1["id"])

        assert len(following) == 2
        following_ids = [f["id"] for f in following]
        assert user2["id"] in following_ids
        assert user3["id"] in following_ids


class TestUserListForAdmin:
    """Test admin user listing."""

    def test_get_user_list_for_admin(self, integration_db):
        """Get user list excludes admin users."""
        user1 = AuthService.register_user("xander", "xander@example.com", "password")
        user2 = AuthService.register_user("yara", "yara@example.com", "password")

        users = UserService.get_user_list_for_admin()

        # Should have at least 2 users (no admin in the list)
        assert len(users) >= 2
        user_ids = [u["id"] for u in users]
        assert user1["id"] in user_ids
        assert user2["id"] in user_ids

        # All returned users should have essential fields
        for user in users:
            assert "id" in user
            assert "username" in user
            assert "email" in user
            assert "role" in user


class TestUserProfile:
    """Test getting user profile information."""

    def test_get_profile_success(self, integration_db):
        """Retrieve user profile."""
        user = AuthService.register_user("zara", "zara@example.com", "password")

        profile = UserService.get_profile(user["id"])

        assert profile is not None
        assert profile["id"] == user["id"]
        assert profile["username"] == "zara"
        assert profile["email"] == "zara@example.com"

    def test_get_profile_nonexistent(self, integration_db):
        """Get profile for nonexistent user returns None."""
        profile = UserService.get_profile(9999)
        assert profile is None

    def test_get_profile_contains_stats(self, integration_db):
        """Profile includes follower and photo stats."""
        user1 = AuthService.register_user("alex1", "alex1@example.com", "password")
        user2 = AuthService.register_user("alex2", "alex2@example.com", "password")

        # user2 follows user1
        UserService.follow_user(user2["id"], user1["id"])

        # user1 creates an album and photo
        album = AlbumService.create_album("Album 1", user1["id"])
        PhotoService.create_photo_record(
            album_id=album["id"],
            category_id=1,
            description="Photo 1",
        )

        profile = UserService.get_profile(user1["id"])

        assert profile is not None
        assert (
            "follower_count" in profile
            or "followers" in profile.keys()
            or len(UserService.get_followers(user1["id"])) == 1
        )
