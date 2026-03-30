from sqlalchemy.orm import relationship

from app.core.db.models.album import AlbumModel
from app.core.db.models.avatar import AvatarModel
from app.core.db.models.category import CategoryModel
from app.core.db.models.comment import CommentModel
from app.core.db.models.contact import ContactModel
from app.core.db.models.favorite import FavoriteModel
from app.core.db.models.follow import FollowModel
from app.core.db.models.like import LikeModel
from app.core.db.models.notification import NotificationModel
from app.core.db.models.notification_types import NotificationTypeModel
from app.core.db.models.photo import PhotoModel
from app.core.db.models.photo_image import PhotoImageModel
from app.core.db.models.rating import RatingModel
from app.core.db.models.role import RoleModel
from app.core.db.models.user import UserModel

"""
This file imports all SQLAlchemy ORM models and defines their relationships.
All models are imported here to ensure relationships can be established between them.
"""

__all__ = [
    "UserModel",
    "RoleModel",
    "CategoryModel",
    "AlbumModel",
    "PhotoModel",
    "PhotoImageModel",
    "RatingModel",
    "AvatarModel",
    "NotificationModel",
    "NotificationTypeModel",
    "CommentModel",
    "FavoriteModel",
    "ContactModel",
    "FollowModel",
    "LikeModel",
]

# =============================================================================
# RoleModel relationships
# =============================================================================

# ORM one-to-many: one role has many users
RoleModel.users_rel = relationship("UserModel", back_populates="role_rel")

# =============================================================================
# UserModel relationships
# =============================================================================

# ORM many-to-one: many users belong to one role (nullable — unsigned users have no role)
UserModel.role_rel = relationship(
    "RoleModel", foreign_keys=[UserModel.roleId], back_populates="users_rel"
)

# ORM one-to-one: one user has one avatar
UserModel.avatar_rel = relationship(
    "AvatarModel",
    uselist=False,
    cascade="all, delete-orphan",
    passive_deletes=True,
    back_populates="user_rel",
)

# ORM one-to-many: one user (creator) has many albums
UserModel.albums_rel = relationship(
    "AlbumModel",
    cascade="all, delete-orphan",
    passive_deletes=True,
    back_populates="creator_rel",
)

# ORM one-to-many: one user has many contact messages
UserModel.contacts_rel = relationship(
    "ContactModel",
    cascade="all, delete-orphan",
    passive_deletes=True,
    back_populates="user_rel",
)

# ORM one-to-many: one user has many likes
UserModel.likes_rel = relationship(
    "LikeModel", passive_deletes=True, back_populates="user_rel"
)

# ORM one-to-many: one user has many ratings
UserModel.ratings_rel = relationship(
    "RatingModel", passive_deletes=True, back_populates="user_rel"
)

# ORM one-to-many: one user has many comments as author (foreign_keys required — authorId disambiguates)
UserModel.comments_rel = relationship(
    "CommentModel",
    foreign_keys=[CommentModel.authorId],
    passive_deletes=True,
    back_populates="author_rel",
)

# ORM one-to-many: one user has many favorites
UserModel.favorites_rel = relationship(
    "FavoriteModel", passive_deletes=True, back_populates="user_rel"
)

# ORM self-referential one-to-many: users this user follows (followerId = this user's id)
UserModel.following_rel = relationship(
    "FollowModel",
    foreign_keys=[FollowModel.followerId],
    passive_deletes=True,
    back_populates="follower_user_rel",
)

# ORM self-referential one-to-many: users that follow this user (followedId = this user's id)
UserModel.followers_rel = relationship(
    "FollowModel",
    foreign_keys=[FollowModel.followedId],
    passive_deletes=True,
    back_populates="followed_user_rel",
)

# ORM one-to-many: notifications received by this user (recipientId FK)
UserModel.notifications_received_rel = relationship(
    "NotificationModel",
    foreign_keys=[NotificationModel.recipientId],
    passive_deletes=True,
    back_populates="recipient_rel",
)

