FROM ubuntu:latest


ARG ROOT="/root/.config/nvim/autoload"

RUN apt update && \
    apt install -y python3-pip neovim wget && \
    mkdir -p ${ROOT} && \
    wget https://raw.githubusercontent.com/junegunn/vim-plug/master/plug.vim


WORKDIR ${ROOT}
COPY ./docker/init.vim .
