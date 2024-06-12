from src.functions.data_collection.cointegration import calc_spread, calc_zscore, close_prices
from .data_collection.candles import get_candles
from .trade_details import calc_trade_details
from statsmodels.tsa.stattools import coint
from src.endpoints import orderbook_url
from .connect import public_requests
from .data_handler import read_json
import statsmodels.api as sm


def calculate_metrics(series_1, series_2):
    """Calculates co-integration and z-score of the two given series"""
    window = read_json("window")["window"]

    coint_flag = 0
    coint_res = coint(series_1, series_2)
    coint_t = coint_res[0]
    p_value = coint_res[1]
    critical_value = coint_res[2][1]
    model = sm.OLS(series_1, series_2).fit()
    hedge_ratio = model.params[0]
    spread = calc_spread(series_1, series_2, hedge_ratio)
    zscore_list = calc_zscore(spread, window)
    if p_value < 0.5 and coint_t < critical_value:
        coint_flag = 1

    return coint_flag, zscore_list.tolist()


def z_score():
    """Calculates z-score of the two tickers based on mid-prices, using the latest order book data."""
    values = read_json("instrument_1", "instrument_2", "interval", "klines")
    instrument_1, instrument_2, interval, klines = values.values()

    # Getting latest asset orderbook prices and adding dummy price for latest
    orderbook1 = public_requests(orderbook_url, symbol=instrument_1, productType="USDT-FUTURES")

    # Checking error to return structured orderbook 1
    if not orderbook1 or not orderbook1.get("msg") == "success":
        return
    else:
        orderbook_1 = orderbook1["data"]

    mid_price_1, _, _, = calc_trade_details(instrument_1, orderbook_1)

    orderbook2 = public_requests(orderbook_url, symbol=instrument_2, productType="USDT-FUTURES")

    # Checking error to return structured orderbook 2
    if not orderbook2 or not orderbook2.get("msg") == "success":
        return
    else:
        orderbook_2 = orderbook2["data"]

    mid_price_2, _, _, = calc_trade_details(instrument_2, orderbook_2)

    # Getting latest price history
    series_1 = close_prices(get_candles(instrument_1, interval, klines))
    series_2 = close_prices(get_candles(instrument_2, interval, klines))

    # Getting z_score to confirm if hot
    if len(series_1) > 0 and len(series_2) > 0:

        # Replacing last kline price with latest orderbook mid-price
        series_1 = series_1[:-1]
        series_2 = series_2[:-1]
        series_1.append(mid_price_1)
        series_2.append(mid_price_2)

        # Getting latest zscore
        _, zscore_list = calculate_metrics(series_1, series_2)
        zscore = zscore_list[-1]
        if zscore > 0:
            signal_sign_positive = True
        else:
            signal_sign_positive = False

        # Return output
        return zscore, signal_sign_positive

    return  # Return output if not true
