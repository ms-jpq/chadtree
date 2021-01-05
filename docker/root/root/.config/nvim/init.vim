call plug#begin('~/.config/nvim/plugged')
Plug 'ms-jpq/chadtree', {'branch': 'chad'}
call plug#end()

let mapleader=' '
nnoremap <leader>v <cmd>CHADopen<cr>
