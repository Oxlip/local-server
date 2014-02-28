"""
The main program which binds everything else.
"""
import argparse
from database import Database
from rest_client import RestClient
from notifications import start_notification_thread

verbose_level = 0


def process_command_line():
    """
    Process command line arguments and assign to appropriate variable
    """
    global verbose_level
    parser = argparse.ArgumentParser(description='PlugZ Hub.')
    parser.add_argument('--verbose', default=0, help='Increases the logging amount.')
    args = parser.parse_args()
    verbose_level = args.verbose


def main():
    process_command_line()

    db = Database()
    rc = RestClient(db.hub_id)
    channel_id = rc.connect()
    notification_thread = start_notification_thread(channel_id)
    notification_thread.join()


main()
