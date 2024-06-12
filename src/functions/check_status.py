from .position_calls import get_order_details, get_position_details, query_positions
from .trade_details import calc_trade_details
from src.endpoints import orderbook_url
from .connect import public_requests
from .data_handler import read_json


def unrealized_profit():
    """Returns the unrealized profit of an active position"""
    ticker1, ticker2, quote = read_json(
        "long_ticker", "short_ticker", "quote_currency").values()
    tickers = [ticker1, ticker2]
    profit = 0

    for ticker in tickers:
        response = get_position_details(ticker, quote)

        if response.get("data"):
            profit += response.get("data")["unrealizedPL"]

    return profit


def check_order_status(ticker, order_id, remaining_capital, direction="long"):
    """Queries the order using its order ID and returns the order status"""
    quote = read_json("quote_currency")["quote_currency"]

    # Get current orderbook
    orderbook = public_requests(orderbook_url, symbol=ticker, productType="USDT-FUTURES")

    # Checking error to return structured orderbook 1
    if not orderbook or not orderbook.get("msg") == "success":
        return
    else:
        orderbook = orderbook.get("data")

    # Get latest price
    mid_price, _, _ = calc_trade_details(
        ticker, orderbook, direction=direction, capital=remaining_capital)

    print(mid_price)

    # Get trade details
    order_details = get_order_details(ticker, order_id)
    status = order_details.get("status")

    # Get open positions
    position_price, position_quantity = query_positions(ticker, quote)

    # Determine action - trade complete - stop placing orders
    if position_quantity >= remaining_capital and position_quantity > 0:
        print(f"position_quantity {position_quantity}", f"remaining_capital {remaining_capital}")
        return "Trade Complete"

    # Determine action - position filled - buy more
    if status == "filled":
        return "Position Filled"

    # Determine action - order active - do nothing
    if status == "live":
        return "Order Active"

    # Determine action - partial filled order - do nothing
    if status == "partially_filled":
        return "Partial Fill"

    # Determine action - order failed - try place order again
    if status == "canceled":
        return "Try Again"
