# Auto Trading Program for Bitget: Statistical Arbitrage (Pairs Trading)

## Overview
This project is an automated trading bot designed for the **Bitget Exchange**. The bot leverages the concept of **Statistical Arbitrage** through **Pairs Trading** by identifying **cointegrated pairs** of cryptocurrencies and executing trades based on the **mean reversion theory**. The strategy assumes that deviations from the typical relationship between asset prices are temporary and will eventually revert to their mean.

The bot also supports periodic **email notifications** to keep you informed about trade updates and performance.

---

## Features
- **Cointegration Detection:** Finds statistically cointegrated crypto pairs to trade.
- **Mean Reversion Strategy:** Buys undervalued assets and sells overvalued ones when the spread between pairs deviates significantly.
- **Automated Trade Execution:** Places buy/sell orders on Bitget based on trading signals.
- **Risk Management:** Includes parameters for stop-loss and take-profit.
- **Email Notifications:** Sends regular trade updates via email.
- **Error Handling:** Ensures smooth execution and recovery in case of API failures.

---

## How It Works
1. **Data Collection:** Fetches historical price data for selected trading pairs.
2. **Statistical Analysis:** Computes cointegration scores to identify stable pairs.
3. **Spread Calculation:** Monitors the spread between identified pairs.
4. **Trading Signals:** Executes trades when the spread deviates beyond a defined threshold.
5. **Trade Monitoring:** Continuously tracks trades and manages positions.
6. **Email Reports:** Sends periodic email updates on trade status and performance metrics.

---

## Installation
### Prerequisites
- Python 3.8 or higher
- Bitget API keys (create on the Bitget Exchange platform)
- Email account with App password for notifications (Gmail recommended)

---

## Usage
1. **Run the bot:**
   ```bash
   python main.py
   ```
2. The bot will:
   - Analyze the market for cointegrated pairs.
   - Monitor spread deviations and execute trades.
   - Send email updates with trade details.

---

## Configuration
You can adjust the different parameters in the `config.py` file.

---

## Risk Disclaimer
Trading cryptocurrencies involves significant risk and may result in the loss of capital. This bot is intended for educational and research purposes only. Use it at your own risk.

---

## Contact
For any inquiries or support, reach out at jaysubhashconar@gmail.com.

