#!/bin/bash

set -e

ENVIRONMENT="${1:-docker}"
RUN_ID="${2:-1}"

RESULT_DIR="/benchmark/results"
RESULT_FILE="${RESULT_DIR}/memory_results.csv"
LOG_FILE="/tmp/memory_run.log"

mkdir -p "${RESULT_DIR}"

TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
CPU_MODEL=$(lscpu | grep "Model name" | head -1 | cut -d: -f2- | xargs)
CPU_VISIBLE=$(nproc)

if [ ! -f "${RESULT_FILE}" ]; then
    echo "timestamp,environment,run_id,cpu_model,cpu_visible,threads,operation,access_mode,block_size,total_size,throughput_mib_per_sec,total_time_seconds" > "${RESULT_FILE}"
fi

echo "=========================================="
echo "MEMORY PERFORMANCE BENCHMARK"
echo "=========================================="
echo "Environment : ${ENVIRONMENT}"
echo "Run         : ${RUN_ID}"
echo "CPU         : ${CPU_MODEL}"
echo "Visible CPU : ${CPU_VISIBLE}"
echo "Threads     : 4"
echo "Operation   : write"
echo "Access mode : sequential"
echo "Block size  : 1 MiB"
echo "Total size  : 4 GiB"
echo "=========================================="

sysbench memory --memory-block-size=1M --memory-total-size=4G --memory-oper=write --memory-access-mode=seq --threads=4 run | tee "${LOG_FILE}"

THROUGHPUT=$(grep "MiB/sec" "${LOG_FILE}" | tail -1 | sed -E 's/.*\(([0-9.]+) MiB\/sec\).*/\1/')
TOTAL_TIME=$(grep "total time:" "${LOG_FILE}" | awk '{print $3}' | sed 's/s//')

echo "${TIMESTAMP},${ENVIRONMENT},${RUN_ID},\"${CPU_MODEL}\",${CPU_VISIBLE},4,write,seq,1M,4G,${THROUGHPUT},${TOTAL_TIME}" >> "${RESULT_FILE}"

echo ""
echo "Result:"
tail -1 "${RESULT_FILE}"
