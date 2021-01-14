local on_exit = function(_, code)
  vim.api.nvim_err_writeln(" | CHADTree EXITED - " .. code)
end

local on_stdout = function(_, msg)
  vim.api.nvim_out_write(table.concat(msg, "\n"))
end

local on_stderr = function(_, msg)
  vim.api.nvim_err_write(table.concat(msg, "\n"))
end

local top_lv = function()
  local linesp = 1 and "/" or "\\"
  local filepath = "/lua/chadtree.lua"
  local src = debug.getinfo(1).source
  local top_lv = string.sub(src, 2, #src - #filepath)
  return top_lv
end

local start = function()
  local cwd = top_lv()
  local args = {"python3", "-m", "chadtree", vim.fn.serverstart()}
  local params = {
    cwd = cwd,
    on_exit = on_exit,
    on_stdout = on_stdout,
    on_stderr = on_stderr
  }
  local job_id = vim.fn.jobstart(args, params)
  return job_id
end

local POLLING_RATE = 10
local job_id = nil
local open_cmd = "CHADopen"

chad_open_cmd = function(...)
  local args = {...}

  if not job_id then
    job_id = start()
  end

  if _G[open_cmd] then
    _G[open_cmd](args)
  else
    vim.defer_fn(
      function()
        chad_open_cmd(unpack(args))
      end,
      POLLING_RATE
    )
  end
end

vim.api.nvim_command [[command! -nargs=* CHADopen lua chad_open_cmd(<f-args>)]]
