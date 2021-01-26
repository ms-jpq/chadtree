autocmd VimEnter * silent! autocmd! FileExplorer
silent! autocmd! FileExplorer

function CHADon_exit(_, code, __)
  call luaeval('chad.on_exit(...)', [a:code])
endfunction
function CHADon_stdout(_, msg, __)
  call luaeval('chad.on_stdout(...)', [a:msg])
endfunction
function CHADon_stderr(_, msg, __)
  call luaeval('chad.on_stderr(...)', [a:msg])
endfunction


call luaeval('require("chadtree")(...)', [expand('<sfile>:p:h:h')])