import sys

sys.path.append('../')

from rest_client import RestClient, RestReq

tests_api_infos = {
   'hub_id' : '123234',
   'user'   : {
       'name' : 'cderbois',
       'first_name' : 'corentin',
       'last_name'  : 'derbois',
       'email'      : 'cderbois@gmail.com'
    }
}

def test_url_forge():
    url = RestReq('a', 'b', 'd').url_format('c')
    assert url == 'a/b/c/d'
    url = RestReq('a', 'b', 'd').url_format('')
    assert url == 'a/b/d'
    url = RestReq('a', 'b', '').url_format('')
    assert url == 'a/b'


def test_get_user_info():
    client = RestClient()
    success, result = client.get_user_info(tests_api_infos['user']['name'])
    assert success
    for key in ['first_name', 'last_name', 'email']:
        assert result[key] == tests_api_infos['user'][key]


def test_get_hub_info():
    client = RestClient()
    res = client.hub_connect(tests_api_infos['hub_id'], 'should failed with real auth')
    assert res is not None
    assert res['id'] == 1


def test_register_device():
    client = RestClient()
    device_name = 'uSwitch_unittest'
    success, result = client.register_device(tests_api_infos['user']['name'],
                                             '#test_serial',
                                             'uSwitch',
                                             device_name,
                                             tests_api_infos['hub_id'])
    assert success

    devices = client.get_devices(tests_api_infos['hub_id'])
    assert len(devices) > 1

    found = False
    for device in devices:
        if device['name'] == device_name:
            found = True
            assert device['type'] == 'uSwitch'
            assert device['identification'] == '#test_serial'
            device_id = device['id']
    assert found

    res = client.send_device_value(device_id, 10, '#test_serial', 0)
    assert res

