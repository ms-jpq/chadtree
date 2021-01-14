local export = function(export_name)
  local default_sym = vim.g.WebDevIconsUnicodeDecorateFileNodesDefaultSymbol
  local folder_open = vim.g.DevIconsDefaultFolderOpenSymbol
  local folder_close = vim.g.WebDevIconsUnicodeDecorateFolderNodesDefaultSymbol

  local extensions = vim.g.WebDevIconsUnicodeDecorateFileNodesExtensionSymbols
  local exact = vim.g.WebDevIconsUnicodeDecorateFileNodesExactSymbols
  local glob = vim.g.WebDevIconsUnicodeDecorateFileNodesPatternSymbols

  local data = {
    extensions = extensions,
    exact = exact,
    glob = glob,
    default = default_sym,
    folder = {
      open = folder_open,
      closed = folder_close
    }
  }
  local json = vim.fn.json_encode(data)
  vim.fn.writefile({json}, export_name)
end

local load_rtp = function(src)
  for _, s in ipairs(src) do
    vim.o.runtimepath = vim.o.runtimepath .. "," .. "/root/" .. s
  end
end

local load_viml = function(src)
  for _, s in ipairs(src) do
    vim.api.nvim_command("source /root/" .. s)
  end
end

local init = function()
  local v1 = {
    "vim-devicons/plugin/webdevicons.vim"
  }
  local rtp2 = {
    "lsp-status.nvim"
  }
  local v2 = {
    "vim-emoji-icon-theme/plugin/vim-emoji-icon-theme.vim"
  }

  load_viml(v1)
  export("unicode_icons.json")

  load_rtp(rtp2)
  load_viml(v2)
  export("emoji_icons.json")

  os.exit(0)
end

return {
  init = init
}
