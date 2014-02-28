"""
Provides classes and functions to access data from the local database.
Note - The ORM is done in database_declarative.py
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_declarative import Device, Rule, create_db_session, create_tables

from datetime import datetime


class Database:
    """
    PlugZ Hub Database class - Contains all the functions to persist device, rule and sensor data information.
    """

    def __init__(self, sync_interval=60):
        self.engine = create_engine('sqlite:///database.db', echo=True)
        self.devices = []
        self.rules = []
        self.last_sync_time = datetime.now()
        self.sync_interval = sync_interval
        self.session = create_db_session(self.engine)
        #Todo initialize the hub id from database
        self.hub_id = None

    def get_devices(self):
        """
        Returns all the devices that can be managed by a hub.
        This function will take care of syncing with server if needed.
        """
        self._sync()
        return self.devices

    def get_rules(self):
        """
        Returns all the rules that are associated with devices that can be managed by a hub.
        This function will take care of syncing with server if needed.
        """
        self._sync()
        return self.rules

    def _sync(self):
        """
        Sync the database with server if required
        """
        if self.last_sync_time + datetime.timedelta(0, self.sync_interval) < datetime.now():
            return

        # TODO - sync the database by using REST calls to the server


        # fill the object list from database
        self.devices = self.session.query(Device).all()
        self.rules = self.session.query(Rule).all()
