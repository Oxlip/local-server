import sys

sys.path.append('../')

from rest_client import RestClient, RestReq

def test_url_forge():
    url = RestReq('a', 'b', 'd').url_format('c')
    assert url == 'a/b/c/d'
    url = RestReq('a', 'b', 'd').url_format('')
    assert url == 'a/b/d'
    url = RestReq('a', 'b', '').url_format('')
    assert url == 'a/b'


def test_get_user_info():
    client = RestClient()
    success, result = client.get_user_info('cderbois')
    assert success
    assert result['first_name'] == 'corentin'
    assert result['last_name']  == 'derbois'
    assert result['email']      == 'cderbois@gmail.com'

