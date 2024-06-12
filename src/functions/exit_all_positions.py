from .position_calls import query_orders, query_positions
from src.endpoints import cancel_all, close_position_url
from .data_handler import read_json, edit_json
from .connect import private_requests


def close_position(ticker, direction):
    """Closes long and short positions"""
    response = private_requests(close_position_url,
                                symbol=ticker, productType="USDT-FUTURES")

    if response and response.get("msg") == "success":

        if response.get("data") and response["data"]["successList"][0].get("orderId"):
            order_id = response["data"]["successList"][0]["orderId"]
            price, _ = query_orders(ticker, order_id)

            # Saving order details
            edit_json(**{f"{direction}_orderid": order_id,
                         f"{direction}_ticker": ticker,
                         f"entry_{direction}": price})
            return len(response["data"]["successList"])
    return 0


def exit_all_positions():
    """Exits all active positions and ends the trade"""
    long_ticker, short_ticker, quote = read_json(
        "long_ticker", "short_ticker", "quote_currency")

    # Canceling all active orders
    private_requests(cancel_all, method="POST", productType="USDT-FUTURES")

    # Getting position information
    _, size_1 = query_positions(long_ticker, quote)
    _, size_2 = query_positions(short_ticker, quote)

    if size_1 > 0:
        close_position(long_ticker, "long")
    if size_2 > 0:
        close_position(short_ticker, "short")

    # Output results
    kill_switch = 0
    return kill_switch
