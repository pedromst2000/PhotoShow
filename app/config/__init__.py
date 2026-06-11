"""
Configuration module for PhotoShow application.

This package centralizes all environment-based configuration:
- cloudinary_config.py: Cloudinary API credentials, folder structure, environment detection
- Any additional configs (database, logging, etc.) follow the same pattern

All configs read from environment variables (loaded by python-dotenv in main.py at startup).
This supports multi-environment deployments (dev per-developer, prod shared cloud storage).
"""
