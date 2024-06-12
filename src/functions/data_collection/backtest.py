from .cointegration import close_prices, calc_spread, cointegrate
from src.paths import backtest_results, backtest_data
from src.functions.data_collection.candles import get_candles
from src.functions.data_handler import read_json, edit_json
import matplotlib.pyplot as plt
import pandas as pd


def calc_zscore(spread):
    """Calculates Z-score of the spread of the two series"""
    window = read_json("window")["window"]
    df = pd.DataFrame(spread)
    mean = df.rolling(center=False, window=window).mean()
    std = df.rolling(center=False, window=window).std()
    x = df.rolling(center=False, window=1).mean()
    df["ZSCORE"] = (x - mean) / std
    return df["ZSCORE"].astype(float).values


def get_backtest_data(symbol_1, symbol_2):
    """Gets the candles data and calculates the spread & z-score and saves it in a csv file for backtesting"""
    # Loading the price data
    time_frame, count = read_json("interval", "klines").values()
    candles_1 = get_candles(symbol=symbol_1, size=time_frame, number=count)
    candles_2 = get_candles(symbol=symbol_2, size=time_frame, number=count)
    prices_1, prices_2 = close_prices(candles_1), close_prices(candles_2)

    # Getting spread and z-score
    _, _, _, _, hedge_ratio, zero_crossing = cointegrate(prices_1, prices_2)
    spread = calc_spread(prices_1, prices_2, hedge_ratio)
    zscore = calc_zscore(spread)

    df = pd.DataFrame()
    df[symbol_1] = prices_1
    df[symbol_2] = prices_2
    df["Spread"] = spread
    df["Z-Score"] = zscore

    df.to_csv(backtest_data)
    print("Backtesting data has been saved.")
    return df


def backtest(symbol_1, symbol_2):
    """Performs backtest and determines which pairs to go long and short on"""

    data = get_backtest_data(symbol_1, symbol_2)
    price_data = {symbol_1: data[symbol_1], symbol_2: data[symbol_2]}
    positions = []
    threshold, window, capital = read_json("trigger", "window", "capital").values()

    # Iterating through each row in the data
    for i in range(len(data)):
        # Calculating Z-score
        spread_mean = data['Spread'].iloc[max(0, i - window):i + 1].mean()
        spread_std = data['Spread'].iloc[max(0, i - window):i + 1].std()
        z_score = (data['Spread'].iloc[i] - spread_mean) / spread_std

        # Checking for entry/exit signals
        if z_score > threshold:
            # Long asset 1 and short asset 2
            position1 = 1
            position2 = 0  # Since we're not shorting now
        elif z_score < -threshold:
            # Short asset 1 and long asset 2
            position1 = 0  # Since we're not shorting now
            position2 = 1
        else:
            # Clear positions
            position1 = 0
            position2 = 0

        positions.append((position1, position2))

    # Backtesting
    capital1 = capital * .5  # Initial capital for asset 1
    capital2 = capital - capital1  # Initial capital for asset 2
    cap = capital1 + capital2
    portfolio_values = []

    for i in range(len(data)):
        position1, position2 = positions[i]
        price1 = data[symbol_1].iloc[i]
        price2 = data[symbol_2].iloc[i]

        # Updating capital based on positions
        capital1 += position1 * price1
        capital2 += position2 * price2

        # Calculating portfolio value
        portfolio_value = capital1 + capital2
        portfolio_values.append(portfolio_value)

    # Outputting results
    results = pd.DataFrame({
        'Date': data.index,
        'Portfolio_Value': portfolio_values
    })
    results.to_csv(backtest_results, index=False)

    plot_charts(symbol_1, symbol_2, price_data)

    signal_negative_ticker, signal_positive_ticker = (symbol_1, symbol_2) \
        if cap < portfolio_values[-1] else (symbol_2, symbol_1)

    edit_json(signal_negative_ticker=signal_negative_ticker,
              signal_positive_ticker=signal_positive_ticker)


def plot_charts(symbol_1, symbol_2, price_data):
    """Plots charts for the price movement, spread, and Z-score of two symbols."""
    # Extracting prices to plot the trends
    prices_1, prices_2 = price_data.values()

    # Getting spread and z-score
    _, _, _, _, hedge_ratio, zero_crossing = cointegrate(prices_1, prices_2)
    spread = calc_spread(prices_1, prices_2, hedge_ratio)
    zscore = calc_zscore(spread)

    # Calculating percentage changes
    df = pd.DataFrame(columns=[symbol_1, symbol_2])
    df[symbol_1] = prices_1
    df[symbol_2] = prices_2
    df[f"{symbol_1}_pct"] = df[symbol_1] / prices_1[0]
    df[f"{symbol_2}_pct"] = df[symbol_2] / prices_2[0]
    series_1 = df[f"{symbol_1}_pct"].astype(float).values
    series_2 = df[f"{symbol_2}_pct"].astype(float).values

    # Labeling charts
    fig, axs = plt.subplots(3, figsize=(16, 8))
    fig.suptitle(f"Price Movement")
    axs[1].set_title("Spread")
    axs[2].set_title("Z-Score")

    # Plotting price chart
    axs[0].plot(series_1, label=symbol_1)
    axs[0].plot(series_2, label=symbol_2)
    axs[0].legend()

    # Plotting spread
    axs[1].plot(spread, label='Spread')
    axs[1].legend()

    # Plotting z-scores
    axs[2].plot(zscore, label='Z-Score')
    axs[2].legend()

    plt.get_current_fig_manager().set_window_title(f"Price, Spread and Z-Score - {symbol_1} & {symbol_2}")
    plt.tight_layout()  # To adjust subplot layout
    plt.show()
