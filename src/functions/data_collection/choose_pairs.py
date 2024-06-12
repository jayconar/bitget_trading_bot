from src.functions.data_collection.get_symbols import get_symbols
from src.paths import candlesticks_file, pairs_file, symbols_file
from src.functions.data_collection.candles import candles
from src.functions.data_handler import edit_json, read_json
from .cointegration import cointegrated_pairs
from src.functions.utils import get_datetime
from .backtest import backtest
import pandas as pd
import json
import os


def get_instruments():
    """Returns the pairs of a specified index from the data"""
    index = read_json("index")["index"]
    pairs_data = pd.read_csv(pairs_file)

    instrument_1 = pairs_data.iloc[index]['Instrument-1']
    instrument_2 = pairs_data.iloc[index]['Instrument-2']

    return instrument_1, instrument_2


def instruments():
    """Sets minimum order quantity, price decimal places and quantity decimal places for both pairs"""
    file = open(symbols_file, "r")
    data = json.load(file)

    # Selecting the pairs and updating the details
    instrument_1, instrument_2 = get_instruments()
    rounding_1, rounding_2 = [float(data[instrument_1]["indexPrice"]), float(data[instrument_2]["indexPrice"])]
    qty1_rounding, qty2_rounding = [float(data[instrument_1]["bidSz"]), float(data[instrument_2]["bidSz"])]

    edit_json(instrument_1=instrument_1, qty1_rounding=len(str(qty1_rounding).split('.')[-1]),
              instrument_2=instrument_2, qty2_rounding=len(str(qty2_rounding).split('.')[-1]),
              rounding_1=len(str(rounding_1).split('.')[-1]), rounding_2=len(str(rounding_2).split('.')[-1]))

    file.close()
    return instrument_1, instrument_2


def select_pairs():
    """Finds Co-integrated pairs for trading and creates the report"""
    # Getting available symbols to trade
    print("Fetching available symbols..")
    if get_symbols():
        print(f"Successfully fetched and stored candlestick data for {candles()} pairs")
    else:
        print("No symbols available for trading")
        return 0

    # Finding all co-integrated pairs using the historical price data
    if os.path.isfile(candlesticks_file):
        with open(candlesticks_file, "r") as file:
            prices = json.load(file)

        # Finding co-integrated pairs if enough candlesticks data is available
        if len(prices) >= 2:
            print("Calculating co-integration...")
            if cointegrated_pairs(prices):
                next_update = get_datetime(delta=1)
                edit_json(next_update=next_update)

                # Selecting the pairs based on the index set in config.json
                instrument_1, instrument_2 = instruments()
                if os.path.isfile(pairs_file):
                    # Backtesting the instruments to choose which pair to go long on
                    backtest(instrument_1, instrument_2)
                    return 1
    return 0
