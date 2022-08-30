CHAD = CHAD or {}
chad = chad or {}

local linesep = "\n"
local POLLING_RATE = 10
local is_win = vim.api.nvim_call_function("has", {"win32"}) == 1

local cwd = (function()
  local source = debug.getinfo(2, "S").source
  local file = string.match(source, "^@(.*)")
  return vim.api.nvim_call_function("fnamemodify", {file, ":p:h:h"})
end)()

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

local settings = function()
  local go, _settings = pcall(vim.api.nvim_get_var, "chadtree_settings")
  local settings = go and _settings or {}
  return settings
end

local job_id = nil
local err_exit = false

chad.on_exit = function(args)
  local code = unpack(args)
  if not (code == 0 or code == 143) then
    err_exit = true
    vim.api.nvim_err_writeln("CHADTree EXITED - " .. code)
  else
    err_exit = false
  end
  job_id = nil
end

chad.on_stdout = function(args)
  local msg = unpack(args)
  vim.api.nvim_out_write(table.concat(msg, linesep))
end

chad.on_stderr = function(args)
  local msg = unpack(args)
  if vim.api.nvim_call_function("has", {"nvim-0.5"}) == 1 then
    vim.api.nvim_echo({{table.concat(msg, linesep), "ErrorMsg"}}, true, {})
  else
    vim.api.nvim_err_write(table.concat(msg, linesep))
  end
end

local go, _py3 = pcall(vim.api.nvim_get_var, "python3_host_prog")
local py3 = go and _py3 or (is_win and "python" or "python3")
local xdg_dir = vim.api.nvim_call_function("stdpath", {"data"})

local main = function(is_xdg)
  local v_py =
    cwd ..
    (is_win and [[/.vars/runtime/Scripts/python.exe]] or
      "/.vars/runtime/bin/python3")

  if is_win then
    local v_py_xdg = xdg_dir .. "/chadrt/Scripts/python"
    local v_py = is_xdg and v_py_xdg or v_py
    if vim.api.nvim_call_function("filereadable", {v_py}) == 1 then
      return {v_py}
    else
      local win_proxy = cwd .. [[/win.cmd]]
      return {win_proxy, py3}
    end
  else
    local v_py_xdg = xdg_dir .. "/chadrt/bin/python3"
    local v_py = is_xdg and v_py_xdg or v_py
    if vim.api.nvim_call_function("filereadable", {v_py}) == 1 then
      return {v_py}
    else
      return {py3}
    end
  end
end

local start = function(deps, ...)
  local is_xdg = settings().xdg
  local args =
    vim.tbl_flatten {
    deps and py3 or main(is_xdg),
    {"-m", "chadtree"},
    {...},
    (is_xdg and {"--xdg", xdg_dir} or {})
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

chad.Deps = function()
  start(true, "deps", "--nvim")
end

vim.api.nvim_command [[command! -nargs=0 CHADdeps lua chad.Deps()]]

local set_chad_call = function(cmd)
  local t1 = 0
  chad[cmd] = function(...)
    local args = {...}
    if t1 == 0 then
      t1 = vim.loop.now()
    end

    if not job_id then
      local server = vim.api.nvim_call_function("serverstart", {})
      job_id = start(false, "run", "--socket", server)
    end

    if not err_exit and CHAD[cmd] then
      CHAD[cmd](args)
      t2 = vim.loop.now()
      if settings().profiling and t1 >= 0 then
        print("Init       " .. (t2 - t1) .. "ms")
      end
      t1 = -1
    else
      defer(
        POLLING_RATE,
        function()
          if err_exit then
            return
          else
            chad[cmd](unpack(args))
          end
        end
      )
    end
  end
end

set_chad_call("Noop")

set_chad_call("Open")
vim.api.nvim_command [[command! -nargs=* CHADopen lua chad.Open(<f-args>)]]

set_chad_call("Help")
vim.api.nvim_command [[command! -nargs=* CHADhelp lua chad.Help(<f-args>)]]

chad.lsp_ensure_capabilities = function(cfg)
  local spec1 = {
    capabilities = vim.lsp.protocol.make_client_capabilities()
  }
  local spec2 = {
    capabilities = {
      workspace = {
        fileOperations = {
          didCreate = true,
          didRename = true,
          didDelete = true
        }
      }
    }
  }
  local maps = cfg.capabilities and {spec2} or {spec1, spec2}
  local new =
    vim.tbl_deep_extend("force", cfg or vim.empty_dict(), unpack(maps))
  return new
end

chad.Noop()
return chad
