from .trade_details import get_ticker_trade_liquidity
from .check_status import check_order_status
from .connect import private_requests
from src.endpoints import cancel_all
from .data_handler import read_json
from .order import execute_order
from .z_score import z_score
import time


def trade(kill_switch):
    """Executes the trading strategy by analysing z-score, placing and managing trades dynamically"""

    # Setting variables
    order_long_id = ""
    order_short_id = ""
    signal_side = ""
    hot = False
    trigger, signal_positive_ticker, signal_negative_ticker, capital = read_json(
        "trigger", "signal_positive_ticker", "signal_negative_ticker", "capital").values()

    # Calculating and saving the latest z-score
    zscore, signal_sign_positive = z_score()

    # Switch to hot if meets signal threshold
    # Note: You can add in coint-flag check too if you want extra vigilance
    if abs(zscore) > trigger:

        # Active hot trigger
        hot = True
        print("-- Trade Status HOT --")
        print("-- Placing and Monitoring Existing Trades --")

    # Place and manage trades
    if hot and kill_switch == 0:

        # Get trades history for liquidity
        avg_liquidity_ticker_p, last_price_p = get_ticker_trade_liquidity(signal_positive_ticker)
        avg_liquidity_ticker_n, last_price_n = get_ticker_trade_liquidity(signal_negative_ticker)

        # Determine long ticker vs short ticker
        if signal_sign_positive:
            long_ticker = signal_positive_ticker
            short_ticker = signal_negative_ticker
            avg_liquidity_long = avg_liquidity_ticker_p
            avg_liquidity_short = avg_liquidity_ticker_n
            last_price_long = last_price_p
            last_price_short = last_price_n
        else:
            long_ticker = signal_negative_ticker
            short_ticker = signal_positive_ticker
            avg_liquidity_long = avg_liquidity_ticker_n
            avg_liquidity_short = avg_liquidity_ticker_p
            last_price_long = last_price_n
            last_price_short = last_price_p

        # Fill targets
        capital_long = capital * 0.5
        capital_short = capital - capital_long
        initial_fill_target_long_usdt = avg_liquidity_long * last_price_long
        initial_fill_target_short_usdt = avg_liquidity_short * last_price_short
        initial_capital_injection_usdt = min(initial_fill_target_long_usdt,
                                             initial_fill_target_short_usdt)

        # Ensure initial capital does not exceed limits set in configuration
        if initial_capital_injection_usdt > capital_long:
            initial_capital_usdt = capital_long
        else:
            initial_capital_usdt = initial_capital_injection_usdt

        # Set remaining capital
        remaining_capital_long = capital_long
        remaining_capital_short = capital_short

        # Trade until filled or signal is false
        order_status_long = ""
        order_status_short = ""
        counts_long = 0
        counts_short = 0
        while kill_switch == 0:

            # Place order - long
            if counts_long == 0:
                order_long_id = execute_order(long_ticker, "Long", initial_capital_usdt)
                counts_long = 1 if order_long_id else 0
                remaining_capital_long = remaining_capital_long - initial_capital_usdt

            # Place order - short
            if counts_short == 0:
                order_short_id = execute_order(short_ticker, "Short", initial_capital_usdt)
                counts_short = 1 if order_short_id else 0
                remaining_capital_short = remaining_capital_short - initial_capital_usdt

            # Update signal side
            if zscore > 0:
                signal_side = "positive"
            else:
                signal_side = "negative"

            # Handle kill switch for Market orders
            if counts_long and counts_short:
                kill_switch = 1

            # Allow for time to register the limit orders
            time.sleep(3)

            # Check limit orders and ensure z_score is still within range
            zscore_new, signal_sign_p_new = z_score()
            if kill_switch == 0:
                if abs(zscore_new) > trigger * 0.9 and signal_sign_p_new == signal_sign_positive:

                    # Check long order status
                    if counts_long == 1:
                        order_status_long = check_order_status(long_ticker, order_long_id, remaining_capital_long, "long")

                    # Check short order status
                    if counts_short == 1:
                        order_status_short = check_order_status(short_ticker, order_short_id, remaining_capital_short, "short")

                    print(order_status_long, order_status_short, zscore_new)

                    # If orders still active, do nothing
                    if order_status_long == "Order Active" or order_status_short == "Order Active":
                        continue

                    # If orders partial fill, do nothing
                    if order_status_long == "Partial Fill" or order_status_short == "Partial Fill":
                        continue

                    # If orders trade complete, do nothing - stop opening trades
                    if order_status_long == "Trade Complete" and order_status_short == "Trade Complete":
                        kill_switch = 1

                    # If position filled - place another trade
                    if order_status_long == "Position Filled" and order_status_short == "Position Filled":
                        counts_long = 0
                        counts_short = 0

                    # If order cancelled for long - try again
                    if order_status_long == "Try Again":
                        counts_long = 0

                    # If order cancelled for short - try again
                    if order_status_short == "Try Again":
                        counts_short = 0

                else:
                    # Cancel all active orders
                    private_requests(cancel_all, method="POST", productType="USDT-FUTURES")
                    print("Orders Canceled")
                    kill_switch = 1

    # Output status
    return kill_switch, signal_side
