(function(_)
  if vim.diagnostic then
    local diagnostics = vim.diagnostic.get(nil, nil)
    vim.validate({diagnostics = {diagnostics, "table"}})
    local acc = {}
    for _, row in pairs(diagnostics) do
      local buf = row.bufnr
      local severity = tostring(row.severity)
      vim.validate(
        {
          buf = {buf, "number"},
          row_severity = {row.severity, "number"}
        }
      )
      if not acc[buf] then
        acc[buf] = {}
      end
      if not acc[buf][severity] then
        acc[buf][severity] = 0
      end
      acc[buf][severity] = acc[buf][severity] + 1
    end
    local acc2 = {}
    for buf, warnings in pairs(acc) do
      local path = vim.api.nvim_buf_get_name(buf)
      acc2[path] = warnings
    end
    return acc2
  end
end)(...)
