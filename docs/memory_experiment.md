# Memory Performance Experiment — Sequential Write

## Objective

Compare sequential memory-write throughput between a VMware virtual machine and a Docker container under equivalent CPU and memory resource allocation.

## Host

- OS: Windows 11 Pro
- CPU: Intel Core i9-14900KF
- Physical cores: 24
- Logical processors: 32
- RAM: approximately 64 GB
- Storage: approximately 1 TB SSD
- VMware Workstation: 17.6.4
- Docker Desktop: 29.7.2
- Docker backend: WSL2

## Virtual Machine

- Ubuntu: 24.04.4 LTS
- vCPU: 4
- RAM: 8 GB
- Virtual disk: 60 GB
- Network: NAT

## Docker

- Base image: Ubuntu 24.04
- CPU quota: 4 CPUs
- Memory limit: 8 GiB
- Visible CPUs reported by `nproc`: 32

## Workload

- Benchmark: Sysbench memory
- Version: 1.0.20
- Operation: Write
- Access mode: Sequential
- Block size: 1 MiB
- Total data transferred: 4 GiB
- Threads: 4
- Repetitions: 5

## Primary Metric

Memory throughput in MiB/s.

Higher throughput indicates greater measured memory-write performance.

## VM Results

| Run | Throughput (MiB/s) |
|---:|---:|
| 1 | 117947.43 |
| 2 | 114792.24 |
| 3 | 113839.41 |
| 4 | 98113.58 |
| 5 | 114955.29 |

Mean: 111929.59 MiB/s

## Docker Results

| Run | Throughput (MiB/s) |
|---:|---:|
| 1 | 130064.19 |
| 2 | 129146.42 |
| 3 | 121460.46 |
| 4 | 128869.68 |
| 5 | 130722.78 |

Mean: 128052.71 MiB/s

## Observation

Docker produced higher average sequential memory-write throughput than the VMware VM in this experiment.

The measured mean difference was approximately 14.40%.

Docker also exhibited lower run-to-run variation than the VM in the five measured repetitions.

## Limitations

The workload completes very quickly, in approximately 0.03–0.04 seconds. Such short measurements can be sensitive to caching, scheduling, system state, and measurement overhead.

The VM and Docker measurements were also collected at different times rather than in an interleaved randomized order.

Therefore, the result should be interpreted as a workload-specific experimental observation rather than a universal performance advantage of containers.

## Validation

A separate validation run was performed before the official measurements and was excluded from the five-run dataset.

## Reproducibility

Raw results:

- `results/memory/vm_memory_results.csv`
- `results/memory/docker_memory_results.csv`

Combined dataset:

- `results/memory/combined_memory_results.csv`

Analysis:

- `analysis/analyze_memory.py`