# ORM one-to-many: notifications sent/triggered by this user (senderId FK)
UserModel.notifications_sent_rel = relationship(
    "NotificationModel",
    foreign_keys=[NotificationModel.senderId],
    passive_deletes=True,
    back_populates="sender_rel",
)

# =============================================================================
# AvatarModel relationships
# =============================================================================

# ORM many-to-one: avatar belongs to one user (unique constraint makes it one-to-one in practice)
AvatarModel.user_rel = relationship(
    "UserModel", foreign_keys=[AvatarModel.userId], back_populates="avatar_rel"
)

# =============================================================================
# AlbumModel relationships
# =============================================================================

# ORM many-to-one: many albums belong to one creator user
AlbumModel.creator_rel = relationship(
    "UserModel", foreign_keys=[AlbumModel.creatorId], back_populates="albums_rel"
)

# ORM one-to-many: one album has many photos (photos survive album deletion — albumId SET NULL by DB)
AlbumModel.photos_rel = relationship(
    "PhotoModel",
    passive_deletes=True,
    back_populates="album_rel",
)

# ORM one-to-many: one album has many favorites
AlbumModel.favorites_rel = relationship(
    "FavoriteModel",
    cascade="all, delete-orphan",
    passive_deletes=True,
    back_populates="album_rel",
)

# =============================================================================
# CategoryModel relationships
# =============================================================================

# ORM one-to-many: one category has many photos (cascade delete when category is removed)
CategoryModel.photos_rel = relationship(
    "PhotoModel",
    cascade="all, delete-orphan",
    passive_deletes=True,
    back_populates="category_rel",
)

# =============================================================================
# PhotoModel relationships
# =============================================================================

# ORM many-to-one: many photos belong to one category
PhotoModel.category_rel = relationship(
    "CategoryModel", foreign_keys=[PhotoModel.categoryId], back_populates="photos_rel"
)

# ORM many-to-one: many photos belong to one album (optional — photo may exist without an album)
PhotoModel.album_rel = relationship(
    "AlbumModel", foreign_keys=[PhotoModel.albumId], back_populates="photos_rel"
)

# ORM one-to-one: one photo has a single image (photo_image.photoId unique)
PhotoModel.image_rel = relationship(
    "PhotoImageModel",
    cascade="all, delete-orphan",
    passive_deletes=True,
    back_populates="photo_rel",
    uselist=False,
)

# ORM one-to-many: one photo has many ratings
PhotoModel.ratings_rel = relationship(
    "RatingModel",
    cascade="all, delete-orphan",
    passive_deletes=True,
    back_populates="photo_rel",
)

# ORM one-to-many: one photo has many comments
PhotoModel.comments_rel = relationship(
    "CommentModel",
    cascade="all, delete-orphan",
    passive_deletes=True,
    back_populates="photo_rel",
)

# ORM one-to-many: one photo has many likes
PhotoModel.likes_rel = relationship(
    "LikeModel",
    cascade="all, delete-orphan",
    passive_deletes=True,
    back_populates="photo_rel",
)

# =============================================================================
# PhotoImageModel relationships
# =============================================================================

# ORM one-to-one: image belongs to one photo (unique constraint enforces one image per photo)
PhotoImageModel.photo_rel = relationship(
    "PhotoModel",
    foreign_keys=[PhotoImageModel.photoId],
    back_populates="image_rel",
    uselist=False,
)

# =============================================================================
# RatingModel relationships
# =============================================================================

# ORM many-to-one: many ratings belong to one user
RatingModel.user_rel = relationship(
    "UserModel", foreign_keys=[RatingModel.userId], back_populates="ratings_rel"
)

# ORM many-to-one: many ratings belong to one photo
RatingModel.photo_rel = relationship(
    "PhotoModel", foreign_keys=[RatingModel.photoId], back_populates="ratings_rel"
)

# =============================================================================
# CommentModel relationships
# =============================================================================

# ORM many-to-one: many comments belong to one author user
CommentModel.author_rel = relationship(
    "UserModel", foreign_keys=[CommentModel.authorId], back_populates="comments_rel"
)

# ORM many-to-one: many comments belong to one photo
CommentModel.photo_rel = relationship(
    "PhotoModel", foreign_keys=[CommentModel.photoId], back_populates="comments_rel"
)

