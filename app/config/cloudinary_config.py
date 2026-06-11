import os

# ---------------------------------------------------------------------------
# Cloudinary cloud credentials
# Read from the .env file at project root (loaded by python-dotenv in main.py)
# ---------------------------------------------------------------------------
CLOUDINARY_CLOUD_NAME: str = os.getenv("CLOUDINARY_CLOUD_NAME", "")
CLOUDINARY_API_KEY: str = os.getenv("CLOUDINARY_API_KEY", "")
CLOUDINARY_API_SECRET: str = os.getenv("CLOUDINARY_API_SECRET", "")

CLOUDINARY_OPTIONS: dict = {
    "cloud_name": CLOUDINARY_CLOUD_NAME,
    "api_key": CLOUDINARY_API_KEY,
    "api_secret": CLOUDINARY_API_SECRET,
}

# ---------------------------------------------------------------------------
# Cloudinary folder structure
# Separate dev (hardcoded seed data) and prod (user uploads) environments:
#   dev/profile_avatars  → CSV seed avatars (untouchable, default data)
#   dev/photos_gallery   → CSV seed photos (untouchable, default data)
#   prod/profile_avatars → User-uploaded avatars (managed dynamically)
#   prod/photos_gallery  → User-uploaded photos (managed dynamically)
#
# This separation allows:
#   - Reset DB keeps dev assets in cloud, deletes only prod assets
#   - Easy identification: dev assets have simple names, prod have full paths
#   - Default state always recoverable from dev folder
# ---------------------------------------------------------------------------
_ROOT_FOLDER = "photo-show"
_DEV_ENV = "dev"
_PROD_ENV = "prod"

# Seed data (from CSV) lives in dev folders - NEVER delete from cloud
FOLDER_AVATARS_DEV: str = f"{_ROOT_FOLDER}/{_DEV_ENV}/profile_avatars"
FOLDER_PHOTOS_DEV: str = f"{_ROOT_FOLDER}/{_DEV_ENV}/photos_gallery"

# User uploads go to prod folders - can be deleted/replaced during reset/restore
FOLDER_AVATARS_PROD: str = f"{_ROOT_FOLDER}/{_PROD_ENV}/profile_avatars"
FOLDER_PHOTOS_PROD: str = f"{_ROOT_FOLDER}/{_PROD_ENV}/photos_gallery"

# Backwards compatibility: keep old constants pointing to prod (where uploads go)
FOLDER_AVATARS: str = FOLDER_AVATARS_PROD
FOLDER_PHOTOS: str = FOLDER_PHOTOS_PROD

# ---------------------------------------------------------------------------
# Default avatar fallback URL
# Upload your default_avatar image to Cloudinary once and set this variable
# in your .env file.  If left empty the UI renders a blank placeholder.
# ---------------------------------------------------------------------------
DEFAULT_AVATAR_URL: str = os.getenv("DEFAULT_AVATAR_URL", "")
DEFAULT_AVATAR_PUBLIC_ID: str = os.getenv("DEFAULT_AVATAR_PUBLIC_ID", "")
