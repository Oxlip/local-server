"""
Provides classes and functions to access data from the local database.
Note - The ORM is done in database_declarative.py
"""

from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_declarative import HubInfo, Device, Rule, create_db_session, init_tables, drop_tables


DATABASE_FILE_NAME = 'sqlite:///database.db'


def reset_tables(identification, hub_id):
    """
    Initialize the tables to factory reset condition.
    """
    engine = create_engine(DATABASE_FILE_NAME, echo=True)
    # Drop table and create them again
    drop_tables(engine)
    init_tables(engine)
    session = create_db_session(engine)
    # Add one row to identify the hub.
    hub_info = HubInfo(identification=identification, id=hub_id)
    session.add(hub_info)
    session.commit()


class Database:
    """
    PlugZ Hub Database class - Contains all the functions to persist device, rule and sensor data information.
    """

    def __init__(self, rest_client, sync_interval=60):
        self.engine = create_engine(DATABASE_FILE_NAME, echo=True)
        self.devices = []
        self.rules = []
        self.last_sync_time = datetime.now()
        self.sync_interval = sync_interval
        self.session = create_db_session(self.engine)
        self.rest_client = rest_client
        init_tables(self.engine)
        self._sync(force=True)

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

    def _sync(self, force=False):
        """
        Sync the database with server if required
        """
        sync_required = force or self.last_sync_time + datetime.timedelta(0, self.sync_interval) > datetime.now()
        if not sync_required:
            return

        # TODO - sync the database by using REST calls to the server
        r_devices = self.rest_client.get_devices()
        for r_device in r_devices:
            print r_device

        # fill the object list from database
        self.devices = self.session.query(Device).all()
        self.rules = self.session.query(Rule).all()
