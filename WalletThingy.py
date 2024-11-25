from AutonomysWallet import BalanceChecker

# Configuration
NODE_URL = "ws://yournodeIP:NodePort"
ADDRESSES = [
    "xxxxxxxxxxxxxxxxxxx", # Add additional addresses seperated by commas
]

CHECK_INTERVAL = 60  # seconds

USE_DISCORD = True
DISCORD_WEBHOOK = False # " False, or put your Webhook in quotes: 'https://discord.com/api/webhooks/XXXXXX/YYYYYYYYYYYYYYYYYY"

USE_PUSHBULLET = False
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
