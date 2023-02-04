import sqlalchemy as sa
from .base import Base


class UserView(Base):
    __tablename__ = "user"

    id = sa.Column(sa.BigInteger, primary_key=True)
    fullname = sa.Column(sa.String)
    username = sa.Column(sa.String)
    team = sa.Column(sa.String)
    role = sa.Column(sa.String)
    city = sa.Column(sa.String)
    traineeship = sa.Column(sa.String)
    profession = sa.Column(sa.String)
    start_year = sa.Column(sa.String)
    end_year = sa.Column(sa.String)
    phone_number = sa.Column(sa.String)
    email = sa.Column(sa.String)
    active = sa.Column(sa.Integer)
    role_id = sa.Column(sa.Integer)
