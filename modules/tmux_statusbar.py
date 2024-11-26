import time
import threading

from modules.AutonomysWallet import BalanceChecker
from system_stats import fetch_system_stats


def fetch_wallet_data(checker, addresses):
    """
    Fetch wallet balance data from the wallet checker.
    """
    wallet_status = []
    for address in addresses:
        balance = checker.get_balance(address)
        if balance is not None:
            # Use plain text for tmux compatibility
            wallet_status.append(f"{address[:6]}: {balance:.4f}")
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

    # Run continuously to update the status bar
    while True:
        try:
            # Fetch wallet and system data
            wallet_data = fetch_wallet_data(checker, config["addresses"])
            system_data = fetch_system_stats()

            # Combine data into a single line
            combined_status = f"{wallet_data} | {system_data}"

            # Print the combined status line (tmux captures this)
            print(combined_status, flush=True)

            # Update every 10 seconds
            time.sleep(10)
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Error in status bar updater: {e}", flush=True)
            time.sleep(10)


if __name__ == "__main__":
    main()
