import datetime
import sqlalchemy
from flask_login import UserMixin
from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin

from .db_session import SqlAlchemyBase


class Comment(SqlAlchemyBase, SerializerMixin, UserMixin):
    __tablename__ = 'comment'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    text = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    time_stamp = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.utcnow)
    user_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id"), nullable=False)
    book_id = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    user = orm.relationship('User', backref='comments')
