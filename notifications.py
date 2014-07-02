"""
pubnub client to receive notifications from the remote server.
The notifications may be also a command(turn on light), rule update...
"""

import PubNub
from device_handler import handle_server_command


def notification_loop(channel_id):
    """
    Process push notifications in a loop
    """
    # TODO - Replace the publish key and subscribe key
    pubnub = PubNub.Pubnub(publish_key='pub-c-9ff29ff2-1427-4864-bbfa-7d3270a233dc',
                           subscribe_key='sub-c-7e20413a-8d2d-11e3-ae86-02ee2ddab7fe',
                           ssl_on=False)
    pubnub.subscribe({
        'channel': channel_id,
        'callback': handle_server_command
    })
