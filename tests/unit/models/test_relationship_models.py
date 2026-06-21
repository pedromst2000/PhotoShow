"""Unit tests for FollowModel, FavoriteModel, AvatarModel, PhotoImageModel, NotificationModel, ReportModel, ContactModel."""

from datetime import datetime, timezone

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.db.engine import Base
from app.core.db.models.album import AlbumModel
from app.core.db.models.avatar import AvatarModel
from app.core.db.models.category import CategoryModel
from app.core.db.models.contact import ContactModel
from app.core.db.models.favorite import FavoriteModel
from app.core.db.models.follow import FollowModel
from app.core.db.models.notification import NotificationModel
from app.core.db.models.notification_types import NotificationTypeModel
from app.core.db.models.photo import PhotoModel
from app.core.db.models.photo_image import PhotoImageModel
from app.core.db.models.report import ReportModel
from app.core.db.models.report_reason import ReportReasonModel
from app.core.db.models.role import RoleModel
from app.core.db.models.user import UserModel


@pytest.fixture
def test_db():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    session.add_all(
        [
            RoleModel(id=1, role="admin"),
            RoleModel(id=2, role="regular"),
            RoleModel(id=3, role="unsigned"),
        ]
    )
    session.commit()
    yield session
    session.close()


@pytest.fixture
def fixtures_users(test_db):
    user1 = UserModel(
        username="user1", email="user1@gmail.com", password="hashed", roleId=2
    )
    user2 = UserModel(
        username="user2", email="user2@gmail.com", password="hashed", roleId=2
    )
    test_db.add_all([user1, user2])
    test_db.commit()
    return user1, user2


@pytest.fixture
def fixtures_photo(test_db):
    category = CategoryModel(category="Test")
    test_db.add(category)
    test_db.commit()
    photo = PhotoModel(
        description="Photo",
        publishedDate=datetime.now(timezone.utc),
        categoryId=category.id,
    )
    test_db.add(photo)
    test_db.commit()
    return photo


@pytest.fixture
def fixtures_album(test_db, fixtures_users):
    user1, _ = fixtures_users
    album = AlbumModel(name="Test Album", creatorId=user1.id)
    test_db.add(album)
    test_db.commit()
    return album


# ─── Follow Model Tests ─────────────────────────────────────────
class TestFollowModel:
    """Test FollowModel."""

    def test_to_dict(self, test_db, fixtures_users):
        follower, followed = fixtures_users
        follow = FollowModel(followerId=follower.id, followedId=followed.id)
        test_db.add(follow)
        test_db.commit()

        result = follow.to_dict()
        assert result["followerId"] == follower.id
        assert result["followedId"] == followed.id

    def test_unique_follow_pair(self, test_db, fixtures_users):
        follower, followed = fixtures_users
        follow1 = FollowModel(followerId=follower.id, followedId=followed.id)
        test_db.add(follow1)
        test_db.commit()

        follow2 = FollowModel(followerId=follower.id, followedId=followed.id)
        test_db.add(follow2)

        with pytest.raises(Exception):
            test_db.commit()

    def test_get_by_id(self, test_db, fixtures_users):
        follower, followed = fixtures_users
        follow = FollowModel(followerId=follower.id, followedId=followed.id)
        test_db.add(follow)
        test_db.commit()

        retrieved = test_db.query(FollowModel).filter_by(id=follow.id).first()
        assert retrieved is not None


# ─── Favorite Model Tests ──────────────────────────────────────────
class TestFavoriteModel:
    """Test FavoriteModel."""

    def test_to_dict(self, test_db, fixtures_users, fixtures_album):
        user, _ = fixtures_users
        favorite = FavoriteModel(userId=user.id, albumId=fixtures_album.id)
        test_db.add(favorite)
        test_db.commit()

        result = favorite.to_dict()
        assert result["userId"] == user.id
        assert result["albumId"] == fixtures_album.id

    def test_unique_user_album_favorite(self, test_db, fixtures_users, fixtures_album):
        user, _ = fixtures_users
        fav1 = FavoriteModel(userId=user.id, albumId=fixtures_album.id)
        test_db.add(fav1)
        test_db.commit()

        fav2 = FavoriteModel(userId=user.id, albumId=fixtures_album.id)
        test_db.add(fav2)

        with pytest.raises(Exception):
            test_db.commit()

    def test_get_by_id(self, test_db, fixtures_users, fixtures_album):
        user, _ = fixtures_users
        favorite = FavoriteModel(userId=user.id, albumId=fixtures_album.id)
        test_db.add(favorite)
        test_db.commit()

        retrieved = test_db.query(FavoriteModel).filter_by(id=favorite.id).first()
        assert retrieved is not None


