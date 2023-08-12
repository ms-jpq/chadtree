(function(args)
  local method, params = unpack(args)
  if vim.lsp then
    local clients = vim.lsp.get_active_clients()
    for _, client in pairs(clients) do
      client.notify(method, params)
    end
  end
end)(...)
