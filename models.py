# coding: utf-8
import uuid
from database import Base
from sqlalchemy import TIMESTAMP, Column, ForeignKey, Boolean,\
                       String, Boolean, text, Date, Integer, Identity

metadata = Base.metadata


class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, Identity(start=42, cycle=True), primary_key=True)
    email = Column(String, nullable=False)
    password = Column(String, nullable=False)
    first_name = Column(String(20), nullable=True)
    last_name = Column(String(20), nullable=True)
    birth_date = Column(Date, nullable=True)
    server = Column(String(20), nullable=True)
    key = Column(String(4), nullable=True)
    activated = Column(Boolean, nullable=True)
