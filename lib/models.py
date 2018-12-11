'''

    mission.lib.models

'''
# System level imports
import os, sys, datetime, uuid, json
from sqlalchemy import Column, ForeignKey, Integer, String, Table, DateTime, Boolean, BLOB
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

from mission.lib.database import Base

class RingDevice(Base):
    __tablename__ = 'ring_devices'
    id = Column(Integer, primary_key=True)
    device_id = Column(String(100))
    device_type = Column(String(100))
    name = Column(String(100))
    last_recording_id = Column(String(100))
    connection_status = Column(String(100))
    events = relationship("RingEvent", back_populates='device')
    
class RingEvent(Base):
    __tablename__ = 'ring_events'
    id = Column(Integer, primary_key=True)
    device = relationship("RingDevice", back_populates='events')
    device_id = Column(Integer, ForeignKey('ring_devices.id'))
    event_id = Column(String(512), nullable=True)
    date = Column(DateTime)
    answered = Column(Boolean)
    kind = Column(String(100))
    snapshot_url = Column(String(512), nullable=True)
    duration = Column(Integer)
    
class Doorbell(Base):
    __tablename__ = 'doorbells'
    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    device_id = Column(String(100))
    last_recording_id = Column(String(100))
    connection_status = Column(String(100))
    snapshot_url = Column(String(256))
        
class RingCamera(Base):
    __tablename__ = 'ring_cameras'
    id = Column(Integer, primary_key=True)
    device_id = Column(String(100))
    name = Column(String(100))
    last_recording_id = Column(String(100))
    connection_status = Column(String(100))
    snapshot_url = Column(String(256))
    
class NestCamera(Base):
    __tablename__ = 'nest_cameras'
    id = Column(Integer, primary_key=True)
