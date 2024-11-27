import time
from substrateinterface import SubstrateInterface
from decimal import Decimal
import logging
from modules.notifications import NotificationManager



class BalanceChecker:
    def __init__(self, node_url, addresses, check_interval, notification_config, run_as_tmux):
        """
        Initialize the BalanceChecker.
        """
        self.node_url = node_url
        self.addresses = addresses
        self.check_interval = check_interval
        self.run_as_tmux = run_as_tmux
        self.first_cycle = True
        self.previous_balances = {}

    

        # Configure logging
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s [%(levelname)s] %(message)s"
        )
        logging.info("BalanceChecker initialized")
        


    def connect_to_node(self):
        """
        Connect to the Substrate node.
        """
        try:
            self.substrate = SubstrateInterface(url=self.node_url)
            #logging.info("Successfully connected to the node")
        except Exception as e:
            logging.error(f"Failed to connect to node: {e}")
            self.substrate = None

    def truncate_address(self, address):
        """
        Truncate a wallet address for display purposes.
        """
        return f"{address[:4]}...{address[-4:]}"

    def get_balance(self, address):
        
        """
        Retrieve the balance for a specific wallet address.
        """
        try:
            result = self.substrate.query('System', 'Account', [address])
            free_balance = result['data']['free'].value
            balance_decimal = round(Decimal(free_balance) / Decimal(10**18), 5)
            logging.debug(f"Balance for {self.truncate_address(address)}: {balance_decimal}")
            return balance_decimal
        except Exception as e:
            logging.error(f"Error retrieving balance for {self.truncate_address(address)}: {e}")
            return None

    def check_balances(self):
        """
        Check balances for all configured wallet addresses.
        """
        #logging.info("Running check_balances, not as Statusbar")
        self.connect_to_node()
        if not self.substrate:
            logging.warning("Connection to node failed. Skipping this cycle.")
            return

        for address in self.addresses:
            current_balance = self.get_balance(address)
            if current_balance is None:
                logging.warning(f"Failed to retrieve balance for {self.truncate_address(address)}. Skipping.")
                continue

            previous_balance = self.previous_balances.get(address)

            # Notify only if balance has changed (not first cycle)
            if previous_balance is not None and current_balance != previous_balance:
                change = round(current_balance - previous_balance, 3)
                message = (
                    f"Balance change detected for {self.truncate_address(address)}:\n"
                    f"Change: {current_balance} ({'+' if change > 0 else '-'} {change} AI3)\n"
                )
            
                logging.info(message)
                self.notify(message)

            # Update the balance for the next cycle
            self.previous_balances[address] = current_balance

        # First cycle completed
        self.first_cycle = False
        time.sleep(self.check_interval)

    def run_as_statusbar(self):
        """
        Continuously output balance updates for tmux status bar.
        """
        logging.info("Running as Statusbar")
        self.connect_to_node()
        if not self.substrate:
            print("Error: Unable to connect to node")
            return

        while True:
            try:
                status_line = []
                for address in self.addresses:
                    balance = self.get_balance(address)
                    if balance is not None:
                        status_line.append(f"{self.truncate_address(address)}: {balance:.6f}")
                print(" | ".join(status_line), flush=True)
                time.sleep(self.check_interval)
            except KeyboardInterrupt:
                break
