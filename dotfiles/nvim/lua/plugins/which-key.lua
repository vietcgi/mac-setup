-- Which-key (shows available keybindings) - Updated for v3.0.0+

return {
  "folke/which-key.nvim",
  event = "VeryLazy",
  init = function()
    vim.o.timeout = true
    vim.o.timeoutlen = 500
  end,
  opts = {
    -- your configuration comes here
    -- or leave it empty to use the default settings
    -- refer to the configuration section below
  },
  config = function()
    local wk = require("which-key")
    wk.setup({})

    -- Register key groups using the new v3 API
    wk.add({
      { "<leader>f", group = "Find" },
      { "<leader>e", group = "Explorer" },
      { "<leader>s", group = "Split" },
      { "<leader>h", group = "Git Hunk" },
      { "<leader>t", group = "Toggle" },
      { "<leader>c", group = "Code" },
      { "<leader>r", group = "Rename/Restart" },
      { "<leader>d", group = "Diagnostics" },
      { "<leader>D", group = "Buffer Diagnostics" },
    })
  end,
}
