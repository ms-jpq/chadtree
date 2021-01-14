local linesep = "\n"

local on_exit = function(_, code)
  local msg = " | CHADTree EXITED - " .. code
  if code ~= 0 then
    vim.api.nvim_err_writeln(msg)
  end
end

local on_stdout = function(_, msg)
  vim.api.nvim_out_write(table.concat(msg, linesep))
end

local on_stderr = function(_, msg)
  vim.api.nvim_err_write(table.concat(msg, linesep))
end

local top_lv = function()
  local filepath = "/lua/chadtree.lua"
  local src = debug.getinfo(1).source
  local top_lv = string.sub(src, 2, #src - #filepath)
  return top_lv
end

local start = function(...)
  local cwd = top_lv()
  local args =
    vim.tbl_flatten {
    {"python3", "-m", "chadtree"},
    {...},
    {"--socket", vim.fn.serverstart()}
  }
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

chad = chad or {}

chad.deps_cmd = function()
  start("deps")
end

vim.api.nvim_command [[command! -nargs=0 CHADdeps lua chad.deps_cmd()]]

local set_chad_call = function(name, cmd)
  chad[name] = function(...)
    local args = {...}

    if not job_id then
      job_id = start("run")
    end

    if _G[cmd] then
      _G[cmd](args)
    else
      vim.defer_fn(
        function()
          chad[name](unpack(args))
        end,
        POLLING_RATE
      )
    end
  end
end

set_chad_call("open_cmd", "CHADopen")
vim.api.nvim_command [[command! -nargs=* CHADopen lua chad.open_cmd(<f-args>)]]

set_chad_call("help_cmd", "CHADhelp")
vim.api.nvim_command [[command! -nargs=0 CHADhelp lua chad.help_cmd(<f-args>)]]
