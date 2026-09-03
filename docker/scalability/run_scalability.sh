#!/bin/bash

set -e

ENVIRONMENT="${1:-vm}"
CONCURRENCY="${2:-1}"

PRIME_LIMIT=20000
DURATION=30

RESULT_DIR="results/scalability"
RESULT_FILE="${RESULT_DIR}/scalability_${ENVIRONMENT}.csv"
LOG_DIR="logs/scalability"

mkdir -p "$RESULT_DIR" "$LOG_DIR"

if [ ! -f "$RESULT_FILE" ]; then
    echo "timestamp,environment,concurrency,prime_limit,duration_seconds,total_events,total_events_per_sec,wall_time_seconds" > "$RESULT_FILE"
fi

echo "=========================================="
echo "SCALABILITY BENCHMARK"
echo "=========================================="
echo "Environment : $ENVIRONMENT"
echo "Concurrency : $CONCURRENCY"
echo "Prime limit : $PRIME_LIMIT"
echo "Duration    : ${DURATION}s"
echo "=========================================="

START_TIME=$(date +%s.%N)

PIDS=()

for i in $(seq 1 "$CONCURRENCY"); do
    LOG_FILE="${LOG_DIR}/${ENVIRONMENT}_c${CONCURRENCY}_job${i}.log"

    sysbench cpu \
        --cpu-max-prime="$PRIME_LIMIT" \
        --threads=1 \
        --time="$DURATION" \
        run > "$LOG_FILE" 2>&1 &

    PIDS+=("$!")
done

for PID in "${PIDS[@]}"; do
    wait "$PID"
done

END_TIME=$(date +%s.%N)

WALL_TIME=$(awk -v start="$START_TIME" -v end="$END_TIME" \
    'BEGIN {printf "%.4f", end - start}')

TOTAL_EVENTS=0

for i in $(seq 1 "$CONCURRENCY"); do
    LOG_FILE="${LOG_DIR}/${ENVIRONMENT}_c${CONCURRENCY}_job${i}.log"

    EVENTS=$(grep "events per second:" "$LOG_FILE" | awk '{print $4}')

    if [ -n "$EVENTS" ]; then
        TOTAL_EVENTS=$(awk -v total="$TOTAL_EVENTS" -v value="$EVENTS" \
            'BEGIN {printf "%.2f", total + value}')
    fi
done

TOTAL_EVENTS_PER_SEC=$(awk -v total="$TOTAL_EVENTS" \
    'BEGIN {printf "%.2f", total}')

TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

echo "${TIMESTAMP},${ENVIRONMENT},${CONCURRENCY},${PRIME_LIMIT},${DURATION},${TOTAL_EVENTS},${TOTAL_EVENTS_PER_SEC},${WALL_TIME}" >> "$RESULT_FILE"

echo ""
echo "Result:"
echo "Concurrency          : $CONCURRENCY"
echo "Aggregate throughput : $TOTAL_EVENTS_PER_SEC events/sec"
echo "Wall-clock time      : $WALL_TIME seconds"
