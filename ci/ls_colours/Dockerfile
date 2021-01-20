FROM ubuntu:latest


RUN apt-get update && \
    apt-get install -y --no-install-recommends  && \
    rm -rf /var/lib/apt/lists/*


WORKDIR /root


RUN git clone --depth=1 https://github.com/seebi/dircolors-solarized.git
COPY . /


RUN nvim --headless
