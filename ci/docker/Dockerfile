FROM ubuntu:focal


RUN apt update && \
    apt install -y software-properties-common && \
    add-apt-repository ppa:neovim-ppa/unstable && \
    apt update && \
    apt install -y neovim git
WORKDIR /root

RUN git clone --depth=1 https://github.com/ryanoasis/vim-devicons.git && \
    git clone --depth=1 https://github.com/adelarsq/vim-emoji-icon-theme.git && \
    git clone --depth=1 https://github.com/nvim-lua/lsp-status.nvim.git

COPY . /

RUN nvim --headless
