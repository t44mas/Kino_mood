import datetime

import sqlalchemy
from flask_login import UserMixin
from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin

from .db_session import SqlAlchemyBase


class ViewedBook(SqlAlchemyBase, SerializerMixin, UserMixin):
    __tablename__ = 'viewedBook'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    user_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id"), nullable=False)
    book_id = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    viewed_at = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.utcnow)
    title = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    author = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    poster_url = sqlalchemy.Column(sqlalchemy.String, nullable=True)

    user = orm.relationship('User')
