# shellcheck shell=bash
# Modern .zshrc configuration
# Migrated from Ansible mac-setup
# This file is sourced by zsh, not executed directly

# Path configuration for GNU tools (prefer GNU over macOS)
export PATH="/opt/homebrew/opt/libtool/libexec/gnubin:$PATH"
export PATH="/opt/homebrew/opt/coreutils/libexec/gnubin:$PATH"
export PATH="/opt/homebrew/opt/gnu-tar/libexec/gnubin:$PATH"
export PATH="/opt/homebrew/opt/grep/libexec/gnubin:$PATH"
export PATH="/opt/homebrew/opt/gnu-sed/libexec/gnubin:$PATH"
export PATH="/opt/homebrew/opt/gsed/libexec/gnubin:$PATH"
export PATH="/opt/homebrew/opt/gawk/libexec/gnubin:$PATH"
export PATH="/opt/homebrew/opt/make/libexec/gnubin:$PATH"
export PATH="/opt/homebrew/opt/gnu-which/libexec/gnubin:$PATH"

# mise - Modern tool version manager
eval "$(mise activate zsh)"

# Oh My Zsh installation
export ZSH="$HOME/.oh-my-zsh"

# Powerlevel10k theme
# To configure: p10k configure
export ZSH_THEME="powerlevel10k/powerlevel10k"

# Oh My Zsh plugins
export plugins=(
  git
  kubectl
  kubectx
  kube-ps1
  pip
  sudo
  terraform
  vscode
  vi-mode
  web-search
  command-not-found
  zsh-syntax-highlighting
  zsh-autosuggestions
  zsh-completions
)

# shellcheck source=/dev/null
source "$ZSH/oh-my-zsh.sh"

# User configuration

# Preferred editor (using neovim)
export EDITOR='nvim'
export VISUAL='nvim'

# Aliases
alias ls="lsd --color=always --sort=extension"
alias cat="bat --paging=never"

# Neovim aliases (vim -> nvim)
alias vim='nvim'
alias vi='nvim'
alias v='nvim'

# thefuck - Command correction
eval "$(thefuck --alias)"

# dircolors
if [ -f "$HOME/.dircolors" ]; then
  eval "$(gdircolors -b $HOME/.dircolors)"
fi

# FZF - Fuzzy finder
# shellcheck source=/dev/null
[ -f ~/.fzf.zsh ] && source ~/.fzf.zsh

# GRC - Generic Colouriser (colorize command output)
# shellcheck source=/dev/null
[ -f /opt/homebrew/etc/grc.zsh ] && source /opt/homebrew/etc/grc.zsh

# Powerlevel10k instant prompt
# Should stay close to the top of ~/.zshrc
# shellcheck disable=SC1090
if [[ -r "${XDG_CACHE_HOME:-$HOME/.cache}/p10k-instant-prompt-$(whoami).zsh" ]]; then
  source "${XDG_CACHE_HOME:-$HOME/.cache}/p10k-instant-prompt-$(whoami).zsh"
fi

# To customize prompt, run `p10k configure` or edit ~/.p10k.zsh
# shellcheck source=/dev/null
[[ ! -f ~/.p10k.zsh ]] || source ~/.p10k.zsh
