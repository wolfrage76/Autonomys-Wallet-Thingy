from modules.AutonomysWallet import BalanceChecker

# Configuration
NODE_URL = "ws://192.168.1.208:9944" # Thew node and port to connect to
ADDRESSES = [
    "xxxxxxxxxxxxxxx", # Add additional addresses seperated by commas
]

CHECK_INTERVAL = 600 # seconds
DISCORD_WEBHOOK = False # '' 
# False, or put your Webhook in quotes: 'https://discord.com/api/webhooks/XXXXXX/YYYYYYYYYYYYYYYYYY'


PUSHBULLET_TOKEN = False # False, or put your token in quotes: 'your_pushbullet_access_token'

if __name__ == "__main__":
    checker = BalanceChecker(
        node_url=NODE_URL,
        addresses=ADDRESSES,
        check_interval=CHECK_INTERVAL,
        discord_webhook=DISCORD_WEBHOOK,
        pushbullet_token=PUSHBULLET_TOKEN
    )
    checker.start_monitoring()
