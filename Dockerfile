FROM ubuntu:latest

ENV TERM=xterm-256color
RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install --yes --no-install-recommends -- python3-venv neovim git ca-certificates && \
    rm -rf -- /var/lib/apt/lists/*


ADD https://raw.githubusercontent.com/junegunn/vim-plug/master/plug.vim /root/.config/nvim/autoload/plug.vim
COPY ./docker /
COPY . /root/.config/nvim/plugged/chadtree

WORKDIR /root/.config/nvim/plugged/chadtree
