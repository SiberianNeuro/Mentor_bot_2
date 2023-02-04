import sqlalchemy as sa

from .base import Base
from .user import User


class ExamStage(Base):
    __tablename__ = "lib_exam_stages"
    __table_args__ = {"extend_existing": True}

    id = sa.Column(sa.Integer, primary_key=True, unique=True, autoincrement=True)
    stage = sa.Column(sa.String(45))


class ExamResult(Base):
    __tablename__ = "lib_exam_results"
    __table_args__ = {"extend_existing": True}

    id = sa.Column(sa.Integer, primary_key=True, unique=True, autoincrement=True)
    result = sa.Column(sa.String(45))


class Exam(Base):
    __tablename__ = "exams"
    __table_args__ = {"extend_existing": True}

    id = sa.Column(sa.Integer, primary_key=True, unique=True, autoincrement=True)
    user_id = sa.Column(sa.Integer, sa.ForeignKey(f"{User.__tablename__}.id", ondelete="CASCADE", onupdate="CASCADE"))
    stage_id = sa.Column(sa.Integer, sa.ForeignKey(f'{ExamStage.__tablename__}.id', ondelete="CASCADE", onupdate="CASCADE"))
    result_id = sa.Column(sa.Integer, sa.ForeignKey(f'{ExamResult.__tablename__}.id', ondelete="CASCADE", onupdate="CASCADE"))
    document_id = sa.Column(sa.String)
    score_id = sa.Column(sa.DECIMAL)
    link = sa.Column(sa.String)
    date = sa.Column(sa.Date)
    retake_date = sa.Column(sa.Date)
    calls = sa.Column(sa.String)
