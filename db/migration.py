import csv
from datetime import datetime

from db.engine import SessionLocal, init_db
from db.models import (
    AlbumModel,
    AvatarModel,
    CategoryModel,
    CommentModel,
    ContactModel,
    FavoriteModel,
    FollowModel,
    LikeModel,
    NotificationModel,
    NotificationTypeModel,
    PhotoImageModel,
    PhotoModel,
    RatingModel,
    RoleModel,
    UserModel,
)
from utils.hash_utils import hash_password
from utils.log_utils import log_check, log_issue, log_success

# ── CSV readers (return plain lists of ORM objects) ───────────────────────────


def _read_roles() -> list:
    """
    Read roles from CSV file and return a list of RoleModel instances.

    Returns:
        list: A list of RoleModel instances read from the CSV file.
    """

    path = "files/roles.csv"
    data = []
    log_check(f"Reading roles from {path}...")
    try:
        with open(path, "r", encoding="utf-8-sig", newline="") as f:
            for parts in csv.reader(f):  # expected: id,role
                if parts[0] == "id":
                    continue
                if len(parts) < 2:  # skip malformed lines
                    continue
                data.append(RoleModel(id=int(parts[0]), role=parts[1]))
        log_success(f"Loaded {len(data)} roles.")
    except FileNotFoundError as e:
        log_issue("roles.csv not found — roles will not be seeded", exc=e, path=path)
    except Exception as e:
        log_issue("Unexpected error reading roles", exc=e, path=path)
    return data


def _read_users() -> list:
    """
    Read users from CSV file and return a list of UserModel instances.

    Returns:
        list: A list of UserModel instances read from the CSV file.
    """

    path = "files/users.csv"
    data = []
    log_check(f"Reading users from {path}...")
    try:
        with open(path, "r", encoding="utf-8-sig", newline="") as f:
            for parts in csv.reader(
                f
            ):  # expected: id,username,email,password,roleID,isBlocked
                if parts[0] == "id":
                    continue
                if len(parts) < 6:
                    continue
                try:
                    role_val = int(parts[4]) if parts[4].strip() else 3
                except (ValueError, TypeError):
                    role_val = 3
                is_blocked = parts[5].strip() == "True"
                data.append(
                    UserModel(
                        id=int(parts[0]),
                        username=parts[1],
                        email=parts[2],
                        password=hash_password(parts[3]),
                        roleId=role_val,
                        isBlocked=is_blocked,
                    )
                )
        log_success(f"Loaded {len(data)} users.")
    except FileNotFoundError as e:
        log_issue("users.csv not found — users will not be seeded", exc=e, path=path)
    except Exception as e:
        log_issue("Unexpected error reading users", exc=e, path=path)
    return data


def _read_avatars() -> list:
    """
    Read avatars from CSV file and return a list of AvatarModel instances.

    Returns:
        list: A list of AvatarModel instances read from the CSV file.
    """
    path = "files/avatars.csv"
    data = []
    log_check(f"Reading avatars from {path}...")
    try:
        with open(path, "r", encoding="utf-8-sig", newline="") as f:
            for parts in csv.reader(f):  # expected: id,userID,avatar
                if parts[0] == "id":
                    continue
                if len(parts) < 3:
                    continue
                try:
                    row_id = int(parts[0]) if parts[0].strip() else None
                except Exception:
                    row_id = None
                try:
                    user_id = int(parts[1])
                except Exception:
                    continue
                avatar_path = parts[2].strip()
                if not avatar_path:
                    continue
                data.append(
                    AvatarModel(
                        id=row_id,
                        userId=user_id,
                        avatar=avatar_path,
                    )
                )
        log_success(f"Loaded {len(data)} avatars from avatars.csv.")
    except FileNotFoundError as e:
        log_issue(
            "avatars.csv not found — avatars will not be seeded", exc=e, path=path
        )
    except Exception as e:
        log_issue("Unexpected error reading avatars.csv", exc=e, path=path)
    return data


def _read_categories() -> list:
    """
    Read categories from CSV file and return a list of CategoryModel instances.

    Returns:
        list: A list of CategoryModel instances read from the CSV file.
    """

    path = "files/categories.csv"
    data = []
    log_check(f"Reading categories from {path}...")
    try:
        with open(path, "r", encoding="utf-8-sig", newline="") as f:
            for parts in csv.reader(f):  # expected: id,category
                if parts[0] == "id":
                    continue
                if len(parts) < 2:
                    continue
                data.append(CategoryModel(id=int(parts[0]), category=parts[1]))
        log_success(f"Loaded {len(data)} categories.")
    except FileNotFoundError as e:
        log_issue(
            "categories.csv not found — categories will not be seeded", exc=e, path=path
        )
    except Exception as e:
        log_issue("Unexpected error reading categories", exc=e, path=path)
    return data


