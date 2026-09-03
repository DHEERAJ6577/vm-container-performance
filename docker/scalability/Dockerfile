FROM ubuntu:24.04

RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y sysbench bash && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /benchmark

COPY run_scalability.sh /benchmark/run_scalability.sh

RUN chmod +x /benchmark/run_scalability.sh

ENTRYPOINT ["/bin/bash", "/benchmark/run_scalability.sh"]
