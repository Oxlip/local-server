"""
pubnub client to receive notifications from the remote server.
The notifications may be also a command(turn on light), rule update...
"""

import PubNub
import threading


def start_notification_thread(channel_id):
    """
    Start notification processing in a separate thread.
    """
    notification_thread = threading.Thread(target=_start_notifications, args=(channel_id,))
    notification_thread.daemon = True
    notification_thread.start()

    return notification_thread


def _start_notifications(channel_id):
    """
    Process push notifications in a loop
    """
    # TODO - Replace the publish key and subscribe key
    pubnub = PubNub.Pubnub(publish_key='pub-c-9ff29ff2-1427-4864-bbfa-7d3270a233dc',
                           subscribe_key='sub-c-7e20413a-8d2d-11e3-ae86-02ee2ddab7fe',
                           ssl_on=False)
    pubnub.subscribe({
        'channel': channel_id,
        'callback': _notification_received
    })


def _notification_received(message):
    """
    When a notification arrives this function is called to process the message.
    """
    print 'Notification from pubnub = ' + str(message)
    return True
