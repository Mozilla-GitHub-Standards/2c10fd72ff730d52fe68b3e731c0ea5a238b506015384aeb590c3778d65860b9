import base64
import hmac
import os
import random
import uuid

from fxa import errors
from fxa.core import Client
from fxa.plugins.requests import FxABrowserIDAuth

from ailoads.fmwk import scenario, requests

# Read configuration from env
SERVER_URL = os.getenv('SYNCTO_SERVER_URL',
                       "https://syncto.stage.mozaws.net:443")
FXA_URL = os.getenv("SYNCTO_FXA_URL",
                    "https://api-accounts.stage.mozaws.net/v1")
FXA_USER_SALT = os.getenv("SYNCTO_FXA_USER_SALT")

# if env variable present convert it to bytes
if FXA_USER_SALT:
    FXA_USER_SALT = FXA_USER_SALT.encode('utf-8')
# else build a temporary one
else:
    FXA_USER_SALT = base64.urlsafe_b64encode(os.urandom(36))

# Constants
FXA_ERROR_ACCOUNT_EXISTS = 101

ACCOUNT_CREATED = False


def picked(percent):
    """Should we stay or should we go?"""
    return random.randint(0, 100) < percent


class FXAUser(object):
    def __init__(self):
        self.server = FXA_URL
        self.password = hmac.new(FXA_USER_SALT, b"syncto").hexdigest()
        self.email = "syncto-%s@restmail.net" % self.password
        print("Using FxA: ", self.email, ' : ', self.password)
        self.auth = self.get_auth()

    def get_auth(self):
        global ACCOUNT_CREATED

        if ACCOUNT_CREATED:
            return ACCOUNT_CREATED

        # ONLY WORKS WITH FxA STAGE

        if 'stage' in SERVER_URL:
            if 'stage' not in self.server:
                raise Exception("Please use the FxA stage server.")

            client = Client(self.server)

            try:
                client.create_account(self.email,
                                      password=self.password,
                                      preVerified=True)
            except errors.ClientError as e:
                if e.errno != FXA_ERROR_ACCOUNT_EXISTS:
                    raise
        else:
            print("You are not using stage, make sure your FxA test "
                  "account exists: https://123done-prod.dev.lcip.org/")

        audience = "https://token.stage.mozaws.net/"

        ACCOUNT_CREATED = FxABrowserIDAuth(
            self.email,
            password=self.password,
            audience=audience,
            server_url=self.server,
            with_client_state=True)

        return ACCOUNT_CREATED


_CONNECTIONS = {}


def get_connection(conn_id=None):
    if conn_id is None or conn_id not in _CONNECTIONS:
        conn = SynctoConnection(uuid.uuid4().hex)
        _CONNECTIONS[conn_id] = conn

    return _CONNECTIONS[conn_id]


class SynctoConnection(object):

    def __init__(self, id):
        self.id = id
        self.user = FXAUser()
        self.authenticated = False

    def get(self, endpoint):
        return requests.get(
            SERVER_URL + endpoint,
            auth=self.user.auth)

    def put(self, endpoint, data):
        return requests.put(
            SERVER_URL + endpoint,
            json=data,
            auth=self.user.auth)

    def delete(self, endpoint):
        return requests.delete(
            SERVER_URL + endpoint,
            auth=self.user.auth)


@scenario(100)
def readonly_sync():
    """Syncing history from an existing account"""
    conn = get_connection('user1')

    # 1. Connecting to get back the crypto key
    r = conn.get('/v1/buckets/syncto/collections/crypto/records')
    r.raise_for_status()
    body = r.json()
    assert "data" in body

    # 2. Connecting to get back the meta informations
    r = conn.get('/v1/buckets/syncto/collections/meta/records')
    r.raise_for_status()
    body = r.json()
    assert "data" in body

    # 3. Connecting to get the bookmarks (for TV)
    r = conn.get('/v1/buckets/syncto/collections/bookmarks/records')
    r.raise_for_status()
    body = r.json()
    assert "data" in body

    # 4. Connecting to get the history
    r = conn.get('/v1/buckets/syncto/collections/history/records')
    r.raise_for_status()
    body = r.json()
    assert "data" in body

    # 5. Connecting to get the passwords
    r = conn.get('/v1/buckets/syncto/collections/passwords/records')
    r.raise_for_status()
    body = r.json()
    assert "data" in body


if __name__ == '__main__':
    readonly_sync()
