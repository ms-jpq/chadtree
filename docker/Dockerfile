FROM ubuntu:focal


RUN apt update && \
    apt install -y python3-pip neovim git wget && \
    pip3 install pynvim


WORKDIR /root/.config/nvim
RUN mkdir -p autoload && \
    cd autoload && \
    wget https://raw.githubusercontent.com/junegunn/vim-plug/master/plug.vim


COPY root /
