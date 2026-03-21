"""
This file marks the 'db.models' directory as a Python package.
"""

from db.models.album import AlbumModel
from db.models.avatar import AvatarModel
from db.models.category import CategoryModel
from db.models.comment import CommentModel
from db.models.contact import ContactModel
from db.models.favorite import FavoriteModel
from db.models.follow import FollowModel
from db.models.like import LikeModel
from db.models.notification import NotificationModel
from db.models.notification_types import NotificationTypeModel
from db.models.photo import PhotoModel
from db.models.photo_image import PhotoImageModel
from db.models.rating import RatingModel
from db.models.role import RoleModel
from db.models.user import UserModel

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
