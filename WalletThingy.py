import threading
import time
import shutil
import platform
import subprocess
import psutil
import logging
import yaml

from modules.notifications import NotificationManager
from itertools import cycle
from substrateinterface import SubstrateInterface

def setup_logging():
    """
    Configure logging settings.
    """
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s"
    )

def load_config():
    """
    Load the configuration file (config.yaml) for node connection,
    addresses, and notification settings.
    """
    try:
        with open("config.yaml", "r") as file:
            config = yaml.safe_load(file)
            return config
    except FileNotFoundError:
        logging.error("Error: config.yaml file not found. Please create the file and try again.")
        exit(1)
    except yaml.YAMLError as e:
        logging.error(f"Error reading config.yaml: {e}")
        exit(1)

def validate_config(config):
    """
    Validate the configuration file content.
    """
    if not config.get("node_url"):
        logging.error("Error: 'node_url' is required in config.yaml.")
        exit(1)

    addresses = config.get("addresses")
    if not addresses or not isinstance(addresses, list):
        logging.error("Error: 'addresses' must be a non-empty list in config.yaml.")
        exit(1)

def truncate_address(address):
    """
    Truncate a wallet address for display purposes.
    Example: sue1dbNHjokfnRG9Uqqd34C3VVDBZ5kyraHREAqzyvzsxuPFY -> sue1...uPFY
    """
    return f"{address[:4]}...{address[-4:]}"

class BalanceChecker:
    def __init__(self, node_url, addresses, telegram_chat_id=None, telegram_bot_token=None, check_interval=600, pushover_app_token=None, pushover_user_key=None, notification_config=None, run_as_tmux=False, discord_webhook=None, pushbullet_token=None, ):
        self.node_url = node_url
        self.addresses = addresses
        self.check_interval = check_interval
        self.notification_config = notification_config or {}
        self.run_as_tmux = run_as_tmux
        self.substrate = None
        self.last_balances = {}
        self.lock = threading.Lock()
        self.connect_to_node()
        self.initialize_balances()
        config = load_config()
        self.notification_manager = NotificationManager(
        discord_webhook=config["notifications"].get("discord_webhook"),
        pushbullet_token=config["notifications"].get("pushbullet_token"),
        pushover_user_key=config["notifications"].get("pushover", {}).get("user_key"),
        pushover_app_token=config["notifications"].get("pushover", {}).get("app_token"),
        
        
        telegram_bot_token=config["notifications"].get("telegram",{}).get('bot_token'),
        telegram_chat_id=config["notifications"].get("telegram",{}).get('chat_id'),
    )
        self.discord_webhook = discord_webhook
        self.pushbullet_token = pushbullet_token
        self.pushover_user_key = pushover_user_key
        self.pushover_app_token = pushover_app_token
        self.telegram_bot_token = telegram_bot_token
        self.telegram_chat_id = telegram_chat_id, telegram_bot_token
        
        
    def connect_to_node(self):
        """
        Connect to the blockchain node using substrate-interface.
        """
        try:
            self.substrate = SubstrateInterface(
                url=self.node_url,
                # Specify the type registry preset or custom types if needed
            )
            logging.info("Successfully connected to the node")
        except Exception as e:
            logging.error(f"Failed to connect to node: {e}")
            self.substrate = None

    def initialize_balances(self):
        """
        Initialize the last_balances dictionary with the current balances.
        """
        for address in self.addresses:
            balance = self.get_balance(address)
            with self.lock:
                self.last_balances[address] = balance

    def get_balance(self, address):
        """
        Retrieve the balance for a given address from the node.
        """
        try:
            result = self.substrate.query(
                module='System',
                storage_function='Account',
                params=[address]
            )
            balance = result.value['data']['free']
            # Convert balance from smallest unit to main unit (adjust exponent as needed)
            balance_main_unit = balance / 10**18
            return balance_main_unit
        except Exception as e:
            logging.error(f"Failed to get balance for address {address}: {e}")
            return None

    def start_monitoring(self, stop_event):
        """
        Monitor the balances and send notifications if there are changes.
        """
        logging.info("Starting balance monitoring...")
        self.notification_manager.send_notification('\tStarting balance monitoring...')
        while not stop_event.is_set():
            for address in self.addresses:
                balance = self.get_balance(address)
                if balance is not None:
                    with self.lock:
                        last_balance = self.last_balances.get(address)
                        if last_balance is not None and balance != last_balance:
                            change = balance - last_balance
                            logging.info(f"Balance change detected for {truncate_address(address)}: {change:.4f} AI3")
                            self.send_notification(address, self.format_with_commas(balance), change)
                        self.last_balances[address] = balance
            time.sleep(self.check_interval)
    def format_with_commas(number):

        try:
            # If it's a float, format to include commas and maintain decimals
            if isinstance(number, float):
                return f"{number:,.2f}"  # Adjust decimal places if needed
            # If it's an integer, format with commas
            elif isinstance(number, int):
                return f"{number:,}"
            else:
                raise ValueError("Input must be an int or float.")
        except Exception as e:
            raise ValueError(f"Error formatting number: {e}")
        
    
    def send_notification(self, address, balance, change):
        """
        Send a notification about the balance change.
        """
        balance = self.format_with_commas(balance)
        message = f"Balance change for {truncate_address(address)}: {change:+.4f} AI3 (New Balance: {balance:.4f} AI3)"
        
        logging.info(f"Sending notification: {message}")
        self.notification_manager.send_notification(message)

