This will monitor a set of wallets and notify you of updates to your balance via Discord or Pushbullet.

1: Edit WalletThingy.py

2: Configure as needed

3: If using tmux:
    edit '~/.tmux.conf' and add in:
    '''
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
set -g status-left '#[bg=colour28,fg=white]#[bg=colour28,fg=white] #(cat /tmp/tmux_status.txt) #[fg=colour28,bg=colour236]'

# Align the status-left to the left
set -g status-justify left

    '''

4: Run 'tmux source-file ~/.tmux.conf' if using tmux

5: Run 'python WalletThingy.py' (Or might be 'python3 WalletThingy.py')

6: Thank Wolfrage in the Autonomys discord channel.

Optional on Linux, Run it in the background with screen:
'screen -dmS wallet python WalletThingy.py' or 'python WalletThingy.py &'