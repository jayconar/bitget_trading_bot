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
- Install all the necessary libraries listed in `requirements.txt`using the following command:
   ```bash
   pip install -r requirements.txt
   ```
- Create Bitget API keys (create on the Bitget Exchange platform) and Save them as environmental variables using the following commands:
  ```bash
   setx bitget_key "<API KEY HERE>"
   setx bitget_private "<SECRET KEY HERE>"
   setx bitget_passphrase "<PASSPHRASE HERE>"
   ```
- Email account with App password (or account password) for notifications (Don't forget to change the smtp server according to your email in `send_email.py`)
  ```bash
   setx email_password "<EMAIL PASSWORD HERE>"
  ```
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
3. Terminate the program to stop trading:
   - Simply stop the running program to end bot activity. 
   - If you are not sure, just restart your machine or delete the API keys as a kill switch. 
---

## Configuration
You can adjust the different parameters in the `config.json` file.
Make sure to save the bitget API keys & email password as environmental variables.
---

## Risk Disclaimer
Trading cryptocurrencies involves significant risk and may result in the loss of capital. This bot is intended for educational and research purposes only.
I have never tested this bot with real money. I cannot guarantee that it will generate you profits. Use it at your own risk.
---

## Contact
For any inquiries or support, reach out at jaysubhashconar@gmail.com.