# =============================================================================
# ContactModel relationships
# =============================================================================

# ORM many-to-one: many contact messages belong to one user
ContactModel.user_rel = relationship(
    "UserModel", foreign_keys=[ContactModel.userId], back_populates="contacts_rel"
)

# =============================================================================
# FavoriteModel relationships
# =============================================================================

# ORM many-to-one: many favorites belong to one user
FavoriteModel.user_rel = relationship(
    "UserModel", foreign_keys=[FavoriteModel.userId], back_populates="favorites_rel"
)

# ORM many-to-one: many favorites belong to one album
FavoriteModel.album_rel = relationship(
    "AlbumModel", foreign_keys=[FavoriteModel.albumId], back_populates="favorites_rel"
)

# =============================================================================
# FollowModel relationships
# =============================================================================

# ORM many-to-one: the user who is following (followerId = this user's id)
FollowModel.follower_user_rel = relationship(
    "UserModel", foreign_keys=[FollowModel.followerId], back_populates="following_rel"
)

# ORM many-to-one: the user being followed (followedId = this user's id)
FollowModel.followed_user_rel = relationship(
    "UserModel", foreign_keys=[FollowModel.followedId], back_populates="followers_rel"
)

# =============================================================================
# LikeModel relationships
# =============================================================================

# ORM many-to-one: many likes belong to one user
LikeModel.user_rel = relationship(
    "UserModel", foreign_keys=[LikeModel.userId], back_populates="likes_rel"
)

# ORM many-to-one: many likes belong to one photo
LikeModel.photo_rel = relationship(
    "PhotoModel", foreign_keys=[LikeModel.photoId], back_populates="likes_rel"
)

# =============================================================================
# NotificationTypeModel relationships
# =============================================================================

# ORM one-to-many: one notification_type has many notifications
NotificationTypeModel.notifications_rel = relationship(
    "NotificationModel",
    cascade="all, delete-orphan",
    passive_deletes=True,
    back_populates="type_rel",
)

# =============================================================================
# NotificationModel relationships
# =============================================================================

# ORM many-to-one: many notifications belong to one notification type
NotificationModel.type_rel = relationship(
    "NotificationTypeModel",
    foreign_keys=[NotificationModel.typeId],
    back_populates="notifications_rel",
)

# ORM many-to-one: many notifications are received by one user (recipient)
NotificationModel.recipient_rel = relationship(
    "UserModel",
    foreign_keys=[NotificationModel.recipientId],
    back_populates="notifications_received_rel",
)

# ORM many-to-one: many notifications are triggered by one sender user (nullable)
NotificationModel.sender_rel = relationship(
    "UserModel",
    foreign_keys=[NotificationModel.senderId],
    back_populates="notifications_sent_rel",
)

# =============================================================================
# Notification target relationships — direct FK to each target table
# =============================================================================

# Notification → a photo (nullable)
NotificationModel.photo_rel = relationship(
    "PhotoModel",
    foreign_keys=[NotificationModel.photoId],
    back_populates="notifications_rel",
)

# Notification → an album (nullable)
NotificationModel.album_rel = relationship(
    "AlbumModel",
    foreign_keys=[NotificationModel.albumId],
    back_populates="notifications_rel",
)

# Notification → a comment (nullable)
NotificationModel.comment_rel = relationship(
    "CommentModel",
    foreign_keys=[NotificationModel.commentId],
    back_populates="notifications_rel",
)

# Photo → all notifications that reference it
PhotoModel.notifications_rel = relationship(
    "NotificationModel",
    foreign_keys=[NotificationModel.photoId],
    back_populates="photo_rel",
)

# Album → all notifications that reference it
AlbumModel.notifications_rel = relationship(
    "NotificationModel",
    foreign_keys=[NotificationModel.albumId],
    back_populates="album_rel",
)

# Comment → all notifications that reference it
CommentModel.notifications_rel = relationship(
    "NotificationModel",
    foreign_keys=[NotificationModel.commentId],
    back_populates="comment_rel",
)
