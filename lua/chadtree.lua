chad = chad or {}
local linesep = "\n"

if chad.loaded then
  return
else
  chad.loaded = true
  local job_id = nil
  local chad_params = {}
  local err_exit = false

  local on_exit = function(_, code)
    local msg = " | CHADTree EXITED - " .. code
    if code ~= 0 then
      err_exit = true
      vim.api.nvim_err_writeln(msg)
    end
    job_id = nil
    for _, param in ipairs(chad_params) do
      chad[chad_params] = nil
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
      {...}
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

  chad.deps_cmd = function()
    start("deps")
  end

  vim.api.nvim_command [[command! -nargs=0 CHADdeps lua chad.deps_cmd()]]

  local set_chad_call = function(name, cmd)
    table.insert(chad_params, name)
    chad[name] = function(...)
      local args = {...}

      if not job_id then
        job_id = start("run", "--socket", vim.fn.serverstart())
      end

      if not err_exit and _G[cmd] then
        _G[cmd](args)
      else
        vim.defer_fn(
          function()
            if err_exit then
              return
            else
              chad[name](unpack(args))
            end
          end,
          POLLING_RATE
        )
      end
    end
  end

  set_chad_call("open_cmd", "CHADopen")
  vim.api.nvim_command [[command! -nargs=* CHADopen lua chad.open_cmd(<f-args>)]]

  set_chad_call("help_cmd", "CHADhelp")
  vim.api.nvim_command [[command! -nargs=* CHADhelp lua chad.help_cmd(<f-args>)]]
end
