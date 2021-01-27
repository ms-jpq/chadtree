return function(args)
  local cwd = unpack(args)

  local uv = vim.loop
  local on_exit = function(code)
    vim.schedule(
      function()
        vim.api.nvim_err_writeln(" | EXITED - " .. code)
      end
    )
  end
  local on_stdout = function(data)
    vim.schedule(
      function()
        vim.api.nvim_out_write(data)
      end
    )
  end
  local on_stderr = function(data)
    vim.schedule(
      function()
        vim.api.nvim_err_write(data)
      end
    )
  end
  local spawn = function(prog, args, input, cwd, env, handlers)
    local _env = {}
    for key, val in pairs(vim.api.nvim_call_function("environ", {})) do
      table.insert(_env, key .. "=" .. val)
    end
    for key, val in pairs(env) do
      table.insert(_env, key .. "=" .. val)
    end
    local stdin = uv.new_pipe(false)
    local stdout = uv.new_pipe(false)
    local stderr = uv.new_pipe(false)
    local opts = {
      stdio = {stdin, stdout, stderr},
      args = args,
      cwd = cwd,
      env = _env
    }

    local process, pid = nil, nil
    process, pid =
      uv.spawn(
      prog,
      opts,
      function(code, signal)
        local handles = {stdin, stdout, stderr, process}
        for _, handle in ipairs(handles) do
          uv.close(handle)
        end
        (handlers.on_exit or on_exit)(code)
      end
    )
    assert(process, pid)

    uv.read_start(
      stdout,
      function(err, data)
        assert(not err, err)
        if data then
          (handlers.on_stdout or on_stdout)(data)
        end
      end
    )

    uv.read_start(
      stderr,
      function(err, data)
        assert(not err, err)
        if data then
          (handlers.on_stderr or on_stderr)(data)
        end
      end
    )

    if input then
      uv.write(
        stdin,
        input,
        function(err)
          assert(not err, err)
          uv.shutdown(
            stdin,
            function(err)
              assert(not err, err)
            end
          )
        end
      )
    end

    return pid
  end


  local function defer(timeout, callback)
    local timer = uv.new_timer()
    uv.timer_start(
      timer,
      timeout,
      0,
      function()
        uv.timer_stop(timer)
        uv.close(timer)
        vim.schedule(callback)
      end
    )
  end

  --
  --
  -- DOMAIN CODE
  --
  --

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

    local handlers = {
      on_exit = function(code)
        vim.schedule(function ()
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
        end)
      end
    }

    local start = function(...)
      local go, _py3 = pcall(vim.api.nvim_get_var, "python3_host_prog")
      local py3 = go and _py3 or "python3"
      local go, _settings = pcall(vim.api.nvim_get_var, "chadtree_settings")
      local settings = go and _settings or {}

      local args =
        vim.tbl_flatten {
        {py3, "-m", "chadtree"},
        {...},
        (settings.xdg and {"--xdg"} or {})
      }

      local job_id = spawn("./venv.sh", args, nil, cwd, {}, handlers)
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
          local jid = start("run", "--socket", server)
          if jid == -1 then
            vim.api.nvim_err_writeln("Error! - Invalid job!")
          elseif jid == 0 then
            vim.api.nvim_err_writeln("Error! - Not executable!")
          else
            job_id = jid
          end
        end

        if not job_id then
          return
        elseif not err_exit and _G[cmd] then
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
