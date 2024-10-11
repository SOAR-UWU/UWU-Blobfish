#!/usr/bin/env bash
# Taken from https://github.com/SOAR-UWU/Live-ISO-ROS2/blob/main/scripts/customizeLive.sh

set -eo pipefail

sudo apt install -y \
  vim tmux htop ripgrep

# Install fzf from git to get the latest version.
wget -qO- https://github.com/junegunn/fzf/releases/download/v0.55.0/fzf-0.55.0-linux_amd64.tar.gz \
  | tar -xzf - --to-stdout fzf \
  | sudo tee /usr/local/bin/fzf > /dev/null
sudo chmod +x /usr/local/bin/fzf
echo 'eval "$(fzf --bash)"' | sudo tee -a /etc/bash.bashrc > /dev/null

# Add my ripgrep config.
sudo wget -qO /etc/ripgreprc https://raw.githubusercontent.com/Interpause/dotfiles/1b29427/.ripgreprc
echo "export RIPGREP_CONFIG_PATH=/etc/ripgreprc" | sudo tee -a /etc/bash.bashrc > /dev/null

# Make less better to use.
echo "export LESS='-FiJMRW -x4 -z-4 -#5 --use-color'" | sudo tee -a /etc/bash.bashrc > /dev/null

# Configure tmux.
echo 'unbind C-b
set -g prefix C-a
set -g mouse on' | sudo tee -a /etc/tmux.conf > /dev/null

# Configure vim a bit.
echo 'set shiftwidth=4 smarttab
set tabstop=4 softtabstop=0
set mouse=a
set smartcase ignorecase
set formatoptions-=t
' | sudo tee -a /etc/vim/vimrc.local > /dev/null

# Enable ctrl+bksp and ctrl+del.
echo '"\e[3;5~": kill-word' | sudo tee -a /etc/inputrc > /dev/null
echo '"\C-H": backward-kill-word' | sudo tee -a /etc/inputrc > /dev/null

# Wget enable content disposition.
echo "content_disposition = on" | sudo tee -a /etc/wgetrc > /dev/null
