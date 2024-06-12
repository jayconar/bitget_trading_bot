import os

api_key = os.environ.get("bitget_key")
api_secret = os.environ.get("bitget_private")
passphrase = os.environ.get("bitget_passphrase")
email_password = os.environ.get("email_password")

interval_dict = {"1m": 1, "3m": 3, "5m": 5, "15m": 15, "30m": 30,
                 "1H": 60, "4H": 60 * 4, "6H": 60 * 6, "1D": 60 * 24,
                 "3D": 60 * 24 * 3, "1W": 60 * 24 * 7, "1M": 60 * 24 * 30}
