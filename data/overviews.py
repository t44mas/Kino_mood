import sqlalchemy
from flask_login import UserMixin
from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin

from .db_session import SqlAlchemyBase


class Overview(SqlAlchemyBase, SerializerMixin, UserMixin):
    __tablename__ = 'overviews'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    rate = sqlalchemy.Column(sqlalchemy.NUMERIC, nullable=False, default=0)
    user_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id"), nullable=False)
    book_id = sqlalchemy.Column(sqlalchemy.String, nullable=False)

    liked = orm.relationship('User')
