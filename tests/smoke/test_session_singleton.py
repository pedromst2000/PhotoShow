"""
Smoke tests — verify that UserSession singleton behaves correctly.

These tests ensure the session state management follows the singleton pattern
and exposes the expected public API for authentication state.
"""


class TestSessionSingleton:
    """UserSession must be a singleton and expose the expected public API."""

    def test_two_instantiations_return_same_object(self):
        from app.core.state.session import UserSession

        assert UserSession() is UserSession()

    def test_module_level_session_is_a_user_session(self):
        from app.core.state.session import UserSession, session

        assert isinstance(session, UserSession)

    def test_is_authenticated_property_returns_bool(self):
        from app.core.state.session import UserSession

        sess = UserSession()
        assert isinstance(sess.is_authenticated, bool)

    def test_logout_sets_unauthenticated(self):
        from app.core.state.session import UserSession

        sess = UserSession()
        # Log in with dummy data, then immediately log out
        sess.login(
            {"id": 999, "username": "_smoke_test_", "role": "regular"},
            is_new_user=False,
        )
        sess.logout()
        assert sess.is_authenticated is False
