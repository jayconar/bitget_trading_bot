from .connect import public_requests, private_requests
from src.endpoints import orderbook_url, place_order_url
from .data_handler import read_json, edit_json
from .trade_details import calc_trade_details


def place_order(ticker, quantity, side, order_type="market", price=0):
    """Places limit or market order"""
    quote = read_json("quote_currency")["quote_currency"]

    kwargs = {
        "symbol": ticker,
        "productType": "USDT-FUTURES",
        "orderType": order_type,
        "marginMode": "isolated",
        "side": side,
        "marginCoin": quote,
        "size": quantity,
    }
    if type == "limit":
        kwargs["price"] = price

    response = private_requests(place_order_url, method="POST", **kwargs)
    return response


def execute_order(ticker, direction, capital):
    """Initiates limit order placement and saves order details"""
    orderbook = public_requests(orderbook_url, symbol=ticker, productType="USDT-FUTURES")
    # Exit if error
    if not orderbook or not orderbook.get("msg") == "success":
        return

    if orderbook:
        mid_price, stop_loss, quantity = calc_trade_details(
            orderbook["data"], direction, capital)
        if quantity > 0:
            side = "buy" if direction == "long" else "sell"
            response = place_order(ticker, quantity, side,
                                   order_type="limit", price=mid_price)

            if response and response.get("msg") == "success":
                if response.get("data"):
                    order_id = response["data"]["orderId"]
                    # Saving order details
                    edit_json(**{f"{direction}_orderid": order_id,
                                 f"{direction}_ticker": ticker,
                                 f"entry_{direction}": mid_price})
                    return order_id
    return 0
