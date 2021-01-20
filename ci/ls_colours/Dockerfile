FROM ubuntu:latest


RUN apt-get update && \
    apt-get install -y --no-install-recommends git python3 && \
    rm -rf /var/lib/apt/lists/*


WORKDIR /root


RUN GIT_SSL_NO_VERIFY=1 git clone --depth=1 https://github.com/seebi/dircolors-solarized.git
COPY . /


ENTRYPOINT ["./lsc.py", "dircolors-solarized"]