# ─── Avatar Model Tests ────────────────────────────────────────────
class TestAvatarModel:
    """Test AvatarModel."""

    def test_to_dict(self, test_db, fixtures_users):
        user, _ = fixtures_users
        avatar = AvatarModel(
            userId=user.id,
            provider_id="cloud/avatar1",
            provider_url_image="https://res.cloudinary.com/avatar1.jpg",
        )
        test_db.add(avatar)
        test_db.commit()

        result = avatar.to_dict()
        assert result["userId"] == user.id
        assert result["provider_url_image"] == "https://res.cloudinary.com/avatar1.jpg"

    def test_get_by_id(self, test_db, fixtures_users):
        user, _ = fixtures_users
        avatar = AvatarModel(
            userId=user.id, provider_url_image="https://res.cloudinary.com/avatar1.jpg"
        )
        test_db.add(avatar)
        test_db.commit()

        retrieved = test_db.query(AvatarModel).filter_by(id=avatar.id).first()
        assert retrieved is not None


# ─── PhotoImage Model Tests ────────────────────────────────────────
class TestPhotoImageModel:
    """Test PhotoImageModel."""

    def test_to_dict(self, test_db, fixtures_photo):
        photo_image = PhotoImageModel(
            photoId=fixtures_photo.id,
            provider_image_id="photo/img1",
            provider_image_url="https://res.cloudinary.com/img1.jpg",
        )
        test_db.add(photo_image)
        test_db.commit()

        result = photo_image.to_dict()
        assert result["photoId"] == fixtures_photo.id
        assert result["provider_image_url"] == "https://res.cloudinary.com/img1.jpg"

    def test_get_by_id(self, test_db, fixtures_photo):
        photo_image = PhotoImageModel(
            photoId=fixtures_photo.id,
            provider_image_url="https://res.cloudinary.com/img1.jpg",
        )
        test_db.add(photo_image)
        test_db.commit()

        retrieved = test_db.query(PhotoImageModel).filter_by(id=photo_image.id).first()
        assert retrieved is not None


# ─── Notification Model Tests ─────────────────────────────────────
class TestNotificationModel:
    """Test NotificationModel."""

    def test_to_dict(self, test_db, fixtures_users):
        recipient, sender = fixtures_users
        notif_type = NotificationTypeModel(id=1, type="follow", label="Follow")
        test_db.add(notif_type)
        test_db.commit()

        notification = NotificationModel(
            recipientId=recipient.id,
            senderId=sender.id,
            typeId=notif_type.id,
            message="You have a new follower",
        )
        test_db.add(notification)
        test_db.commit()

        result = notification.to_dict()
        assert result["recipientId"] == recipient.id
        assert result["typeId"] == notif_type.id

    def test_get_by_user(self, test_db, fixtures_users):
        recipient, sender = fixtures_users
        notif_type = NotificationTypeModel(id=1, type="follow", label="Follow")
        test_db.add(notif_type)
        test_db.commit()

        notification = NotificationModel(
            recipientId=recipient.id,
            senderId=sender.id,
            typeId=notif_type.id,
            message="New notification",
        )
        test_db.add(notification)
        test_db.commit()

        retrieved = NotificationModel.get_by_user(test_db, recipient.id)
        assert len(retrieved) > 0


# ─── Report Model Tests ────────────────────────────────────────────
class TestReportModel:
    """Test ReportModel."""

    def test_to_dict(self, test_db, fixtures_users, fixtures_photo):
        user, _ = fixtures_users
        reason = ReportReasonModel(id=1, label="inappropriate")
        test_db.add(reason)
        test_db.commit()

        report = ReportModel(
            reporterId=user.id,
            reasonId=reason.id,
            photoId=fixtures_photo.id,
            commentId=None,
        )
        test_db.add(report)
        test_db.commit()

        result = report.to_dict()
        assert result["reporterId"] == user.id
        assert result["reasonId"] == reason.id

    def test_get_by_id(self, test_db, fixtures_users, fixtures_photo):
        user, _ = fixtures_users
        reason = ReportReasonModel(id=1, label="inappropriate")
        test_db.add(reason)
        test_db.commit()

        report = ReportModel(
            reporterId=user.id,
            reasonId=reason.id,
            photoId=fixtures_photo.id,
            commentId=None,
        )
        test_db.add(report)
        test_db.commit()

        retrieved = ReportModel.get_by_id(test_db, report.id)
        assert retrieved is not None


# ─── Contact Model Tests ──────────────────────────────────────────
class TestContactModel:
    """Test ContactModel."""

    def test_to_dict(self, test_db, fixtures_users):
        user, _ = fixtures_users
        contact = ContactModel(userId=user.id, title="Feedback", message="Great app!")
        test_db.add(contact)
        test_db.commit()

        result = contact.to_dict()
        assert result["userId"] == user.id
        assert result["title"] == "Feedback"
        assert result["message"] == "Great app!"

    def test_get_by_id(self, test_db, fixtures_users):
        user, _ = fixtures_users
        contact = ContactModel(userId=user.id, title="Support", message="Help needed")
        test_db.add(contact)
        test_db.commit()

        retrieved = test_db.query(ContactModel).filter_by(id=contact.id).first()
        assert retrieved is not None
