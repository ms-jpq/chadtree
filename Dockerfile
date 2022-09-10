FROM ubuntu:focal

ENV TERM=xterm-256color
RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install --yes --no-install-recommends -- python3-venv neovim git ca-certificates && \
    rm -rf -- /var/lib/apt/lists/*


COPY ./docker /
WORKDIR /root/.config/nvim/pack/modules/start/chadtree
COPY . .

RUN python3 -m chadtree deps --xdg ~/.local/share/nvim
