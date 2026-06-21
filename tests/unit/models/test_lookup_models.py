"""Unit tests for lookup models: Role, NotificationType, ReportReason."""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.db.engine import Base
from app.core.db.models.notification_types import NotificationTypeModel
from app.core.db.models.report_reason import ReportReasonModel
from app.core.db.models.role import RoleModel


@pytest.fixture
def test_db():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


# ─── Role Model Tests ──────────────────────────────────────────
class TestRoleModel:
    """Test RoleModel lookup."""

    def test_to_dict(self, test_db):
        role = RoleModel(role="admin")
        test_db.add(role)
        test_db.commit()

        result = role.to_dict()
        assert result["role"] == "admin"

    def test_role_unique(self, test_db):
        role1 = RoleModel(role="admin")
        test_db.add(role1)
        test_db.commit()

        role2 = RoleModel(role="admin")
        test_db.add(role2)

        with pytest.raises(Exception):
            test_db.commit()

    def test_get_by_name(self, test_db):
        """RoleModel.get_by_name() - actual method."""
        role = RoleModel(role="regular")
        test_db.add(role)
        test_db.commit()

        retrieved = RoleModel.get_by_name(test_db, "regular")
        assert retrieved is not None

    def test_get_all(self, test_db):
        test_db.add_all([RoleModel(role="admin"), RoleModel(role="regular")])
        test_db.commit()

        all_roles = RoleModel.get_all(test_db)
        assert len(all_roles) >= 2


# ─── NotificationType Model Tests ──────────────────────────────────
class TestNotificationTypeModel:
    """Test NotificationTypeModel lookup."""

    def test_to_dict(self, test_db):
        notif_type = NotificationTypeModel(type="follow", label="User Follow")
        test_db.add(notif_type)
        test_db.commit()

        result = notif_type.to_dict()
        assert result["type"] == "follow"
        assert result["label"] == "User Follow"

    def test_type_unique(self, test_db):
        type1 = NotificationTypeModel(type="like", label="Photo Liked")
        test_db.add(type1)
        test_db.commit()

        type2 = NotificationTypeModel(type="like", label="Like")
        test_db.add(type2)

        with pytest.raises(Exception):
            test_db.commit()

    def test_get_by_id(self, test_db):
        notif_type = NotificationTypeModel(type="comment", label="Comment Added")
        test_db.add(notif_type)
        test_db.commit()

        retrieved = NotificationTypeModel.get_by_id(test_db, notif_type.id)
        assert retrieved is not None

    def test_get_by_type(self, test_db):
        """Test NotificationTypeModel.get_by_type() method."""
        notif_type = NotificationTypeModel(type="mention", label="Mentioned")
        test_db.add(notif_type)
        test_db.commit()

        retrieved = NotificationTypeModel.get_by_type(test_db, "mention")
        assert retrieved is not None

    def test_get_all(self, test_db):
        test_db.add_all(
            [
                NotificationTypeModel(type="follow", label="Follow"),
                NotificationTypeModel(type="like", label="Like"),
            ]
        )
        test_db.commit()

        all_types = NotificationTypeModel.get_all(test_db)
        assert len(all_types) >= 2


# ─── ReportReason Model Tests ──────────────────────────────────────
class TestReportReasonModel:
    """Test ReportReasonModel lookup."""

    def test_to_dict(self, test_db):
        reason = ReportReasonModel(label="Inappropriate")
        test_db.add(reason)
        test_db.commit()

        result = reason.to_dict()
        assert result["label"] == "Inappropriate"

    def test_label_unique(self, test_db):
        reason1 = ReportReasonModel(label="Spam")
        test_db.add(reason1)
        test_db.commit()

        reason2 = ReportReasonModel(label="Spam")
        test_db.add(reason2)

        with pytest.raises(Exception):
            test_db.commit()

    def test_get_by_label(self, test_db):
        """ReportReasonModel.get_by_label() - actual method."""
        reason = ReportReasonModel(label="Offensive")
        test_db.add(reason)
        test_db.commit()

        retrieved = ReportReasonModel.get_by_label(test_db, "Offensive")
        assert retrieved is not None

    def test_get_labels(self, test_db):
        """ReportReasonModel.get_labels() returns list of label strings."""
        test_db.add_all(
            [ReportReasonModel(label="Spam"), ReportReasonModel(label="Harassment")]
        )
        test_db.commit()

        labels = ReportReasonModel.get_labels(test_db)
        assert "Spam" in labels
        assert "Harassment" in labels
