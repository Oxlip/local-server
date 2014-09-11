import os
import sys
import uobj
import uswitch
import logging

sys.path.append('../')

from rest_client import RestClient
from optparse import OptionParser

##############################################################################
#          Cli simulation part
##############################################################################

def cli_params():
    cmd_line = OptionParser()
    
    cmd_line.add_option('-l', '--load-session', dest='load_session',
                        help='Load session previusly save',
                        action='store_true', default=False)

    cmd_line.add_option('-i', '--hub-id', dest='hub_id',
                        help='Serial to the hub to play with',
                        type='string', default=None)

    cmd_line.add_option('-p', '--list', dest='list',
                        help='List ssession',
                        action='store_true', default=False)

    options, args = cmd_line.parse_args()

    if options.hub_id is None and not options.load_session:
        logging.error('If you don\'t load a session, provide a hub_id')
        sys.exit(1)

    return options, args

def load_session_from_hub_id(options):
    client = RestClient('123234', 'should failed with real auth')
    devices = client.get_devices()
    print devices

def load_session_from_file():
    _file_path = '/tmp/usim.session'
    if not os.path.exists(_file_path):
        logging.error('There are no current session')
        return []
    with open(_file_path, 'r') as f:
        try:
            session = json.load(f)
        except:
            logging.error('File session comrupted')
            return []
    return session

def save_session_to_file(session):
    _file_path = '/tmp/usim.session'
    str_session = json.dumps(session)
    try:
        with open(_file_path, 'wa+') as f:
            f.write(str_session)
    except:
        logging.error('Failed to save the session')

def load_session(options):
    print options
    if options.load_session:
        session = load_session_from_file()
    else:
        session = load_session_from_hub_id(options)

def cli_simul(options, args):
    pass

if __name__ == '__main__':
    options, args = cli_params()
    load_session(options)
    cli_simul(options, args)
