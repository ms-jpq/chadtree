(function(args)
  local wc = vim.api.nvim_win_call
  if wc then
    local win = unpack(args)
    return wc(
      win,
      function()
        return vim.fn.winline()
      end
    )
  else
    return vim.NIL
  end
end)(...)
