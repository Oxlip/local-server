"""
pubnub client to receive notifications from the remote server.
The notifications may be also a command(turn on light), rule update...
"""

import PubNub


def process_notifications(channel_id):
    """
    Process push notifications in a loop
    """
    pubnub = PubNub.Pubnub(publish_key='pub-c-9ff29ff2-1427-4864-bbfa-7d3270a233dc',
                           subscribe_key='sub-c-7e20413a-8d2d-11e3-ae86-02ee2ddab7fe',
                           ssl_on=False)
    pubnub.subscribe({
        'channel': channel_id,
        'callback': notification_received
    })


def notification_received(message):
    """
    When a notification arrives this function is called to process the message.
    """
    return True
