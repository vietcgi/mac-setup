-- Neovim Options

local opt = vim.opt

-- Line numbers
opt.number = true
opt.relativenumber = true

-- Tabs & indentation
opt.tabstop = 2
opt.shiftwidth = 2
opt.softtabstop = 2
opt.expandtab = true
opt.autoindent = true
opt.smartindent = true

-- Line wrapping
opt.wrap = false

-- Search settings
opt.ignorecase = true
opt.smartcase = true
opt.hlsearch = true
opt.incsearch = true

-- Appearance
opt.termguicolors = true
opt.background = "dark"
opt.signcolumn = "yes"
opt.cursorline = true

-- Backspace
opt.backspace = "indent,eol,start"

-- Clipboard
opt.clipboard:append("unnamedplus")

-- Split windows
opt.splitright = true
opt.splitbelow = true

-- Statusline
opt.laststatus = 3  -- Global statusline

-- Completion
opt.completeopt = "menu,menuone,noselect"

-- Undo & backup
opt.undofile = true
opt.backup = false
opt.swapfile = false

-- Update time
opt.updatetime = 250
opt.timeoutlen = 300

-- Mouse
opt.mouse = "a"

-- Scrolloff
opt.scrolloff = 8
opt.sidescrolloff = 8

-- Performance
opt.lazyredraw = false
