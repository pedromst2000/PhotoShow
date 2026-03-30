"""
This file marks the 'state' directory as a Python package.

Global application state management.

This module provides centralized state management for the application,
including user session handling and authentication state.
"""

from app.core.state.session import UserSession, session

__all__ = ["UserSession", "session"]
