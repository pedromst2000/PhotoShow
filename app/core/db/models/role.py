from datetime import datetime, timezone

from sqlalchemy import CheckConstraint, Column, DateTime, Integer, String

from app.core.db.engine import Base, SessionLocal


class RoleModel(Base):
    """
    RoleModel represents a user role in the database, with methods to retrieve roles.
    """

    __tablename__: str = "roles"

    __table_args__ = (
        CheckConstraint("id > 0 AND id < 10000000", name="ck_roles_id_range"),
        CheckConstraint("length(trim(role)) > 0", name="ck_roles_name_not_empty"),
        CheckConstraint("length(role) <= 25", name="ck_roles_name_maxlen"),
    )

    id: int = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    role: str = Column(String(25), unique=True, nullable=False)
    createdAt: DateTime = Column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updatedAt: DateTime = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    def to_dict(self) -> dict:
        """
        Convert the RoleModel instance to a dictionary.

        Returns:
            dict: A dictionary representation of the RoleModel instance.
        """
        return {
            "id": self.id,
            "role": self.role,
            "createdAt": self.createdAt,
            "updatedAt": self.updatedAt,
        }

    @classmethod
    def get_all(cls) -> list:
        """
        Retrieve all roles from the database and return them as a list of dictionaries.

        Returns:
            list: A list of dictionaries, each representing a role.
        """
        with SessionLocal() as session:
            return [r.to_dict() for r in session.query(cls).all()]

    @classmethod
    def get_by_name(cls, role_name: str) -> dict | None:
        """
        Retrieve a role by its name from the database.

        Args:
            role_name (str): The name of the role to retrieve.
        Returns:
            dict | None: A dictionary representing the role if found, otherwise None.
        """

        with SessionLocal() as session:
            r = session.query(cls).filter(cls.role.ilike(role_name)).first()
            return r.to_dict() if r else None
