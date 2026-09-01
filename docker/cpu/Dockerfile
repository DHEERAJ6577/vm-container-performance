FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        sysbench \
        util-linux \
        ca-certificates && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /benchmark

COPY run_cpu.sh .

RUN sed -i "s/\r$//" /benchmark/run_cpu.sh && chmod +x /benchmark/run_cpu.sh

