autocmd VimEnter * silent! autocmd! FileExplorer
silent! autocmd! FileExplorer

augroup CHADTree
  autocmd!
  autocmd FileType CHADTree autocmd BufEnter,WinEnter <buffer> stopinsert
augroup end

function CHADon_exit(_, code, __)
  call luaeval('chad.on_exit(...)', [a:code])
endfunction
function CHADon_stdout(_, msg, __)
  call luaeval('chad.on_stdout(...)', [a:msg])
endfunction
function CHADon_stderr(_, msg, __)
  call luaeval('chad.on_stderr(...)', [a:msg])
endfunction


call luaeval('require("chadtree") and 0')
