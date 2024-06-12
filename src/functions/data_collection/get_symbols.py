from ..data_handler import read_json, save_json
from ..connect import public_requests
from src.endpoints import symbols_url
from src.paths import symbols_file


def get_symbols():
    """Gets the list of available trade pairs and stores them in a file"""

    # Getting USDT Futures contracts only
    response = public_requests(symbols_url, productType="USDT-FUTURES")
    quote = read_json("quote_currency")["quote_currency"]
    data = {}

    # Checking if the request encountered any error
    if response and response.get("code") == "00000" and response.get("msg") == "success":
        for product in response.get("data"):

            # Getting only active trade-able pairs
            conditions = [product.get("symbol").endswith(quote)]

            # Structuring the data
            if all(conditions):
                data[product["symbol"]] = product

        # Storing the data in a json file
        save_json(data, symbols_file)
        return len(data)
    return 0
