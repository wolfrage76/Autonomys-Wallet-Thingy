import time
from substrateinterface import SubstrateInterface, Keypair
from decimal import Decimal
import requests
import json
import logging

class BalanceChecker:
    def __init__(self, node_url, addresses, check_interval, discord_webhook=None, pushbullet_token=None):
        self.node_url = node_url
        self.addresses = addresses
        self.check_interval = check_interval
        self.discord_webhook = discord_webhook
        self.pushbullet_token = pushbullet_token
        self.previous_balances = {}
        self.first_cycle = True

        # Configure logging
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s [%(levelname)s] %(message)s"
        )
        logging.info("BalanceChecker initialized")

    def connect_to_node(self):
        try:
            self.substrate = SubstrateInterface(
                url=self.node_url,
                # type_registry_preset='substrate-node-template'
            )
            #logging.info("Successfully connected to the node")
        except Exception as e:
            logging.error(f"Failed to connect to node: {e}")
            self.substrate = None

    def get_balance(self, address):
        try:
            result = self.substrate.query('System', 'Account', [address])
            free_balance = result['data']['free'].value  # Use .value for U128
            balance_decimal = round(Decimal(free_balance) / Decimal(10**18), 5)  # Adjust for Substrate's decimal format
            short_address = address[-4:]  # Display only the last 4 characters of the address
            logging.debug(f"Balance for ...{short_address}: {balance_decimal}")
            return balance_decimal
        except AttributeError as e:
            logging.error(f"Attribute error while retrieving balance for {address}: {e}")
            logging.error(f"Result structure: {result}")
            return None
        except Exception as e:
            logging.error(f"Error retrieving balance for {address}: {e}")
            return None

    def notify(self, message):
        if self.discord_webhook:
            self.send_discord_notification(message)
        if self.pushbullet_token:
            self.send_pushbullet_notification(message)

    def send_discord_notification(self, message):
        try:
            payload = {"content": message}
            response = requests.post(self.discord_webhook, json=payload)
            response.raise_for_status()
        except Exception as e:
            logging.error(f"Error sending Discord notification: {e}")

    def send_pushbullet_notification(self, message):
        try:
            headers = {
                'Access-Token': self.pushbullet_token,
                'Content-Type': 'application/json'
            }
            payload = {"type": "note", "title": "Balance Alert", "body": message}
            response = requests.post("https://api.pushbullet.com/v2/pushes", json=payload, headers=headers)
            response.raise_for_status()
        except Exception as e:
            logging.error(f"Error sending Pushbullet notification: {e}")

    def check_balances(self):
        self.connect_to_node()
        if not self.substrate:
            logging.warning("Connection to node failed. Skipping this cycle.")
            return

        for address in self.addresses:
            current_balance = self.get_balance(address)
            if current_balance is None:
                logging.warning(f"Failed to retrieve balance for {address}. Skipping.")
                continue

            previous_balance = self.previous_balances.get(address)

            # Notify only if this is not the first cycle and balance has changed
            if previous_balance is not None and current_balance != previous_balance:
                message = (
                    f"Balance change detected for {address[:4]}...{address[-4:]}\nChange: {current_balance} ({round(current_balance - previous_balance,3)} AI3)\n"
                )
                logging.info(message)
                self.notify(message)
            else:
                # logging.info(f"Checked balance for {address[-4:]}...{address[:4]}:No Change ({current_balance})")
                pass
            # Update the balance for the next cycle
            self.previous_balances[address] = current_balance

        # First cycle completed
        self.first_cycle = False

    def start_monitoring(self):
        while True:
            self.check_balances()
            time.sleep(self.check_interval)
