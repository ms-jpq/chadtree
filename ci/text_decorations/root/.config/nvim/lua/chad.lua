local export_icons = function()
  return {
    ext_exact = vim.g.WebDevIconsUnicodeDecorateFileNodesExtensionSymbols,
    name_exact = vim.g.WebDevIconsUnicodeDecorateFileNodesExactSymbols,
    name_glob = vim.g.WebDevIconsUnicodeDecorateFileNodesPatternSymbols,
    default_icon = vim.g.WebDevIconsUnicodeDecorateFileNodesDefaultSymbol,
    folder = {
      open = vim.g.DevIconsDefaultFolderOpenSymbol,
      closed = vim.g.WebDevIconsUnicodeDecorateFolderNodesDefaultSymbol
    }
  }
end

local export_colours = function()
  return {
    ext_exact = vim.g.NERDTreeExtensionHighlightColor,
    name_exact = vim.g.NERDTreeExactMatchHighlightColor,
    name_glob = vim.g.NERDTreePatternMatchHighlightColor
  }
end

local load_rtp = function(src)
  vim.o.runtimepath = vim.o.runtimepath .. "," .. "/root/" .. src
end

local load_viml = function(src)
  vim.api.nvim_command("source " .. "/root/" .. src)
end

load_viml "vim-devicons/plugin/webdevicons.vim"
local devicons = export_icons()

load_viml "vim-emoji-icon-theme/plugin/vim-emoji-icon-theme.vim"
local emoji = export_icons()

load_viml "vim-nerdtree-syntax-highlight/after/syntax/nerdtree.vim"
local nerdtree_syntax = export_colours()

local exports = {
  devicons = devicons,
  emoji = emoji,
  nerdtree_syntax = nerdtree_syntax
}
local json = vim.fn.json_encode(exports)

vim.fn.writefile({json}, "exports.json")

os.exit(0)
