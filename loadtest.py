import json
import os
import uuid

from ailoads.fmwk import scenario, requests

# Read configuration from env
SERVER_URL = os.getenv('SYNCTO_SERVER_URL',
                       "https://syncto.stage.mozaws.net:443").rstrip('/')

FXA_BROWSERID_ASSERTION = os.getenv("FXA_BROWSERID_ASSERTION")
FXA_CLIENT_STATE = os.getenv("FXA_CLIENT_STATE")

if not FXA_BROWSERID_ASSERTION and not FXA_CLIENT_STATE:
    raise ValueError("Please define FXA_BROWSERID_ASSERTION "
                     "and FXA_CLIENT_STATE env variables.")


_CONNECTIONS = {}


def get_connection(conn_id=None):
    if conn_id is None or conn_id not in _CONNECTIONS:
        conn = SynctoConnection(uuid.uuid4().hex)
        _CONNECTIONS[conn_id] = conn

    return _CONNECTIONS[conn_id]


class SynctoConnection(object):

    def __init__(self, id):
        self.id = id
        self.headers = {
            "Authorization": "BrowserID %s" % FXA_BROWSERID_ASSERTION,
            "X-Client-State": FXA_CLIENT_STATE
        }
        self.timeout = 300000

    def get(self, endpoint):
        return requests.get(
            SERVER_URL + endpoint,
            headers=self.headers,
            timeout=self.timeout)

    def put(self, endpoint, data):
        return requests.put(
            SERVER_URL + endpoint,
            json=data,
            headers=self.headers,
            timeout=self.timeout)

    def delete(self, endpoint):
        return requests.delete(
            SERVER_URL + endpoint,
            headers=self.headers,
            timeout=self.timeout)


@scenario(20)
def readonly_crypto():
    """Syncing history from an existing account"""
    conn = get_connection('user1')

    # 1. Connecting to get back the crypto key
    r = conn.get('/v1/buckets/syncto/collections/crypto/records')
    r.raise_for_status()
    body = r.json()
    assert "data" in body


@scenario(20)
def readonly_meta():
    """Syncing history from an existing account"""
    conn = get_connection('user1')

    # 2. Connecting to get back the meta informations
    r = conn.get('/v1/buckets/syncto/collections/meta/records')
    r.raise_for_status()
    body = r.json()
    assert "data" in body


@scenario(20)
def readonly_bookmarks():
    """Syncing history from an existing account"""
    conn = get_connection('user1')

    # 3. Connecting to get the bookmarks (for TV)
    r = conn.get('/v1/buckets/syncto/collections/bookmarks/records')
    r.raise_for_status()
    body = r.json()
    assert "data" in body


@scenario(20)
def readonly_history():
    """Syncing history from an existing account"""
    conn = get_connection('user1')

    # 4. Connecting to get the history
    r = conn.get('/v1/buckets/syncto/collections/history/records')
    r.raise_for_status()
    body = r.json()
    assert "data" in body


@scenario(20)
def readonly_passwords():
    """Syncing history from an existing account"""
    conn = get_connection('user1')

    # 5. Connecting to get the passwords
    r = conn.get('/v1/buckets/syncto/collections/passwords/records')
    r.raise_for_status()
    body = r.json()
    assert "data" in body


@scenario(30)
def write_history():
    """Adding some history data."""
    conn = get_connection('user1')

    PAYLOAD = {
        "ciphertext": ("75IcW3P4WxUJipehWryevc+ygK5vojh3nOadu7YSX9"
                       "zJSm3eBHu5lNIg1UtDyt3b"),
        "IV": "Sj3U2Nkk2IjE2S59hv0m7Q==",
        "hmac": ("c6a530f3486142d1069f80bfaff907e0cc077a892cf7f9bd"
                 "62f943b68b610351")
    }

    payload = {"data": {"payload": json.dumps(PAYLOAD), "sortindex": 2000}}
    # Adding some history.
    r = conn.put('/v1/buckets/syncto/collections/history/records/d2X1O6-DyeFS',
                 payload)
    r.raise_for_status()

    body = r.json()
    assert "data" in body

    # Removing some history
    r = conn.delete('/v1/buckets/syncto/collections/history'
                    '/records/d2X1O6-DyeFS')
    r.raise_for_status()
