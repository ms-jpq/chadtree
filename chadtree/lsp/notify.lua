(function (method, params)
  if vim.lsp then
    local clients = vim.lsp.get_active_clients()
    for _, client in ipairs(clients) do
      client.notify(method, params)
    end
  end
end)(...)

