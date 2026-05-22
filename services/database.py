"""
Database service - PostgreSQL (Railway) dan SQLite (local) dengan SQLAlchemy.
"""
import os
import logging
from datetime import datetime
from typing import Optional
from sqlalchemy import (
    create_engine, Column, Integer, BigInteger, String, Boolean,
    DateTime, Text, Enum as SAEnum, text
)
from sqlalchemy.orm import DeclarativeBase, sessionmaker, Session
from config.settings import DATABASE_URL, SQLITE_URL, USE_POSTGRES

logger = logging.getLogger(__name__)


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    telegram_id = Column(BigInteger, unique=True, nullable=False, index=True)
    username = Column(String(64), nullable=True)
    first_name = Column(String(128), nullable=True)
    is_banned = Column(Boolean, default=False)
    ban_reason = Column(Text, nullable=True)
    total_chats = Column(Integer, default=0)
    report_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_seen = Column(DateTime, default=datetime.utcnow)


class Report(Base):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, autoincrement=True)
    reporter_id = Column(BigInteger, nullable=False)
    reported_id = Column(BigInteger, nullable=False)
    reason = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    reviewed = Column(Boolean, default=False)


class EventLog(Base):
    __tablename__ = "event_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    event_type = Column(String(64), nullable=False)
    user_id = Column(BigInteger, nullable=True)
    detail = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


def get_engine():
    if USE_POSTGRES:
        url = DATABASE_URL
        if url.startswith("postgres://"):
            url = url.replace("postgres://", "postgresql://", 1)
        return create_engine(url, pool_pre_ping=True)
    else:
        return create_engine(SQLITE_URL, connect_args={"check_same_thread": False})


engine = get_engine()
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


def init_db():
    Base.metadata.create_all(bind=engine)
    logger.info("Database initialized.")


def get_session() -> Session:
    return SessionLocal()


def get_or_create_user(telegram_id: int, username: str = None, first_name: str = None) -> User:
    with get_session() as session:
        user = session.query(User).filter_by(telegram_id=telegram_id).first()
        if not user:
            user = User(telegram_id=telegram_id, username=username, first_name=first_name)
            session.add(user)
            session.commit()
            session.refresh(user)
        else:
            user.last_seen = datetime.utcnow()
            if username:
                user.username = username
            if first_name:
                user.first_name = first_name
            session.commit()
        return user


def is_user_banned(telegram_id: int) -> bool:
    with get_session() as session:
        user = session.query(User).filter_by(telegram_id=telegram_id).first()
        return user.is_banned if user else False


def ban_user(telegram_id: int, reason: str = None):
    with get_session() as session:
        user = session.query(User).filter_by(telegram_id=telegram_id).first()
        if user:
            user.is_banned = True
            user.ban_reason = reason
            session.commit()


def unban_user(telegram_id: int):
    with get_session() as session:
        user = session.query(User).filter_by(telegram_id=telegram_id).first()
        if user:
            user.is_banned = False
            user.ban_reason = None
            session.commit()


def add_report(reporter_id: int, reported_id: int, reason: str = None):
    with get_session() as session:
        report = Report(reporter_id=reporter_id, reported_id=reported_id, reason=reason)
        session.add(report)
        reported_user = session.query(User).filter_by(telegram_id=reported_id).first()
        if reported_user:
            reported_user.report_count += 1
        session.commit()


def log_event(event_type: str, user_id: int = None, detail: str = None):
    with get_session() as session:
        log = EventLog(event_type=event_type, user_id=user_id, detail=detail)
        session.add(log)
        session.commit()


def get_stats() -> dict:
    with get_session() as session:
        total_users = session.query(User).count()
        banned_users = session.query(User).filter_by(is_banned=True).count()
        total_reports = session.query(Report).count()
        pending_reports = session.query(Report).filter_by(reviewed=False).count()
        return {
            "total_users": total_users,
            "banned_users": banned_users,
            "total_reports": total_reports,
            "pending_reports": pending_reports,
        }


def get_recent_reports(limit: int = 10):
    with get_session() as session:
        return session.query(Report).order_by(Report.created_at.desc()).limit(limit).all()


def increment_chat_count(telegram_id: int):
    with get_session() as session:
        user = session.query(User).filter_by(telegram_id=telegram_id).first()
        if user:
            user.total_chats += 1
            session.commit()
