from functions import (save_json, edit_json, read_json, notify, check_trades,
                       needs_update, get_datetime, select_pairs, z_score,
                       unrealized_profit, exit_all_positions, trade
                       )

if __name__ == "__main__":
    print("Bot Initiated")

    # Initialising variables
    status_dict = {"message": "starting..."}
    order_long = {}
    order_short = {}
    positive_signal = False
    signal_side = ""
    switch = 0

    save_json(status_dict, "status.json")

    print("Looking for trades...")

    while True:

        noTrades, checks = check_trades()  # Checking for any open orders or positions

        # Choosing the most recently co-integrated pairs
        if noTrades and needs_update():
            instrument_1, instrument_2 = select_pairs()
            print(f" Selected {instrument_1} & {instrument_2} to trade")
            noTrades, checks = check_trades()

        if get_datetime() >= read_json("next_update")["next_update"]:
            notify()
            edit_json(next_update=get_datetime(delta=1, time_str=17))

        # Saving status
        status_dict["message"] = "Initial checks made..."
        status_dict["checks"] = checks
        save_json(status_dict, "status.json")

        # Checking for signal and place new trades
        if noTrades and switch == 0:
            status_dict["message"] = "Managing new trades..."
            save_json(status_dict, "status.json")
            switch, signal_side = trade(switch)

        if switch == 1:
            # Calculating the latest z-score
            zscore, positive_signal = z_score()
            profit = unrealized_profit()

            if profit > 0:
                if signal_side == "positive" and zscore < 0:
                    switch = 2
                if signal_side == "negative" and zscore >= 0:
                    switch = 2

            # Switching back to zero if trades are closed
            nuevaNoTrades, _ = check_trades()
            if nuevaNoTrades and switch != 2:
                switch = 0

        # Closing all active orders and open positions
        if switch == 2:
            print("Closing all positions...")
            status_dict["message"] = "Closing existing trades..."
            save_json(status_dict, "status.json")
            switch = exit_all_positions()
            exit_all_positions()  # For good measures
            print("All active positions and open orders are closed")
