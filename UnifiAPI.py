from requests import HTTPError, Request, Session
from requests.models import PreparedRequest
from math import floor
from config import (
    UNIFI_API_KEY,
    UNIFI_URL,
    UNIFI_SITE,
)
from datetime import datetime
import urllib3

# Disable SSL warnings for self-signed certificates
urllib3.disable_warnings()

SITE_URL = f"{UNIFI_URL}/proxy/network/integration/v1/sites"


class UnifiAPI:
    _request: PreparedRequest

    def __init__(self):
        headers = {"Accept": "application/json", "X-API-KEY": UNIFI_API_KEY}
        self._request = Request(
            url=SITE_URL,
            headers=headers,
        ).prepare()
        sites = self._send(key="data") or []
        site = next(
            filter(lambda x: x.get("internalReference") == UNIFI_SITE, sites), None
        )
        if not site:
            raise ValueError(f"Site '{UNIFI_SITE}' not found in Unifi API response.")

        self._request = Request(
            url=f"{SITE_URL}/{site.get('id')}/hotspot/vouchers",
            headers=headers,
        ).prepare()

    def _send(self, method="GET", data=None, key=None):
        req = self._request.copy()
        req.prepare_method(method)
        if data:
            req.prepare_body(None, None, json=data)
        response = Session().send(req, timeout=10, verify=False).json()
        if key:
            prop = response.get(key, None)
            if prop is None:
                raise HTTPError(response=response)
            return prop
        return response

    def list_vouchers(self, since: datetime = None, timestamp=None):
        data = {"create_time": timestamp or since.timestamp()} if since else {}
        return self._send(data=data, key="data")

    def create_voucher(self, name, checkout: datetime):
        minutes = (checkout - datetime.now()).total_seconds() / 60
        data = {
            "name": name,
            "timeLimitMinutes": floor(minutes),
            "rxRateLimitKbps": 5000,
        }
        return self._send("POST", data, key="vouchers")[0]