def _read_albums() -> list:
    """
    Read albums from CSV file and return a list of AlbumModel instances.

    Returns:
        list: A list of AlbumModel instances read from the CSV file.
    """

    path = "files/albuns.csv"
    data = []
    log_check(f"Reading albums from {path}...")
    try:
        with open(path, "r", encoding="utf-8-sig", newline="") as f:
            for parts in csv.reader(f):  # expected: id,name,creatorID
                if parts[0] == "id":
                    continue
                if len(parts) < 3:
                    continue
                data.append(
                    AlbumModel(id=int(parts[0]), name=parts[1], creatorId=int(parts[2]))
                )
        log_success(f"Loaded {len(data)} albums.")
    except FileNotFoundError as e:
        log_issue("albuns.csv not found — albums will not be seeded", exc=e, path=path)
    except Exception as e:
        log_issue("Unexpected error reading albums", exc=e, path=path)
    return data


def _read_photos() -> list:
    """
    Read photos from CSV file and return a list of PhotoModel instances.

    Returns:
        list: A list of PhotoModel instances read from the CSV file.
    """

    path = "files/photos.csv"
    data = []
    log_check(f"Reading photos from {path}...")
    try:
        with open(path, "r", encoding="utf-8-sig", newline="") as f:
            for parts in csv.reader(
                f
            ):  # expected: id,description,publishedDate,categoryID,albumID
                if parts[0] == "id":
                    continue
                if len(parts) < 5:
                    continue
                try:
                    album_id = int(parts[4])
                except Exception:
                    # malformed or missing album id — skip this row
                    continue
                try:
                    published_date = datetime.fromisoformat(parts[2])
                except Exception:
                    published_date = datetime.now()
                data.append(
                    PhotoModel(
                        id=int(parts[0]),
                        description=parts[1],
                        publishedDate=published_date,
                        categoryId=int(parts[3]),
                        albumId=album_id,
                    )
                )
        log_success(f"Loaded {len(data)} photos.")
    except FileNotFoundError as e:
        log_issue("photos.csv not found — photos will not be seeded", exc=e, path=path)
    except Exception as e:
        log_issue("Unexpected error reading photos", exc=e, path=path)
    return data


def _read_photo_image() -> list:
    """
    Read photo images from CSV file and return a list of PhotoImageModel instances.

    Returns:
        list: A list of PhotoImageModel instances read from the CSV file.
    """

    path = "files/photo_image.csv"
    data = []
    log_check(f"Reading photo images from {path}...")
    try:
        with open(path, "r", encoding="utf-8-sig", newline="") as f:
            for parts in csv.reader(f):  # expected: id,photoID,image
                if parts[0] == "id":
                    continue
                if len(parts) < 3:
                    continue
                data.append(
                    PhotoImageModel(
                        id=int(parts[0]),
                        photoId=int(parts[1]),
                        image=parts[2],
                    )
                )
        log_success(f"Loaded {len(data)} photo images.")
    except FileNotFoundError:
        log_check(f"{path} not found — photo images will not be seeded")
    except Exception as e:
        log_issue("Unexpected error reading photo images", exc=e, path=path)
    return data


def _read_ratings() -> list:
    """
    Read ratings from CSV file and return a list of RatingModel instances.

    Returns:
        list: A list of RatingModel instances read from the CSV file.
    """

    path = "files/ratings.csv"
    data = []
    log_check(f"Reading ratings from {path}...")
    try:
        with open(path, "r", encoding="utf-8-sig", newline="") as f:
            for parts in csv.reader(f):  # expected: id,userID,photoID,rating
                if parts[0] == "id":
                    continue
                if len(parts) < 4:
                    continue
                data.append(
                    RatingModel(
                        id=int(parts[0]),
                        userId=int(parts[1]),
                        photoId=int(parts[2]),
                        rating=int(parts[3]),
                    )
                )
        log_success(f"Loaded {len(data)} ratings.")
    except FileNotFoundError:
        log_check(f"{path} not found — ratings will not be seeded")
    except Exception as e:
        log_issue("Unexpected error reading ratings", exc=e, path=path)
    return data


def _read_likes() -> list:
    """
    Read likes from CSV file and return a list of LikeModel instances.

    Returns:
        list: A list of LikeModel instances read from the CSV file.
    """

    path = "files/likes.csv"
    data = []
    log_check(f"Reading likes from {path}...")
    try:
        with open(path, "r", encoding="utf-8-sig", newline="") as f:
            for parts in csv.reader(f):  # expected: id,userID,photoID
                if parts[0] == "id":
                    continue
                if len(parts) < 3:
                    continue
                data.append(
                    LikeModel(
                        id=int(parts[0]),
                        userId=int(parts[1]),
                        photoId=int(parts[2]),
                    )
                )
        log_success(f"Loaded {len(data)} likes.")
    except FileNotFoundError as e:
        log_issue("likes.csv not found — likes will not be seeded", exc=e, path=path)
    except Exception as e:
        log_issue("Unexpected error reading likes", exc=e, path=path)
    return data


