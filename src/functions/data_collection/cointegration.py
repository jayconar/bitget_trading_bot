from statsmodels.tsa.stattools import coint
from src.paths import pairs_file
import statsmodels.api as sm
import pandas as pd
import numpy as np
import math


def close_prices(prices):
    """Extracts Close prices from candlestick data"""
    closing_prices = [float(candle[4]) for candle in prices if not math.isnan(float(candle[4]))]
    return closing_prices


def calc_zscore(series, window_size):
    """Calculates Z-Score"""
    mean = series.rolling(window=window_size).mean()
    std = series.rolling(window=window_size).std()
    zscore = (series - mean) / std
    return zscore


def calc_spread(series_1, series_2, hedge_ratio):
    """Calculates the Spread between two series"""
    spread = pd.Series(series_1) - (pd.Series(series_2) * hedge_ratio)
    return spread


def cointegrate(series_1, series_2):
    """Calculates and determines a co-integrated pair"""
    coint_test = 0
    t_value, p_value, critical_value = coint(series_1, series_2)
    model = sm.OLS(series_1, series_2).fit()  # To calculate the hedge ratio
    hedge_ratio = model.params[0]
    spread = calc_spread(series_1, series_2, hedge_ratio)
    zero_crossings = len(np.where(np.diff(np.sign(spread)))[0])
    if p_value < 0.5 and t_value < critical_value[1]:
        coint_test = 1
    return (coint_test, round(p_value, 2), round(t_value, 2),
            round(critical_value[1], 2), round(hedge_ratio, 2), zero_crossings)


def cointegrated_pairs(prices):
    """Takes the available symbols, finds all possible co-integrated pairs and stores it"""
    pairs = []
    included_pairs = []

    for symbol_1 in list(prices.keys()):
        for symbol_2 in list(prices.keys()):
            if symbol_2 != symbol_1:
                sorted_characters = sorted(symbol_1 + symbol_2)
                unique = "".join(sorted_characters)
                if unique in included_pairs:
                    break

                series_1 = close_prices(prices[symbol_1])
                series_2 = close_prices(prices[symbol_2])

                coint_test, p_value, t_value, c_value, hedge_ratio, zero_crossings = cointegrate(series_1, series_2)
                if coint_test:
                    included_pairs.append(unique)
                    pairs.append({
                        "Instrument-1": symbol_1,
                        "Instrument-2": symbol_2,
                        "p-value": p_value,
                        "t-value": t_value,
                        "critical value": c_value,
                        "hedge_ratio": hedge_ratio,
                        "Zero_crossings": zero_crossings
                    })
    if not pairs:
        print("No cointegrated pairs found; Try adjusting the candle limit and interval")
        return None
    coint_df = pd.DataFrame(pairs).sort_values(by="Zero_crossings", ascending=False)
    coint_df.to_csv(pairs_file, index=False)
    print("Calculations completed; Report has been saved in co-integrated_pairs.csv")
    return len(coint_df)
