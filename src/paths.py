from pathlib import Path

# Project directory path
root = Path(__file__).parents[1]

# File Paths
config = root/"src"/"config.json"
symbols_file = root / "reports" / "symbols.json"
candlesticks_file = root/"reports"/"candlesticks.json"
pairs_file = root / "reports" / "co-integrated_pairs.csv"
backtest_data = root/"reports"/"backtest_data.csv"
backtest_results = root/"reports"/"backtest_results.csv"
recent_trades = root/"reports"/"recent_trades.csv"
trade_history = root/"reports"/"trade_history.csv"
order_records = root/"reports"/"order_records.csv"
