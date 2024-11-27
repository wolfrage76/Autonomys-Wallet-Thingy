# Wallet Monitor

This script monitors a set of wallets and notifies you of updates to your balance via Discord or Pushbullet. It can also display wallet balances and system statistics in your tmux status bar.

## Features

- **Balance Monitoring**: Keep track of multiple wallet addresses and detect balance changes.
- **Notifications**: Receive alerts via Discord, Pushover, Telegram or Pushbullet when your wallet balances change.
- **System Statistics**: Display CPU, memory usage, and GPU statistics.
- **tmux Integration**: Seamlessly integrate with tmux to display information in the status bar.

## Requirements

- **Python 3.x**
- **Python Packages**:
  - `substrate-interface`
  - `psutil`
  - `pyyaml`
- **Utilities**:
  - `nvidia-smi` (for GPU statistics)
  - `tmux` (optional, for status bar display)
- **Fonts**:
  - Powerline-compatible font (for special symbols in tmux status bar)

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/wallet-monitor.git
cd wallet-monitor
```

### 2. Install Python Dependencies

```bash
pip install substrate-interface psutil pyyaml
```

### 3. Install Powerline Fonts (Optional)

If you plan to use the tmux status bar with decorative symbols:

- **Linux/macOS**:

  ```bash
  git clone https://github.com/powerline/fonts.git --depth=1
  cd fonts
  ./install.sh
  ```

- **Windows**:

  - Download the fonts from the [Powerline Fonts GitHub repository](https://github.com/powerline/fonts).
  - Install the fonts by opening each `.ttf` file and clicking "Install".

### 4. Configure `config.yaml`

Edit the `config.yaml.example` file in the project directory, edit settings then rename to `config.yaml`:

- **`node_url`**: WebSocket URL of the blockchain node.
- **`addresses`**: List of wallet addresses to monitor.
- **`check_interval`**: Time interval (in seconds) between balance checks.
- **`notifications`**: Provide credentials for notification services.

### 5. Configure tmux (Optional)

If you are using tmux and want to display information in the status bar, edit your `~/.tmux.conf` file:

```tmux
# Enable 256 colors
set -g default-terminal "screen-256color"

# Set the status bar update interval
set -g status-interval 10

# Set the status bar style
set -g status-style bg=colour236,fg=white

# Remove default window status to prevent clutter
set -g window-status-format ''
set -g window-status-current-format ''

# Remove session/window titles to prevent ':bash' or ':python' suffixes
set-option -g set-titles off
set-option -g set-titles-string ''

# Disable status-right to avoid conflicts
set -g status-right ''

# Set a large length for the left section
set -g status-left-length 1000

# Define the left side of the status bar with colors and decorators
set -g status-left '#[bg=colour28,fg=white]⚡#[bg=colour28,fg=white] #(cat /tmp/tmux_status.txt) #[fg=colour28,bg=colour236]⚡'

# Align the status-left to the left
set -g status-justify left
```

**Note**: The decorative symbols `⚡` require a Powerline-compatible font to display correctly.

Reload the tmux configuration:

```bash
tmux source-file ~/.tmux.conf
```

### 6. Run the Script

Start the wallet monitor:

```bash
python3 WalletThingy.py
```

If `python` points to Python 3 on your system, you can use:

```bash
python WalletThingy.py
```

### 7. Run in the Background (Optional)

To run the script in the background:

- **Using `screen`**:

  ```bash
  screen -dmS wallet_monitor python3 WalletThingy.py
  ```

- **Using `nohup`**:

  ```bash
  nohup python3 WalletThingy.py &
  ```

- **Using `&`**:

  ```bash
  python3 WalletThingy.py &
  ```

## Usage

- **Monitoring**: The script will monitor the specified wallet addresses and check for balance changes every `check_interval` seconds.
- **Notifications**: You will receive notifications via the configured services when a balance change is detected.
- **tmux Status Bar**: If enabled, the script will update the tmux status bar with wallet balances, CPU/memory usage, and GPU statistics.

## Example tmux Status Bar Output

```
 sue1...uPFY: 123.45678901 AI3 | CPU: 24.7% | GPU0: NVIDIA Ge... 1.42/8.00GB 45°C 11% 
```

- **Wallet Balance**: Displays the truncated wallet address and current balance.
- **System Stats**: Alternates between CPU and memory usage.
- **GPU Stats**: Shows GPU memory usage, temperature, and utilization.

## Acknowledgements

- **Me**: Special thanks to myself for being awesome

## Troubleshooting

- **Python Version**: Ensure you are using Python 3.x.
- **Dependencies**: Make sure all Python dependencies are installed.
- **`nvidia-smi` Errors**: If you encounter errors with `nvidia-smi`, ensure NVIDIA drivers are properly installed.
- **tmux Issues**: If the status bar does not display correctly, verify your `~/.tmux.conf` settings and reload the configuration.
- **Font Display**: If decorative symbols do not appear correctly, make sure you have a Powerline-compatible font installed and set in your terminal emulator.