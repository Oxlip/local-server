"""
Provides classes and functions to access data from the local database.
Note - The ORM is done in database_declarative.py
"""

from datetime import datetime
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_declarative import HubInfo, Device, Rule, create_db_session, init_tables, drop_tables


DATABASE_FILE_NAME = 'sqlite:///database.db'


def reset_tables(identification, hub_id):
    """
    Initialize the tables to factory reset condition.
    """
    engine = create_engine(DATABASE_FILE_NAME, echo=False)
    # Drop table and create them again
    drop_tables(engine)
    init_tables(engine)
    session = create_db_session(engine)
    # Add one row to identify the hub.
    hub_info = HubInfo(identification=identification, id=hub_id)
    session.add(hub_info)
    session.commit()


def _is_device_in_list(device_list, device_id):
    """
    Finds whether the given device_id exists in the given list.
    """
    for dev in device_list:
        if (isinstance(dev, Device) and dev.id == device_id) or \
           (isinstance(dev, dict) and dev['id'] == device_id):
            return True
    return False


def _device_list_diff(local_devices, cloud_devices):
    """
    Do diff of a local_devices and cloud_devices.
    Returns number of devices added and number of devices deleted.

    TODO - The algorithm used is worst, as simple sorting and then finding
           would make a huge difference...
    """
    devices_added = []
    devices_removed = local_devices
    for c_dev in cloud_devices:
        device_id = c_dev['id']
        already_exists = _is_device_in_list(local_devices, device_id)
        if not already_exists:
            devices_added.append(c_dev)

    for i in xrange(len(devices_removed) - 1, -1, -1):
        l_dev = devices_removed[i]
        device_id = l_dev.id
        still_exists = _is_device_in_list(cloud_devices, device_id)
        if still_exists:
            del devices_removed[i]

    return devices_added, devices_removed


class Database:
    """
    uHub Database class - Contains all the functions to persist device, rule and sensor data information.
    """

    def __init__(self, rest_client, sync_interval=60):
        self.engine = create_engine(DATABASE_FILE_NAME, echo=False)
        self.last_sync_time = datetime.now()
        self.sync_interval = sync_interval
        self.session = create_db_session(self.engine)
        self.rest_client = rest_client
        init_tables(self.engine)
        self._sync(force=True)

    def get_device(self, device_id):
        """
        Returns a device with given device_id
        """
        return self.session.query(Device).filter_by(id=device_id).one()

    def is_device_exists(self, identification):
        """
        Returns True if a device with given identification exists
        """
        return self.session.query(Device).filter_by(identification=identification).count() > 0

    def set_device_ip(self, identification, ip):
        """
        Sets IP address of a device.
        """
        self.session.query(Device).filter_by(identification=identification).update({"ip": ip})

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

        try:
            clould_dlist = self.rest_client.get_devices()
        except Exception, e:
            devices_added, devices_removed = [], []
            logging.error('Failed to sync to cloud server - {0}'.format(e))
        else:
            local_dlist = self.session.query(Device).all()
            devices_added, devices_removed = _device_list_diff(local_dlist, clould_dlist)

        logging.info('{0} devices added and {1} devices removed'.format(len(devices_added), len(devices_removed)))
        try:
            for a_dev in devices_added:
                logging.info('++ {0} {1}'.format(a_dev['id'], a_dev['identification']))

                dev = Device(id=a_dev['id'], identification=a_dev['identification'],
                             sub_identification=a_dev['sub_identification'],
                             type=a_dev['type'], default_value=a_dev['default_value'])
                self.session.add(dev)

            for r_dev in devices_removed:
                logging.info('-- {0} {1}'.format(r_dev.id, r_dev.identification))
                self.session.delete(r_dev)

            self.session.commit()
        except Exception, e:
            logging.error('Failed to update the local DB - {0}'.format(e))
            self.session.rollback()
        else:
            logging.info('Device information synched with server:')

        #TODO - sync rules also.
