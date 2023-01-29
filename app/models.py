# coding: utf-8
from app.database import Base
from sqlalchemy.sql import func
from sqlalchemy import TIMESTAMP, Column, Boolean, UniqueConstraint, \
                       String, Boolean, Date, Integer, Identity, ForeignKey

metadata = Base.metadata


class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, Identity(cycle=True), primary_key=True)
    email = Column(String, nullable=False)
    password = Column(String, nullable=False)
    first_name = Column(String(20), nullable=True)
    last_name = Column(String(20), nullable=True)
    birth_date = Column(Date, nullable=True)
    server = Column(String(20), nullable=True)
    is_activated = Column(Boolean, nullable=True)
    time_created = Column(TIMESTAMP(timezone=True), server_default=func.now())
    time_updated = Column(TIMESTAMP(timezone=True), onupdate=func.now())
    __table_args__ = (UniqueConstraint("email", "server",
                                       name="already_existed"),)


class Validation(Base):
    __tablename__ = 'validation'
    id = Column(Integer, Identity(cycle=True), primary_key=True)
    user_id = Column(Integer, ForeignKey("user.id"))
    pin_code = Column(String(4), nullable=False)
    url = Column(String(20), nullable=False, unique=True)
    time_email_sent = Column(TIMESTAMP(timezone=True),
                             server_default=func.now(),
                             onupdate=func.now())
