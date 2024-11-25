from AutonomysWallet import BalanceChecker

# Configuration
NODE_URL = "ws://192.168.1.208:9944"
ADDRESSES = [
    "sue1dbNHjokfnRG9Uqqd34C3VVDBZ5kyraHREAqzyvzsxuPFY", # Add additional addresses seperated by commas
]

CHECK_INTERVAL = 300  # seconds

DISCORD_WEBHOOK = 'https://discord.com/api/webhooks/1310714764091064463/CUjDNhjVqY4lSP0-9d9o6W3px_Oou_wLuyCdMfvN-PFYj3DN5mAJBUXncCe6V-e13Q_o' # " False, or put your Webhook in quotes: 'https://discord.com/api/webhooks/XXXXXX/YYYYYYYYYYYYYYYYYY"'

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
