from src.endpoints import positions_url, open_orders_url
from .connect import private_requests
from .data_handler import read_json


def check_orders():
    """Checks for active orders and returns order status"""
    response = private_requests(open_orders_url, productType="USDT-FUTURES")

    if response.get("data").get("entrustedList"):
        return True
    return False


def check_positions():
    """Checks positions and returns true or false along with the quantity and cost"""
    quote = read_json("quote_currency")["quote_currency"]

    response = private_requests(positions_url,
                                productType="USDT-FUTURES", marginCoin=quote)
    if response.get("data"):
        return True
    return False


def check_trades():
    """Checks for any active orders or positions and returns Boolean accordingly"""
    checks = [check_orders(), check_positions()]
    no_trades = not any(checks)
    return no_trades, checks
