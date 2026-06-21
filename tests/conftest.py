"""
Root pytest configuration — applied to all test suites.

Sets environment variables BEFORE any app module is imported, so
cloudinary config and other env-dependent code work without real credentials.
"""

import os

# Must be the very first thing — before any app import resolves env vars.
os.environ.setdefault("RUNNING_TESTS", "1")
os.environ.setdefault("CLOUDINARY_CLOUD_NAME", "test_cloud")
os.environ.setdefault("CLOUDINARY_API_KEY", "test_key")
os.environ.setdefault("CLOUDINARY_API_SECRET", "test_secret")
os.environ.setdefault("DEFAULT_AVATAR_URL", "https://example.com/default_avatar.jpg")
os.environ.setdefault("DEFAULT_AVATAR_PUBLIC_ID", "test/default_avatar")
