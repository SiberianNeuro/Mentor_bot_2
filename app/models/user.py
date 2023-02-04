import sqlalchemy as sa
from sqlalchemy.orm import relationship

from .base import Base


class Role(Base):
    __tablename__ = "lib_roles"

    id = sa.Column(sa.Integer, primary_key=True, unique=True, autoincrement=True)
    name = sa.Column(sa.String)
    is_superuser = sa.Column(sa.Integer)


class Traineeship(Base):
    __tablename__ = "lib_traineeships"

    id = sa.Column(sa.Integer, primary_key=True, unique=True, autoincrement=True)
    stage = sa.Column(sa.String)


class Division(Base):
    __tablename__ = "lib_divisions"

    id = sa.Column(sa.Integer, primary_key=True, unique=True, autoincrement=True)
    name = sa.Column(sa.String)
    team = relationship("Team", back_populates='division')


class Team(Base):
    __tablename__ = "lib_teams"

    id = sa.Column(sa.Integer, primary_key=True, unique=True, autoincrement=True)
    name = sa.Column(sa.String)
    division_id = sa.Column(sa.Integer, sa.ForeignKey(f"{Division.__tablename__}.id", ondelete="CASCADE", onupdate="CASCADE"),
                            nullable=False)
    division = relationship("Division", back_populates='team')


class User(Base):
    __tablename__ = "staffs"

    id = sa.Column(sa.Integer, primary_key=True, unique=True, autoincrement=True)
    fullname = sa.Column(sa.String)
    city = sa.Column(sa.String)
    role_id = sa.Column(sa.Integer, sa.ForeignKey(f"{Role.__tablename__}.id", ondelete="CASCADE", onupdate="CASCADE"))
    team_id = sa.Column(sa.Integer, sa.ForeignKey(f"{Team.__tablename__}.id", ondelete="CASCADE", onupdate="CASCADE"))
    traineeship_id = sa.Column(sa.Integer,
                               sa.ForeignKey(f"{Traineeship.__tablename__}.id", ondelete="CASCADE", onupdate="CASCADE"))
    profession = sa.Column(sa.String)
    start_year = sa.Column(sa.String)
    end_year = sa.Column(sa.String)
    birthdate = sa.Column(sa.Date)
    phone = sa.Column(sa.String)
    email = sa.Column(sa.String)
    username = sa.Column(sa.String)
    chat_id = sa.Column(sa.String)
    reg_date = sa.Column(sa.DateTime)
    active = sa.Column(sa.Integer)
    update_date = sa.Column(sa.DateTime)


