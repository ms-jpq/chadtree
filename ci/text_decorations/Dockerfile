FROM ubuntu:latest


RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends -- neovim git ca-certificates && \
    rm -rf -- /var/lib/apt/lists/*


WORKDIR /root


RUN git clone --depth=1 https://github.com/ryanoasis/vim-devicons.git && \
    git clone --depth=1 https://github.com/adelarsq/vim-emoji-icon-theme.git && \
    git clone --depth=1 https://github.com/tiagofumo/vim-nerdtree-syntax-highlight.git


COPY . /


RUN nvim --headless
ENTRYPOINT ["cat", "exports.json"]
