local init = function ()

  local extensions = vim.g.WebDevIconsUnicodeDecorateFileNodesExtensionSymbols
  local exact      = vim.g.WebDevIconsUnicodeDecorateFileNodesExactSymbols
  local glob       = vim.g.WebDevIconsUnicodeDecorateFileNodesPatternSymbols

  local data = {
    extensions = extensions,
    exact      = exact,
    glob       = glob,
  }
  local json = vim.fn.json_encode(data)
  vim.fn.writefile({json}, "icons.json")
  os.exit(0)

end


return {
  init = init
}
