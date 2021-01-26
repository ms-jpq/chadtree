autocmd VimEnter * silent! autocmd! FileExplorer
silent! autocmd! FileExplorer


let s:top_level = resolve(expand('<sfile>:p:h:h'))
call luaeval('require("chadtree")(...)', [s:top_level])