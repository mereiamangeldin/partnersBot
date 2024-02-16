from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
import datetime

Base = declarative_base()


class Admin(Base):
    __tablename__ = 'admins'

    id = Column(String, primary_key=True)
    name = Column(String)
    admin_do_input = Column(Boolean, default=False)
    new_admin_name = Column(String, nullable=True)
    new_channel_link = Column(String, nullable=True)
    admin_input_val = Column(String, nullable=True)


class User(Base):
    __tablename__ = 'users'

    id = Column(String, primary_key=True)
    invited_from_id = Column(String, default='0')
    balance = Column(Integer, default=0)
    language = Column(String, default='RU')
    view_post_time = Column(DateTime, default=datetime.datetime.now)
    current_channel_id = Column(String, default='0')
    username = Column(String, nullable=True)


class Partner(Base):
    __tablename__ = 'partners'
    id = Column(String, primary_key=True)
    link = Column(String, nullable=False)


class NumericVariable(Base):
    __tablename__ = 'numeric_variables'
    id = Column(Integer, primary_key=True)
    total_users_amount = Column(Integer, default=0)
    active_users_amount = Column(Integer, default=0)
    passive_users_amount = Column(Integer, default=0)

    invite_friend_price = Column(Integer, default=0)
    join_channel_price = Column(Integer, default=0)
    view_post_price = Column(Integer, default=0)
    min_withdrawal_amount = Column(Integer, default=0)
    min_invited_friends = Column(Integer, default=0)


class Subscription(Base):
    __tablename__ = 'subscriptions'
    id = Column(Integer, primary_key=True)
    user_id = Column(String, ForeignKey('users.id'))
    channel_id = Column(String, ForeignKey('partners.id'))
