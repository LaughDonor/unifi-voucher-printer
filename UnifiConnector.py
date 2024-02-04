from math import floor
from pprint import pprint
from ssl import get_server_certificate

from datetime import datetime
from requests import Session
from unificontrol.pinned_requests import PinningHTTPSAdapter

from config import UNIFI_HOST, UNIFI_PORT, UNIFI_USER, UNIFI_PASS, UNIFI_URL, UNIFI_SITE
from utils import API


class UnifiConnector:
    _session = Session()

    def __init__(self):
        cert = get_server_certificate((UNIFI_HOST, UNIFI_PORT))
        self._session.headers.update(
            {"Accept": "application/json", "Content-Type": "application/json"}
        )
        self._session.mount(UNIFI_URL, PinningHTTPSAdapter(cert))
        self._session.verify = True
        self.login()
        pprint(self._session.headers)

    @API
    def login(self):
        return self._session.post(
            f"{UNIFI_URL}/api/auth/login",
            json={
                "username": UNIFI_USER,
                "password": UNIFI_PASS,
                "token": "",
                "rememberMe": False,
            },
            timeout=1,
            hooks={"response": self._set_csrf_token},
        )

    def _set_csrf_token(self, response, *args, **kwargs):
        self._session.headers.update(
            {"X-Csrf-Token": response.headers.get("X-Csrf-Token")}
        )

    @API
    def list_vouchers(self, since: datetime = None, timestamp=None):
        time = {"create_time": timestamp or since.timestamp()} if since else {}
        return self._session.get(
            f"{UNIFI_URL}/proxy/network/api/s/{UNIFI_SITE}/stat/voucher",
            json=time,
            timeout=1,
        )

    @API
    def create_voucher(self, note, checkout: datetime):
        minutes = (checkout - datetime.now()).total_seconds() / 60
        data = {
            "cmd": "create-voucher",
            "down": 5000,
            "expire_number": str(floor(minutes)),
            "expire_unit": 1,
            "n": 1,
            "note": note,
            "quota": 1,
            "up": 5000,
        }
        print(self._session.cookies)
        return self._session.post(
            f"{UNIFI_URL}/proxy/network/api/s/{UNIFI_SITE}/cmd/hotspot",
            json=data,
            timeout=1,
        )
