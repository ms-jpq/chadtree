FROM ubuntu:focal

ENV TERM=xterm-256color
RUN apt-get update && \
    apt-get install -y python3-venv neovim git wget && \
    rm -rf /var/lib/apt/lists/*


WORKDIR /root/.config/nvim
RUN mkdir -p autoload && \
    wget https://raw.githubusercontent.com/junegunn/vim-plug/master/plug.vim --output-document=autoload/plug.vim && \
    git clone --depth=1 https://github.com/ms-jpq/chadtree.git


COPY docker/root /
COPY . /root/.config/nvim/plugged/chadtree/

ENV XDG_DATA_HOME /root/XDG_DATA_HOME
WORKDIR /root/.config/nvim/plugged/chadtree
# RUN python3 -m chadtree deps
