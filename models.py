from sqlalchemy import (
    Column,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Router(Base):
    __tablename__ = 'routers'
    __table_args__ = (UniqueConstraint('host', 'password_hash', name='uq_router_host_password_hash'),)

    id = Column(Integer, primary_key=True, autoincrement=True)
    host = Column(String, nullable=False)
    password_hash = Column(String, nullable=False)
    password_encrypted = Column(String, nullable=False)


class UserRouter(Base):
    __tablename__ = 'user_routers'

    user_id = Column(Integer, primary_key=True)
    router_id = Column(Integer, ForeignKey('routers.id'), primary_key=True)


class Device(Base):
    __tablename__ = 'devices'
    __table_args__ = (UniqueConstraint('router_id', 'name', name='uq_device_router_name'),)

    id = Column(Integer, primary_key=True, autoincrement=True)
    router_id = Column(Integer, ForeignKey('routers.id'), nullable=False)
    name = Column(String, nullable=False)
    mac = Column(String, nullable=False)
    wol = Column(Integer, nullable=False, default=0)


class UserState(Base):
    __tablename__ = 'user_state'

    user_id = Column(Integer, primary_key=True)
    current_router_id = Column(Integer, ForeignKey('routers.id'), nullable=True)
