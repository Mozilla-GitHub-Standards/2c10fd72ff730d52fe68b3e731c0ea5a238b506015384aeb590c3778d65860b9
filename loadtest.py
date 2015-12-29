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
        self.authenticated = False
        self.timeout = 2

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
