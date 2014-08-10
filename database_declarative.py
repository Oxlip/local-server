"""
sqlalchemy ORM for the local sqllite database.
"""

from sqlalchemy import Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.orm import sessionmaker

Base = declarative_base()


class HubInfo(Base):
    """
    Hub information.

    Only one record exists.
    """
    __tablename__ = 'hub_info'
    identification = Column(String(50), primary_key=True)
    hub_id = Column(Integer)
    profile_id = Column(Integer)
    last_sync_time = Column(DateTime)


class Device(Base):
    """
    Device table - Contains information regarding a single device

    All the devices associated with this hub/user will be stored here.
    Expected number of rows  < 50
    """
    __tablename__ = 'device'
    id = Column(Integer, primary_key=True)
    identification = Column(String(50))
    sub_identification = Column(Integer)
    type = Column(String(30))
    default_value = Column(String)
    ip = Column(String) # IP address of the node.


class DeviceData(Base):
    """
    Sensor data buffered in the hub.

    When device sends data it may not be transferred immediately to the server, it is stored here.
    In some predefined interval it would be sync to the server. Once synced this data is removed from here.
    Expected number of rows < 10000.
    """
    __tablename__ = 'device_data'
    id = Column(Integer, primary_key=True)
    device_id = Column(Integer, ForeignKey('device.id'))
    sensor_value = Column(String)
    activity_date = Column(DateTime)
    received_date = Column(DateTime)
    last_sync_time = Column(DateTime)


class Rule(Base):
    """
    Rule table
    """
    __tablename__ = 'rule'
    id = Column(Integer, primary_key=True)


def drop_tables(engine):
    """
    Drops all the tables in the database.
    """
    Base.metadata.drop_all(engine)


def init_tables(engine):
    """
    Creates all table structures in the database.
    """
    Base.metadata.create_all(engine)


def create_db_session(engine):
    """
    Creates a database session
    Loads table from the database into memory.
    """
    Base.metadata.bind = engine
    DBSession = sessionmaker(bind=engine)
    return DBSession()
