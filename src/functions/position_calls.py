from src.endpoints import orders_url, position_status_url
from .connect import private_requests


def get_order_details(ticker, orderid):
    """Fetches details of an order and returns the response"""
    response = private_requests(orders_url, "GET", symbol=ticker,
                                productType="USDT-FUTURES", orderid=orderid)
    print(response)
    if response and response.get("msg") == "success":
        return response

    print("get_open_orders/ ", response)
    return {}


def get_position_details(ticker, quote):
    """Fetches details of a position and returns the response"""
    response = private_requests(position_status_url, "GET", symbol=ticker,
                                productType="USDT-FUTURES", marginCoin=quote)
    if response and response.get("msg") == "success":
        return response

    print("get_open_positions/ ", response)
    return {}


def query_orders(ticker, orderid):
    """Query open orders and returns the price and quantity"""
    response = get_order_details(ticker, orderid)
    price, quantity = 0, 0

    if response.get("data"):
        price = response.get("data")["price"]
        quantity = response.get("data")["size"]

    return price, quantity


def query_positions(ticker, quote):
    """Query open positions and returns the price and quantity"""
    response = get_position_details(ticker, quote)
    price, quantity = 0, 0

    if response.get("data"):
        price = response.get("data")["openPriceAvg"]
        quantity = response.get("data")["openDelegateSize"]

    return price, quantity
