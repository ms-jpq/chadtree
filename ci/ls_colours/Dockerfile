FROM ubuntu:latest


RUN apt-get update && \
    apt-get install -y git python3 && \
    rm -rf /var/lib/apt/lists/*


WORKDIR /root


RUN git clone --depth=1 https://github.com/seebi/dircolors-solarized.git && \
    git clone --depth=1 https://github.com/arcticicestudio/nord-dircolors.git
COPY . /


ENTRYPOINT ["./lsc.py"]
