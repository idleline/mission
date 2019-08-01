'''
    mission.mod_auth.models
    
    Defines the DB models for mission authentication
    
'''
# Import system dependencies
import os, sys, datetime

# Flask dependencies
from flask import g

# Import SQLAlchemy dependencies
from sqlalchemy import Column, ForeignKey, Integer, String, Table, DateTime, func, TypeDecorator, String, Text, Boolean, BLOB, Binary
from sqlalchemy.orm import relationship, backref
from sqlalchemy import create_engine
from flask_security import UserMixin, RoleMixin

# Import application objects
from mission.lib.database import Base

roles_users = Table('roles_users', Base.metadata,
        Column('user_id', Integer, ForeignKey('users.id')),
        Column('role_id', Integer, ForeignKey('role.id')))

class Role(Base, RoleMixin):
    __tablename__ = 'role'
    id = Column(Integer, primary_key=True)
    name = Column(String(80), unique=True)
    description = Column(String(255))
    groups = relationship('UserGroup', back_populates='default_role')

class User(Base, UserMixin):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String(255), unique=True)
    firstname = Column(String(255))
    lastname = Column(String(255))   
    email = Column(String(255), unique=True) 
    last_login_at = Column(DateTime)
    current_login_at = Column(DateTime)
    last_login_ip = Column(String(255))
    current_login_ip = Column(String(255))
    login_count = Column(Integer)
    active = Column(Boolean)
    password = Column(Binary(64))
    notifications = relationship('Notification', back_populates='user')
    user_profile = relationship('UserProfile', uselist=False, back_populates='user')
    roles = relationship('Role', secondary=roles_users, backref=backref('users', lazy='dynamic'))

class UserGroup(Base):
    __tablename__ = 'user_group'
    id = Column(Integer, primary_key=True)
    name = Column(String(128))
    default_role = relationship('Role', back_populates='groups')
    default_role_id = Column(Integer, ForeignKey('role.id'))
    
class UserProfile(Base):
    __tablename__ = 'userprofile'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship('User', back_populates='user_profile')
    created = Column(DateTime)
    last_active = Column(DateTime)
    avatar = Column(String(100))

class Notification(Base):
    __tablename__ = 'notifications'
    id = Column(Integer, primary_key=True)
    creator = Column(String(100))
    title = Column(String(100))
    content = Column(BLOB) 
    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship('User', back_populates='notifications')
    was_read = Column(Boolean)

class Alert(Base):
    __tablename__ = 'alerts'
    id = Column(Integer, primary_key=True)
    alert = Column(String(100))
    title = Column(String(100))
    content = Column(BLOB) 
    was_read = Column(Boolean)
    
    def __init__(self, alert, title, content):
        self.alert = alert
        self.title = title
        self.content = content
        self.was_read = False

class ValidateEmail(Base):
    __tablename__ = 'valid_email'
    id = Column(Integer, primary_key=True)
    created = Column(DateTime)
    user = Column(Integer)
    eid = Column(String(100))
    vid = Column(String(100))
    activated = Column(Boolean)
    