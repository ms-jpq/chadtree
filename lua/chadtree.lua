return function(args)
  local sfile = unpack(args)
  local filepath = "/plugin/chadtree.vim"
  local top_lv = string.sub(sfile, 2, #sfile - #filepath)

  chad = chad or {}
  local linesep = "\n"
  local POLLING_RATE = 10

  if chad.loaded then
    return
  else
    chad.loaded = true
    local job_id = nil
    local chad_params = {}
    local err_exit = false

    local go, _py3 = pcall(vim.api.nvim_get_var, "python3_host_prog")
    local py3 = go and _py3 or "python3"
    local go, _settings = pcall(vim.api.nvim_get_var, "chadtree_settings")
    local settings = _settings or {}

    local function defer(timeout, callback)
      local timer = vim.loop.new_timer()
      timer:start(
        timeout,
        0,
        function()
          timer:stop()
          timer:close()
          vim.schedule(callback)
        end
      )
      return timer
    end

    chad.on_exit = function(args)
      local code = unpack(args)
      local msg = " | CHADTree EXITED - " .. code
      if not (code == 0 or code == 143) then
        err_exit = true
        vim.api.nvim_err_writeln(msg)
      else
        err_exit = false
      end
      job_id = nil
      for _, param in ipairs(chad_params) do
        chad[chad_params] = nil
      end
    end

    chad.on_stdout = function(args)
      local msg = unpack(args)
      vim.api.nvim_out_write(table.concat(msg, linesep))
    end

    chad.on_stderr = function(args)
      local msg = unpack(args)
      vim.api.nvim_err_write(table.concat(msg, linesep))
    end

    local start = function(...)
      local cwd = "/" .. top_lv
      local args =
        vim.tbl_flatten {
        {"python3", "-m", "chadtree"},
        {...},
        (settings.xdg and {"--xdg"} or {})
      }
      local params = {
        cwd = cwd,
        on_exit = "CHADon_exit",
        on_stdout = "CHADon_stdout",
        on_stderr = "CHADon_stderr"
      }
      local job_id = vim.api.nvim_call_function("jobstart", {args, params})
      return job_id
    end

    chad.deps_cmd = function()
      start("deps")
    end

    vim.api.nvim_command [[command! -nargs=0 CHADdeps lua chad.deps_cmd()]]

    local set_chad_call = function(name, cmd)
      table.insert(chad_params, name)
      chad[name] = function(...)
        local args = {...}

        if not job_id then
          local server = vim.api.nvim_call_function("serverstart", {})
          job_id = start("run", "--socket", server)
        end

        if not err_exit and _G[cmd] then
          _G[cmd](args)
        else
          defer(
            POLLING_RATE,
            function()
              if err_exit then
                return
              else
                chad[name](unpack(args))
              end
            end
          )
        end
      end
    end

    set_chad_call("open_cmd", "CHADopen")
    vim.api.nvim_command [[command! -nargs=* CHADopen lua chad.open_cmd(<f-args>)]]

    set_chad_call("help_cmd", "CHADhelp")
    vim.api.nvim_command [[command! -nargs=* CHADhelp lua chad.help_cmd(<f-args>)]]
  end
end