def _read_follows() -> list:
    """
    Read follows from CSV file and return a list of FollowModel instances.

    Returns:
        list: A list of FollowModel instances read from the CSV file.
    """

    path = "files/follows.csv"
    data = []
    log_check(f"Reading follows from {path}...")
    try:
        with open(path, "r", encoding="utf-8-sig", newline="") as f:
            for parts in csv.reader(f):  # expected: id,followerID,followedID
                if parts[0] == "id":
                    continue
                if len(parts) < 3:
                    continue
                data.append(
                    FollowModel(
                        id=int(parts[0]),
                        followerId=int(parts[1]),
                        followedId=int(parts[2]),
                    )
                )
        log_success(f"Loaded {len(data)} follows.")
    except FileNotFoundError as e:
        log_issue(
            "follows.csv not found — follows will not be seeded", exc=e, path=path
        )
    except Exception as e:
        log_issue("Unexpected error reading follows", exc=e, path=path)
    return data


def _read_notifications() -> list:
    """
    Read notifications from CSV file and return a list of NotificationModel instances.

    Returns:
        list: A list of NotificationModel instances read from the CSV file.
    """

    path = "files/notifications.csv"
    data = []
    log_check(f"Reading notifications from {path}...")
    try:
        with open(path, "r", encoding="utf-8-sig", newline="") as f:
            for parts in csv.reader(f):
                if parts[0] == "id":
                    continue
                if len(parts) < 9:
                    continue
                data.append(
                    NotificationModel(
                        id=int(parts[0]),
                        typeId=int(parts[1]),
                        recipientId=int(parts[2]),
                        senderId=int(parts[3]),
                        photoId=int(parts[4]) if parts[4].strip() else None,
                        albumId=int(parts[5]) if parts[5].strip() else None,
                        commentId=int(parts[6]) if parts[6].strip() else None,
                        message=parts[7],
                        isRead=parts[8].strip() == "True",
                    )
                )
        log_success(f"Loaded {len(data)} notifications.")
    except FileNotFoundError as e:
        log_issue(
            "notifications.csv not found — notifications will not be seeded",
            exc=e,
            path=path,
        )
    except Exception as e:
        log_issue("Unexpected error reading notifications", exc=e, path=path)
    return data


def _read_comments(valid_photo_ids: set) -> list:
    """
    Read comments from CSV file and return a list of CommentModel instances.

    Args:
        valid_photo_ids (set): A set of valid photo IDs to filter comments.

    Returns:
        list: A list of CommentModel instances read from the CSV file.
    """
    path = "files/comments.csv"
    data = []
    log_check(f"Reading comments from {path}...")
    try:
        with open(path, "r", encoding="utf-8-sig", newline="") as f:
            for parts in csv.reader(f):  # expected: id,authorID,comment,photoID
                if parts[0] == "id":
                    continue
                if len(parts) < 4:
                    continue
                photo_id = int(parts[3])
                if photo_id not in valid_photo_ids:
                    continue
                data.append(
                    CommentModel(
                        id=int(parts[0]),
                        authorId=int(parts[1]),
                        comment=parts[2],
                        photoId=photo_id,
                    )
                )
        log_success(f"Loaded {len(data)} comments.")
    except FileNotFoundError as e:
        log_issue(
            "comments.csv not found — comments will not be seeded", exc=e, path=path
        )
    except Exception as e:
        log_issue("Unexpected error reading comments", exc=e, path=path)
    return data


def _read_favorites() -> list:
    """
    Read favorites from CSV file and return a list of FavoriteModel instances.

    Returns:
        list: A list of FavoriteModel instances read from the CSV file.
    """
    path = "files/favorites.csv"
    data = []
    log_check(f"Reading favorites from {path}...")
    try:
        with open(path, "r", encoding="utf-8-sig", newline="") as f:
            for parts in csv.reader(f):  # expected: id,albumID,userID
                if parts[0] == "id":
                    continue
                if len(parts) < 3:
                    continue
                data.append(
                    FavoriteModel(
                        id=int(parts[0]),
                        albumId=int(parts[1]),
                        userId=int(parts[2]),
                    )
                )
        log_success(f"Loaded {len(data)} favorites.")
    except FileNotFoundError as e:
        log_issue(
            "favorites.csv not found — favorites will not be seeded", exc=e, path=path
        )
    except Exception as e:
        log_issue("Unexpected error reading favorites", exc=e, path=path)
    return data


