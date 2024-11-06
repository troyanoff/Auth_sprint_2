# models/entity.py
import random
import uuid
from datetime import datetime

from sqlalchemy import (
    Column,
    DateTime,
    String,
    Table,
    ForeignKey,
    UniqueConstraint,
    PrimaryKeyConstraint,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from werkzeug.security import check_password_hash, generate_password_hash

from db.postgres import Base


user_role = Table(
    "user_role",
    Base.metadata,
    Column("user_id", ForeignKey("users.id"), primary_key=True),
    Column("role_id", ForeignKey("roles.id"), primary_key=True),
)


class User(Base):
    __tablename__ = "users"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )
    login = Column(String(255), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    first_name = Column(String(50))
    last_name = Column(String(50))
    created_at = Column(DateTime, default=datetime.now)
    refresh_token = Column(String(1000))
    roles = relationship(
        "Role", secondary=user_role, back_populates="users", lazy="joined"
    )
    login_history = relationship("LoginHistory", lazy="joined")

    def __init__(
        self, login: str, password: str, first_name: str, last_name: str
    ) -> None:
        self.login = login
        self.password = self.password = generate_password_hash(password)
        self.first_name = first_name
        self.last_name = last_name

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password, password)

    def __repr__(self) -> str:
        return f"<User {self.login}>"


class Role(Base):
    __tablename__ = "roles"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )
    name = Column(String(50))
    service = Column(String(50))
    users = relationship(
        "User", secondary=user_role, back_populates="roles", lazy="joined"
    )

    __table_args__ = (UniqueConstraint("name", "service", name="_name_service_uc"),)

    def __init__(self, name: str, service: str) -> None:
        self.name = name
        self.service = service

    def __repr__(self) -> str:
        return f"<Role {self.service}:{self.name}>"


class LoginHistory(Base):
    __tablename__ = "login_history"
    __table_args__ = (
        PrimaryKeyConstraint("id", "random_tag"),
        {
            "postgresql_partition_by": "LIST (random_tag)",
        },
    )

    id = Column(
        UUID(as_uuid=True),
        default=uuid.uuid4,
        nullable=False,
    )
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    login_datetime = Column(DateTime, default=datetime.now)
    random_tag = Column(String(50), default=random.choice(["left", "right"]))


class LoginNetwork(Base):
    __tablename__ = "login_network"

    id = Column(
        UUID(as_uuid=True),
        default=uuid.uuid4,
        primary_key=True,
        nullable=False,
        unique=True,
    )
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    network = Column(String(50), default='yandex')
