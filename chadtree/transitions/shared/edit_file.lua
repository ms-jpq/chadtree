(function(buf, path)
  local escaped = vim.fn.fnameescape(path)
  vim.api.nvim_buf_call(
    buf,
    function()
      vim.cmd("edit " .. escaped)
    end
  )
end)(...)