def fetch_gpu_stats(max_gpus=2):
    """
    Fetch NVIDIA-SMI stats for GPUs, displaying memory usage in GB,
    temperatures, and utilization percentage.
    Limit to `max_gpus` GPUs per update.
    """
    gpu_data = []
    try:
        if platform.system() == "Windows":
            command = [
                "nvidia-smi.exe",
                "--query-gpu=index,name,memory.used,memory.total,temperature.gpu,utilization.gpu",
                "--format=csv,noheader,nounits"
            ]
        else:
            command = [
                "nvidia-smi",
                "--query-gpu=index,name,memory.used,memory.total,temperature.gpu,utilization.gpu",
                "--format=csv,noheader,nounits"
            ]

        output = subprocess.check_output(command, text=True)
        gpus = output.strip().split("\n")
        for gpu in gpus:
            gpu_info = gpu.split(", ")
            if len(gpu_info) < 6:
                continue  # Skip incomplete GPU info
            index, name = gpu_info[0], gpu_info[1]
            mem_used_mb = float(gpu_info[2])
            mem_total_mb = float(gpu_info[3])
            temp = gpu_info[4]
            utilization = gpu_info[5]

            mem_used_gb = mem_used_mb / 1024
            mem_total_gb = mem_total_mb / 1024

            # Truncate GPU name if necessary
            truncated_name = name[:10] + '...' if len(name) > 13 else name # Remvoed from below

            gpu_data.append(
                f"GPU{index} {utilization}%: {mem_used_gb:.2f}/{mem_total_gb:.2f}GB {temp}°C"
            )
    except subprocess.CalledProcessError as e:
        logging.error(f"nvidia-smi command failed: {e}")
        gpu_data.append("No GPU Data")
    except FileNotFoundError:
        logging.error("nvidia-smi not found. Ensure NVIDIA drivers are installed.")
        gpu_data.append("No GPU Data")
    except Exception as e:
        logging.error(f"Failed to fetch GPU stats: {e}")
        gpu_data.append("No GPU Data")

    return gpu_data[:max_gpus]

def fetch_system_stats():
    """
    Fetch system statistics (CPU, memory).
    """
    try:
        # CPU utilization
        cpu_usage = psutil.cpu_percent(interval=1)

        # Memory utilization
        memory = psutil.virtual_memory()
        total_memory_gb = memory.total / (1024 ** 3)
        used_memory_gb = memory.used / (1024 ** 3)
        memory_percent = memory.percent

        return {
            "cpu": f"CPU: {cpu_usage:.1f}%",
            "mem": f"MEM: {used_memory_gb:.1f}/{total_memory_gb:.1f}GB ({memory_percent:.1f}%)",
        }
    except Exception as e:
        logging.error(f"Failed to fetch system stats: {e}")
        return {"cpu": "CPU: N/A", "mem": "MEM: N/A"}