def _read_contacts() -> list:
    """
    Read contacts from CSV file and return a list of ContactModel instances.

    Returns:
        list: A list of ContactModel instances read from the CSV file.
    """
    path = "files/contacts.csv"
    data = []
    log_check(f"Reading contacts from {path}...")
    try:
        with open(path, "r", encoding="utf-8-sig", newline="") as f:
            for parts in csv.reader(f):  # expected: id,title,message,userID
                if parts[0] == "id":
                    continue
                if len(parts) < 4:
                    continue
                data.append(
                    ContactModel(
                        id=int(parts[0]),
                        title=parts[1],
                        message=parts[2],
                        userId=int(parts[3]),
                    )
                )
        log_success(f"Loaded {len(data)} contacts.")
    except FileNotFoundError as e:
        log_issue(
            "contacts.csv not found — contacts will not be seeded", exc=e, path=path
        )
    except Exception as e:
        log_issue("Unexpected error reading contacts", exc=e, path=path)
    return data


def _read_notification_types() -> list:
    """
    Read notification types from CSV file and return a list of NotificationTypeModel instances.

    Returns:
        list: A list of NotificationTypeModel instances read from the CSV file.
    """
    path = "files/notification_types.csv"
    data = []
    log_check(f"Reading notification types from {path}...")
    try:
        with open(path, "r", encoding="utf-8", newline="") as f:
            for parts in csv.reader(f):  # expected: id,type,label,isEnabled
                if parts[0] == "id":
                    continue
                if len(parts) < 4:
                    continue
                data.append(
                    NotificationTypeModel(
                        id=int(parts[0]),
                        type=parts[1],
                        label=parts[2],
                        isEnabled=parts[3].strip() == "True",
                    )
                )
        log_success(f"Loaded {len(data)} notification types.")
    except FileNotFoundError as e:
        log_issue(
            "notification_types.csv not found — notification types will not be seeded",
            exc=e,
            path=path,
        )
    except Exception as e:
        log_issue("Unexpected error reading notification types", exc=e, path=path)
    return data


def _read_all() -> dict:
    """
    Read all CSVs in a dependency-safe order and return a dict of lists.

    Returns:
        dict: A dictionary where keys are table names and values are lists of ORM instances read from
    """
    roles = _read_roles()
    categories = _read_categories()
    users = _read_users()
    avatars = _read_avatars()
    albums = _read_albums()
    photos = _read_photos()
    valid_photo_ids = {p.id for p in photos}
    photo_image = _read_photo_image()
    ratings = _read_ratings()
    comments = _read_comments(valid_photo_ids)
    favorites = _read_favorites()
    contacts = _read_contacts()
    notification_types = _read_notification_types()
    notifications = _read_notifications()
    follows = _read_follows()
    likes = _read_likes()

    return {
        "roles": roles,
        "categories": categories,
        "users": users,
        "avatars": avatars,
        "albums": albums,
        "photos": photos,
        "photo_image": photo_image,
        "ratings": ratings,
        "comments": comments,
        "favorites": favorites,
        "contacts": contacts,
        "notification_types": notification_types,
        "notifications": notifications,
        "follows": follows,
        "likes": likes,
    }


# Ordered keys for insertion/merge so foreign keys resolve correctly
_CSV_ORDER = [
    "roles",
    "categories",
    "users",
    "avatars",
    "albums",
    "photos",
    "photo_image",
    "ratings",
    "comments",
    "favorites",
    "contacts",
    "notification_types",
    "notifications",
    "follows",
    "likes",
]

# ── Public API ────────────────────────────────────────────────────────────────


def sync_static_data() -> None:
    """
    Upsert ALL CSV data into the database on every app startup.
    Existing rows are updated, new rows are inserted.
    Safe to call repeatedly — no duplicates are created.
    """
    log_check("Syncing all data from CSV files...")

    data = _read_all()

    try:
        with SessionLocal() as session:
            with session.begin():
                for key in _CSV_ORDER:
                    for obj in data.get(key, []):
                        session.merge(obj)
                    session.flush()
    except Exception as e:
        log_issue(
            "Failed to sync CSV data to the database — schema may be stale",
            exc=e,
            path="photoshow.db",
        )
        log_issue("Run 'python main.py --resetDB' to drop and rebuild the database")
        return

    log_success("All CSV data synced to database.")


def migrate() -> None:
    """
    Called on every app startup.
    Initializes the database and syncs all data from CSV files.
    """
    try:
        log_check("Initializing database...")
        init_db()
        log_success("Database initialized.")
    except Exception as e:
        log_issue("Database initialization failed", exc=e, path="photoshow.db")
        import sys

        sys.exit(1)
    sync_static_data()
