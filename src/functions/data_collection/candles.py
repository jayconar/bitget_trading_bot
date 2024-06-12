from src.paths import symbols_file, candlesticks_file
from ..data_handler import read_json, save_json
from ..connect import public_requests
from src.endpoints import candles_url
from src.config import interval_dict
import json
import time


def get_candles(symbol, size, number):
    """Simple function to get the candlestick data for the symbol passed in"""
    number = 1000 if number > 1000 else number
    start = int(time.time() - ((interval_dict[size] * 60) * number)) * 1000  # Timestamp of the oldest candle
    end = int(time.time()) * 1000  # Time now

    response = public_requests(candles_url, symbol=symbol, productType="USDT-FUTURES",
                               granularity=size, startTime=start, endTime=end, limit=number)
    # Making sure no error
    if response and response.get("code") == "00000" and response.get("msg") == "success":
        candle_data = response["data"][:-(number+1):-1]
        return candle_data[::-1]
    return {}


def candles():
    """Fetches candlestick data for the available symbols and stores them in a file"""
    size, number = read_json("interval", "klines").values()
    candles_list = {}

    # Getting all the available symbols
    with open(symbols_file, "r") as file:
        symbols = json.load(file)

    # Fetching data for every symbol
    for symbol in symbols:
        response = get_candles(symbol, size, number)
        if len(response) == number:
            candles_list[symbol] = response
            print(f"Fetched candles for {symbol}")
        else:
            print(f"Not enough data for {symbol}({len(response)})")

    # Saving the data in a json file
    save_json(candles_list, candlesticks_file)
    return len(candles_list)
