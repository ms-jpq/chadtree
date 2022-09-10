nnoremap <silent> Q  <esc>
nnoremap <silent> QQ <cmd>quitall!<cr>
vnoremap <silent> Q  <nop>
vnoremap <silent> QQ <cmd>quitall!<cr>

filetype on
set nomodeline
set secure
set termguicolors
set shortmess+=I

let g:python3_host_prog = '/usr/bin/python3'
let g:chadtree_settings = {'profiling': v:true, 'xdg': v:true}
let mapleader=' '
nnoremap <leader>v <cmd>CHADopen<cr>

packloadall
