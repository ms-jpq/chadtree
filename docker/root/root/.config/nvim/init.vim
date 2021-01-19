call plug#begin('~/.config/nvim/plugged')
Plug 'ms-jpq/chadtree', {'branch': 'future2', 'do': 'python3 -m chadtree deps'}
call plug#end()

let mapleader=' '
nnoremap <leader>v <cmd>CHADopen<cr>
