import time
import threading

from modules.AutonomysWallet import BalanceChecker
from system_stats import fetch_system_stats
from modules.notifications import NotificationManager

def fetch_wallet_data(checker, addresses, notification_manager):
    """
    Fetch wallet balance data from the wallet checker.
    """
    wallet_status = []
    for address in addresses:
        balance = checker.get_balance(address)
        if balance is not None:
            # Use plain text for tmux compatibility
            wallet_status.append(f"{address[:6]}: {balance:.4f}")
            # Check if there's a change and notify
            last_balance = checker.last_balances.get(address)
            if last_balance is not None and balance != last_balance:
                change = balance - last_balance
                message = f"Balance change detected for {address[:6]}: {change:+.4f} AI3 (New Balance: {balance:.4f} AI3)"
                #notification_manager.send_notification(message)
        checker.last_balances[address] = balance
    return " | ".join(wallet_status)

def main():
    """
    Combine wallet data and system stats, and print a single-line status
    for tmux status-right.
    """
    # Load configuration
    from WalletThingy import load_config
    config = load_config()

    # Initialize the BalanceChecker
    checker = BalanceChecker(
        node_url=config["node_url"],
        addresses=config["addresses"],
        check_interval=config["check_interval"],
        notification_config=config["notifications"],
        run_as_tmux=config["run_as_tmux"],
    )

    # Initialize the NotificationManager
    notification_manager = NotificationManager(
        discord_webhook=config["notifications"].get("discord_webhook"),
        pushbullet_token=config["notifications"].get("pushbullet_token"),
        pushover_config=config["notifications"].get("pushover"),
        telegram_config=config["notifications"].get("telegram"),
    )
    
    # Run continuously to update the status bar
    while True:
        try:
            # Fetch wallet and system data
            wallet_data = fetch_wallet_data(checker, config["addresses"], notification_manager)
            system_data = fetch_system_stats()

            # Combine data into a single line
            combined_status = f"{wallet_data} | {system_data}"

            # Print the combined status line (tmux captures this)
            print(combined_status, flush=True)

            # Update every 10 seconds
            time.sleep(5)
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Error in status bar updater: {e}", flush=True)
            time.sleep(10)

if __name__ == "__main__":
    main()
