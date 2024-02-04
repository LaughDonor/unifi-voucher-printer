from functools import wraps, partial
from http import HTTPStatus
from json import loads
from pprint import pprint

old_print = print
from curlify import to_curl
from requests import HTTPError, Response


def API(func=None, *, json=True, print=False):
    if func is None:
        return partial(API, json=json, print=print)

    @wraps(func)
    def wrapper(*args, **kwargs):
        result: Response = func(*args, **kwargs)
        if json:
            full_json = loads(result.text)
            if print:
                pprint((result.request.url))
                pprint((result.request.hooks))
                pprint((result.request.body))
                pprint(dict(result.request.headers))
                pprint(dict(result.headers))
                pprint(dict(result.cookies))
                old_print(to_curl(result.request))
                pprint(result.headers.pop("X-CSRF-Token", "NONE!"))

            if (meta := full_json.get("meta", {})).get("rc", "") == "error":
                raise HTTPError(meta.get("msg"))
            response = full_json.get("data", full_json)
        elif result.status_code != HTTPStatus.OK:
            raise HTTPError(result.text)
        else:
            response = result.text

        if print:
            pprint(response)
        return response

    return wrapper
