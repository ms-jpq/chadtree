FROM ubuntu:latest


RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends -- python3 git ca-certificates && \
    rm -rf -- /var/lib/apt/lists/* && \
    update-ca-certificates


WORKDIR /root


RUN git clone --depth=1 https://github.com/seebi/dircolors-solarized.git && \
    git clone --depth=1 https://github.com/arcticicestudio/nord-dircolors.git && \
    git clone --depth=1 https://github.com/trapd00r/LS_COLORS
COPY . /


ENTRYPOINT ["./lsc.py"]