def update_status_bar(checker, config, status_file_path, stop_event):
    """
    Write a dynamic status bar to a file for tmux to read.
    Rotate between wallet addresses and display system/GPU stats,
    alternating CPU and MEM stats.
    """
    try:
        logging.info("Starting tmux status bar (Press Ctrl+C to stop)")

        # Cycle through addresses
        address_cycle = cycle(checker.addresses)
        show_cpu = True  # Toggle flag for rotating CPU/MEM stats

        while not stop_event.is_set():
            try:
                # Fetch the next address
                current_address = next(address_cycle)
                with checker.lock:
                    balance = checker.last_balances.get(current_address)

                if balance is None:
                    balance = checker.get_balance(current_address)
                    with checker.lock:
                        checker.last_balances[current_address] = balance

                truncated_address = truncate_address(current_address)
                wallet_text = f"{truncated_address}: {balance:.4f} AI3" if balance is not None else "---- AI3"

                # Fetch system stats
                system_stats = fetch_system_stats()
                sys_stat = system_stats["cpu"] if show_cpu else system_stats["mem"]
                show_cpu = not show_cpu  # Toggle flag

                # Determine terminal width
                terminal_width = shutil.get_terminal_size().columns

                # Determine how many GPUs to display
                max_gpus = 2 if terminal_width < 120 else 3
                gpu_stats = fetch_gpu_stats(max_gpus=max_gpus) if config.get("enable_gpu", True) else str()
                gpu_text = " | ".join(gpu_stats) if gpu_stats else str()

                # Combine all stats into a single line
                combined_status = f"{wallet_text} | {sys_stat} | {gpu_text}"

                # Write the combined status to the file
                with open(status_file_path, "w") as status_file:
                    status_file.write(combined_status[:terminal_width] + "\n")  # Truncate if necessary

                # Log the update for debugging
                # logging.info(f"Updated status: {combined_status}")

                # Update every 10 seconds
                time.sleep(config.get("check_interval", 10))
            except Exception as e:
                logging.error(f"Error in status bar loop: {e}")
                time.sleep(10)
    except Exception as e:
        logging.error(f"Error initializing status bar: {e}")

def main():
    """
    Main function to initialize and start the BalanceChecker in the appropriate mode.
    """
    setup_logging()

    # Load and validate configuration
    config = load_config()
    validate_config(config)

    # Extract configuration with defaults
    node_url = config.get("node_url")
    addresses = config.get("addresses", [])
    check_interval = config.get("check_interval", 600)
    notification_config = config.get("notifications", {})
    run_as_tmux = config.get("run_as_tmux", True)

    # Truncate addresses for logging
    truncated_addresses = [truncate_address(address) for address in addresses]

    logging.info("Starting BalanceChecker with the following configuration:")
    logging.info(f"Node URL: {node_url}")
    logging.info(f"Addresses: {', '.join(truncated_addresses)}")
    logging.info(f"Check Interval: {check_interval} seconds")
    # logging.info(f"Run as tmux status bar: {run_as_tmux}")

    # Initialize the BalanceChecker
    checker = BalanceChecker(
        node_url=node_url,
        addresses=addresses,
        check_interval=check_interval,
        notification_config=notification_config,
        run_as_tmux=run_as_tmux,
    )

    if run_as_tmux:
        # Define the path for the status file that tmux will read
        status_file_path = "/tmp/tmux_status.txt"

        # Event to signal threads to stop
        stop_event = threading.Event()

        # Create threads for the status bar and balance monitoring
        status_bar_thread = threading.Thread(target=update_status_bar, args=(checker, config, status_file_path, stop_event))
        monitoring_thread = threading.Thread(target=checker.start_monitoring, args=(stop_event,))

        # Start the threads
        status_bar_thread.start()
        monitoring_thread.start()

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            logging.info("Stopping all threads...")
            stop_event.set()
            status_bar_thread.join()
            monitoring_thread.join()
            logging.info("Exiting BalanceChecker. Goodbye!")
    else:
        try:
            # Create a stop_event for consistency
            stop_event = threading.Event()
            checker.start_monitoring(stop_event)
        except KeyboardInterrupt:
            logging.info("Exiting BalanceChecker. Goodbye!")

if __name__ == "__main__":
    main()
