local on_exit = function (_, code)
  vim.api.nvim_err_writeln("CHADTree EXITED - " .. code)
end

local on_stdout = function (_, msg)
  vim.api.nvim_out_write(table.concat(msg, "\n"))
end

local on_stderr = function (_, msg)
  vim.api.nvim_err_write(table.concat(msg, "\n"))
end


local py_main = function ()
  local filepath = "/lua/chadtree.lua"
  local src = debug.getinfo(1).source
  local top_lv = string.sub(src, 2, #src - #filepath)

  local unix = top_lv .. [[/main.py]]
  local windows = top_lv .. [[\main.py]]
  return vim.fn.filereadable(unix) and unix or windows
end


local start = function ()
  local main = py_main()
  local args = { "python3", main, vim.fn.serverstart() }
  local job_id = vim.fn.jobstart(args, { on_exit = on_exit, on_stdout = on_stdout, on_stderr = on_stderr })
  return job_id
end


local POLLING_RATE = 10
local job_id = nil
local open_cmd = "CHADopen"


chad_open_cmd = function (...)
  local args = {...}

  if not job_id then
    job_id = start()
  end

  if _G[open_cmd] then
    _G[open_cmd](args)
  else
    vim.defer_fn(function ()
      chad_open_cmd(unpack(args))
    end, POLLING_RATE)
  end
end


vim.api.nvim_command[[command! -nargs=* CHADopen lua chad_open_cmd(<f-args>)]]