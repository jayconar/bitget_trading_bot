from src.config import api_key, api_secret, passphrase
from src.endpoints import api_url, servertime_url
from functools import wraps
import requests
import base64
import hmac
import json
import time


def get_timestamp():
    """Returns current timestamp of the server in milliseconds"""
    timestamp = public_requests(servertime_url).get("data")
    return timestamp.get("serverTime")


def pre_hash(timestamp, method, request_path, body):
    """Creates a pre-hash string from the given timestamp, method, request path, and body"""
    return str(timestamp) + str.upper(method) + request_path + body


def signature(message, secret_key):
    """Generates a base64-encoded HMAC-SHA256 signature for the given message and secret key"""
    mac = hmac.new(bytes(secret_key, encoding='utf8'),
                   bytes(message, encoding='utf-8'), digestmod='sha256')
    d = mac.digest()
    return base64.b64encode(d).decode()


def auth(url, method, **kwargs):
    """Authenticates and return signature for private API requests"""
    timestamp = get_timestamp()
    request_path = url

    # POST
    if method == "POST":
        body = json.dumps(kwargs)
        sign = signature(pre_hash(timestamp, method, request_path, str(body)), api_secret)
        return sign, timestamp

    # GET
    body = ""
    request_path = url_constructor(request_path, **kwargs)  # Need to be sorted in ascending alphabetical order by key
    sign = signature(pre_hash(timestamp, method, request_path, str(body)), api_secret)
    return sign, timestamp


def rate_limited(delay):
    """Decorator that enforces a delay between function calls"""

    def decorator(func):
        last_called = [0]  # Storing the last time the function was called

        @wraps(func)
        def wrapper(*args, **kwargs):
            elapsed = time.time() - last_called[0]
            if elapsed < delay:
                time.sleep(delay - elapsed)  # Wait for the remaining time
            result = func(*args, **kwargs)
            last_called[0] = time.time()  # Updating the last called time
            return result

        return wrapper

    return decorator


@rate_limited(3)  # To avoid exceeding API rate limits
def public_requests(url, meth="GET", headers=None, body_params="", path_params=None, **kwargs):
    """Makes requests to public market data endpoints and returns the response"""
    headers = headers if headers else {}

    if path_params or kwargs:
        url = url_constructor(url, path_params, **kwargs)

    try:
        if meth == "POST":
            response = requests.post(api_url + url, headers=headers, data=body_params)
        else:  # We're only going to use get and post methods
            response = requests.get(api_url + url, headers=headers, data=body_params)

        response.raise_for_status()  # Raise an HTTPError for bad responses (4xx and 5xx)
        return response.json()

    except requests.exceptions.HTTPError as e:
        print(f"HTTP error: {e}")
        return None
    except requests.exceptions.Timeout as e:
        print(f"Request timed out: {e}")
        return None
    except requests.exceptions.TooManyRedirects as e:
        print(f"Too many redirects: {e}")
        return None
    except requests.exceptions.RequestException as e:
        print(f"Request error: {e}")
        return None
    except json.decoder.JSONDecodeError as e:
        print(f"JSON decode error: {e}")
        return None
    except Exception as e:
        print(e)


def url_constructor(base_url, path_params=None, **kwargs):
    """Passes parameters into url"""
    # Adding path parameters if any
    if path_params and base_url.count(":"):
        split_url = base_url.split("/")

        for i, part in enumerate(split_url):
            # Endpoints with ':' indicates body parameter that needs to be filled
            if ":" in part:
                key = part.replace(":", "")

                if key in path_params:
                    split_url[i] = path_params[key]
        # Concatenating the url
        base_url = "/".join(split_url)

    # Return if no query parameters
    if not kwargs:
        return base_url
    # Adding query parameters
    query_params = []
    for key, value in kwargs.items():
        query_params.append(f"{key}={value}")
    query_string = "&".join(query_params)

    # Combining base url and query string
    url = f"{base_url}?{query_string}"
    return url


def private_requests(url, method="GET", **kwargs):
    """Receives URL and sends any type of private requests to return private responses"""
    sign, timestamp = auth(url, method, **kwargs)

    headers = {
        "ACCESS-KEY": api_key,
        "ACCESS-SIGN": sign,
        "ACCESS-PASSPHRASE": passphrase,
        "ACCESS-TIMESTAMP": timestamp,
        "locale": "en-US",
        "Content-Type": "application/json"
    }

    # Private request is public request with an authenticated header
    response = public_requests(url, method, headers=headers, **kwargs)

    return response
