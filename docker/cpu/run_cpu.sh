#!/bin/bash

set -e

ENVIRONMENT="${1:-docker}"
RUN_ID="${2:-1}"

RESULT_DIR="/benchmark/results"
RESULT_FILE="${RESULT_DIR}/cpu_results.csv"
LOG_FILE="/tmp/cpu_run.log"

mkdir -p "${RESULT_DIR}"

TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
CPU_MODEL=$(lscpu | grep "Model name" | head -1 | cut -d: -f2- | xargs)
CPU_VISIBLE=$(nproc)

if [ ! -f "${RESULT_FILE}" ]; then
    echo "timestamp,environment,run_id,cpu_model,cpu_visible,threads,max_prime,duration_seconds,total_events,events_per_second" > "${RESULT_FILE}"
fi

echo "=========================================="
echo "CPU PERFORMANCE BENCHMARK"
echo "=========================================="
echo "Environment : ${ENVIRONMENT}"
echo "Run         : ${RUN_ID}"
echo "CPU         : ${CPU_MODEL}"
echo "Visible CPU : ${CPU_VISIBLE}"
echo "Threads     : 4"
echo "Max Prime   : 20000"
echo "Duration    : 30 seconds"
echo "=========================================="

sysbench cpu --cpu-max-prime=20000 --threads=4 --time=30 run | tee "${LOG_FILE}"

TOTAL_EVENTS=$(grep "total number of events:" "${LOG_FILE}" | awk '{print $NF}')
EVENTS_PER_SECOND=$(grep "events per second:" "${LOG_FILE}" | awk '{print $NF}')

echo "${TIMESTAMP},${ENVIRONMENT},${RUN_ID},\"${CPU_MODEL}\",${CPU_VISIBLE},4,20000,30,${TOTAL_EVENTS},${EVENTS_PER_SECOND}" >> "${RESULT_FILE}"

echo ""
echo "Result:"
tail -1 "${RESULT_FILE}"
