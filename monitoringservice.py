import threading
import PubNub
import random
import time

__author__ = 'NPrabhaker'


def get_client_notification(channel_id):
    daily_chart_thread = threading.Thread(target=_notify_daily_chart, args=(channel_id + '-daily',))
    daily_chart_thread.daemon = True
    daily_chart_thread.start()

    morris_chart_thread = threading.Thread(target=_notify_Morris_chart, args=(channel_id + '-morris',))
    morris_chart_thread.daemon = True
    morris_chart_thread.start()
    return


def _notify_daily_chart(channel_id):
    # TODO: Connect to DB and publish data
    pubnub = PubNub.Pubnub(publish_key='pub-c-9ff29ff2-1427-4864-bbfa-7d3270a233dc',
                           subscribe_key='sub-c-7e20413a-8d2d-11e3-ae86-02ee2ddab7fe',
                           ssl_on=False)
    datalist = [random.randrange(0, 60), random.randrange(0, 60), random.randrange(0, 60), random.randrange(0, 60),
                random.randrange(0, 60), random.randrange(0, 60), random.randrange(0, 60), random.randrange(0, 60),
                random.randrange(0, 60), random.randrange(0, 60), random.randrange(0, 60), random.randrange(0, 60)]
    #new_data_list = list(datalist)
    neg = -1

    while True:
        del datalist[0]

        datalist.append(random.randrange(15, 55))

        pubnub.publish({
            'channel': channel_id,
            'message': {
                'data': [[0, datalist[0]],
                         [1, datalist[1]],
                         [2, datalist[2]],
                         [3, datalist[3]],
                         [4, datalist[4]],
                         [5, datalist[5]],
                         [6, datalist[6]],
                         [7, datalist[7]],
                         [8, datalist[8]],
                         [9, datalist[9]],
                         [10, datalist[10]]
                ]
            }
        })

        time.sleep(2)


def _notify_Morris_chart(channel_id):
    # TODO: Connect to DB and publish data
    pubnub = PubNub.Pubnub(publish_key='pub-c-9ff29ff2-1427-4864-bbfa-7d3270a233dc',
                           subscribe_key='sub-c-7e20413a-8d2d-11e3-ae86-02ee2ddab7fe',
                           ssl_on=False)
    datalist = [random.randrange(0, 60), random.randrange(0, 60), random.randrange(0, 60), random.randrange(0, 60),
                random.randrange(0, 60), random.randrange(0, 60), random.randrange(0, 60), random.randrange(0, 60),
                random.randrange(0, 60), random.randrange(0, 60), random.randrange(0, 60), random.randrange(0, 60)]
    #new_data_list = list(datalist)
    neg = -1

    while True:
        del datalist[0]

        datalist.append(random.randrange(15, 55))

        pubnub.publish({
            'channel': channel_id,
            'message': {
                'data': [
                    {"period": '2010 Q1', "iphone": random.randrange(1000, 2000), "ipad": random.randrange(3000, 5000), "itouch": random.randrange(100, 6000)},
                    {"period": '2010 Q2', "iphone": random.randrange(1000, 2000), "ipad": random.randrange(3000, 5000), "itouch": random.randrange(100, 6000)},
                    {"period": '2010 Q3', "iphone": random.randrange(1000, 2000), "ipad": random.randrange(3000, 5000), "itouch": random.randrange(100, 6000)},
                    {"period": '2010 Q4', "iphone": random.randrange(1000, 2000), "ipad": random.randrange(3000, 5000), "itouch": random.randrange(100, 6000)},
                    {"period": '2011 Q1', "iphone": random.randrange(1000, 2000), "ipad": random.randrange(3000, 5000), "itouch": random.randrange(100, 6000)},
                    {"period": '2011 Q2', "iphone": random.randrange(1000, 2000), "ipad": random.randrange(3000, 5000), "itouch": random.randrange(100, 6000)},
                    {"period": '2011 Q3', "iphone": random.randrange(1000, 2000), "ipad": random.randrange(3000, 5000), "itouch": random.randrange(100, 6000)},
                    {"period": '2011 Q4', "iphone": random.randrange(1000, 2000), "ipad": random.randrange(3000, 5000), "itouch": random.randrange(100, 6000)},
                    {"period": '2012 Q1', "iphone": random.randrange(1000, 2000), "ipad": random.randrange(3000, 5000), "itouch": random.randrange(100, 6000)},
                    {"period": '2012 Q2', "iphone": random.randrange(1000, 2000), "ipad": random.randrange(3000, 5000), "itouch": random.randrange(100, 6000)}


                ]
            }
        })

        time.sleep(2)



