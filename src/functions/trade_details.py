from src.endpoints import trade_history_url
from .connect import private_requests
from .data_handler import read_json


def get_ticker_trade_liquidity(ticker):
    """Calculates the average liquidity of a ticker based on its last 50 trades"""
    # Getting last fifty trades
    response = private_requests(trade_history_url,
                                symbol=ticker, productType="USDT-FUTURES", limit=50)

    # Getting the list to calculate the average liquidity
    quantity_list = []
    if not response or not response.get("msg") == "success" or not response.get("data"):
        return
    for trade in response.get("data"):
        quantity_list.append(trade["qty"])

    if len(quantity_list) > 0:
        avg_liq = sum(quantity_list) / len(quantity_list)
        res_trades_price = float(response["data"][0]["price"])
        return avg_liq, res_trades_price
    return 0, 0


def calc_trade_details(ticker, orderbook, direction="long", capital=0):
    """Calculates relevant trade metrics like limit price and quantity along with the stop loss"""

    fail_safe, ticker_1, ticker_2, rounding_1, rounding_2, quantity_rounding_1, quantity_rounding_2 = read_json(
        "stop_loss", "instrument_1", "instrument_2", "rounding_1", "rounding_2", "qty1_rounding", "qty2_rounding"
    ).values()

    # Setting calculation and output variables
    mid_price = 0
    quantity = 0
    stop_loss = 0
    bid_items_list = []
    ask_items_list = []

    # Getting prices, stop loss and quantities
    if orderbook:

        # Setting price & quantity rounding
        price_rounding = rounding_1 if ticker == ticker_1 else rounding_2
        quantity_rounding = quantity_rounding_1 if ticker == ticker_1 else quantity_rounding_2

        # Organising prices
        for level in orderbook["bids"]:
            bid_items_list.append(float(level[0]))
        for level in orderbook["asks"]:
            ask_items_list.append(float(level[0]))

        # Calculating price, size, stop loss and average liquidity
        if len(ask_items_list) > 0 and len(bid_items_list) > 0:

            # Sorting the lists
            ask_items_list.sort()
            bid_items_list.sort()
            bid_items_list.reverse()

            # Getting the nearest ask, nearest bid and orderbook spread
            nearest_ask = ask_items_list[0]
            nearest_bid = bid_items_list[0]

            # Calculate hard stop loss
            if direction == "long":
                mid_price = nearest_bid  # Placing at Bid has high probability of not being canceled, but may not fill
                stop_loss = round(mid_price * (1 - fail_safe), price_rounding)
            else:
                mid_price = nearest_ask  # placing at Ask has high probability of not being canceled, but may not fill
                stop_loss = round(mid_price * (1 + fail_safe), price_rounding)

            # Calculate quantity
            quantity = round(capital / mid_price, quantity_rounding)

    # Output results
    return mid_price, stop_loss, quantity
