# Ghostty Terminal Configuration

Custom configuration for Ghostty - a modern, GPU-accelerated terminal emulator.

## Features

### 🎨 **Color Scheme: Catppuccin Mocha**
- Modern, eye-friendly color scheme
- Popular in developer communities
- Excellent contrast for code readability
- 16-color palette + extended colors

### 🔤 **Font: MesloLGS Nerd Font Mono**
- Compatible with Powerlevel10k
- Icon support (Nerd Font glyphs)
- Size: 13pt (adjustable)
- Optional ligatures (disabled by default for clearer code)

### 🖼️ **Window Appearance**
- Background opacity: 95% (semi-transparent)
- Background blur: 20px radius (macOS)
- Padding: 8px horizontal and vertical
- Size: 120 columns × 35 rows

### ⚡ **Performance**
- GPU-accelerated rendering (auto-detected)
- Hardware acceleration on macOS (Metal) and Linux (OpenGL)
- Scrollback: 10,000 lines
- Optimized for smooth performance

### 🖱️ **Mouse & Selection**
- Copy on select (automatic clipboard)
- URL detection and click-to-open
- Word selection on click

### ⌨️ **Keyboard**
- macOS: Option key as Alt (for terminal shortcuts)
- Custom keybindings ready (commented in config)
- Shell integration enabled (cursor, sudo, title)

### 📐 **Cross-Platform**
- Configuration location: `~/.config/ghostty/config`
- Same config works on macOS and Linux
- Platform-specific optimizations auto-detected

## Installation

The configuration is automatically deployed by Ansible:

```bash
# Deploy Ghostty config
ansible-playbook setup.yml --tags ghostty

# Or run full setup
ansible-playbook -i inventory.yml setup.yml
```

**Manual installation:**
```bash
# Create directory
mkdir -p ~/.config/ghostty

# Copy configuration
cp dotfiles/ghostty/config ~/.config/ghostty/config

# Restart Ghostty to apply
```

## Customization

Edit `dotfiles/ghostty/config` to customize:

### Change Font Size
```
font-size = 14  # Increase from 13 to 14
```

### Change Color Scheme
Replace the palette section with another theme:
- **Tokyo Night**
- **Nord**
- **Dracula**
- **Gruvbox**
- **Solarized**

### Enable Ligatures
```
font-feature = +calt  # Enable ligatures for coding fonts
```

### Adjust Transparency
```
background-opacity = 1.0  # Fully opaque
background-opacity = 0.85  # More transparent
```

### Disable Background Blur (for performance)
```
# background-blur-radius = 20  # Comment out to disable
```

### Custom Keybindings
Uncomment and modify keybind lines in config:
```
keybind = cmd+t=new_tab
keybind = cmd+d=new_split:right
```

## Color Schemes

### Current: Catppuccin Mocha
Warm, modern theme with excellent readability.

### Alternative Themes

**To switch themes**, replace the `palette =` lines with one of these:

**Tokyo Night:**
```
background = #1a1b26
foreground = #c0caf5
# ... (add remaining colors)
```

**Nord:**
```
background = #2e3440
foreground = #d8dee9
# ... (add remaining colors)
```

**Dracula:**
```
background = #282a36
foreground = #f8f8f2
# ... (add remaining colors)
```

## Fonts

### Current: MesloLGS Nerd Font

**Alternative Nerd Fonts** (already installed via Brewfile):
```
font-family = "JetBrains Mono Nerd Font"
font-family = "Fira Code Nerd Font"
font-family = "Hack Nerd Font"
```

To install more fonts:
```bash
brew search nerd-font
brew install --cask font-<name>-nerd-font
```

## Testing

### Verify Colors
```bash
msgcat --color=test
```

### Verify Font Glyphs (Nerd Font icons)
```bash
echo -e "\ue0b0 \u00b1 \ue0a0 \u27a6 \u2718 \u26a1 \u2699"
```

### Verify GPU Acceleration
Check Ghostty's debug menu or logs for GPU renderer info.

## Troubleshooting

### Config Not Loading
1. Verify file location: `~/.config/ghostty/config`
2. Check file permissions: `chmod 644 ~/.config/ghostty/config`
3. Restart Ghostty completely (Cmd+Q, not just close window)

### Font Not Found
1. Verify font installed: `brew list --cask | grep nerd-font`
2. Install if missing: `brew install --cask font-meslo-lg-nerd-font`
3. Restart Ghostty after installing fonts

### Performance Issues
1. Disable background blur: comment out `background-blur-radius`
2. Set opacity to 1.0: `background-opacity = 1.0`
3. Reduce scrollback: `scrollback-limit = 5000`

### Colors Look Wrong
1. Check terminal reports true color: `echo $COLORTERM` (should be `truecolor`)
2. Verify shell profile doesn't override colors
3. Try a different color scheme

## Documentation

- **Ghostty Official Docs**: https://ghostty.org/docs
- **Catppuccin Theme**: https://github.com/catppuccin/catppuccin
- **Nerd Fonts**: https://www.nerdfonts.com/

## Tips

1. **Powerlevel10k Integration**: Works out of the box with MesloLGS NF
2. **Tmux**: Fully compatible, no special configuration needed
3. **SSH**: Colors and fonts work seamlessly over SSH
4. **Copy/Paste**: Cmd+C/V on macOS, Ctrl+Shift+C/V on Linux
5. **Splits**: Use tmux for terminal multiplexing (Cmd+D for horizontal split)

## Ansible Integration

This config is deployed via Ansible playbook:

**Tags:**
- `ghostty` - Deploy only Ghostty configuration
- `shell` - Includes Ghostty with shell tools

**Feature Flag:**
- Controlled by: `install_shell_tools` in `group_vars/all.yml`

**Backup:**
- Existing config is backed up automatically before deployment
- Backup location: `~/.config/ghostty/config.backup`

---

**Last Updated**: 2025-10-27
**Ghostty Config Version**: 1.0
