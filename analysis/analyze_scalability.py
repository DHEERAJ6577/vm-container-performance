import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

RESULT_DIR = BASE_DIR / "results" / "scalability"
PLOT_DIR = BASE_DIR / "plots"

VM_FILE = RESULT_DIR / "scalability_vm.csv"
DOCKER_FILE = RESULT_DIR / "scalability_docker.csv"

RESULT_DIR.mkdir(parents=True, exist_ok=True)
PLOT_DIR.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------
# Load datasets
# ---------------------------------------------------------
vm = pd.read_csv(VM_FILE)
docker = pd.read_csv(DOCKER_FILE)

# ---------------------------------------------------------
# Validate expected concurrency levels
# ---------------------------------------------------------
expected_levels = [1, 2, 4, 8]

for name, df in [("VM", vm), ("Docker", docker)]:
    actual_levels = sorted(df["concurrency"].astype(int).tolist())

    if actual_levels != expected_levels:
        raise ValueError(
            f"{name} dataset has concurrency levels "
            f"{actual_levels}; expected {expected_levels}"
        )

    if len(df) != 4:
        raise ValueError(
            f"{name} dataset contains {len(df)} rows; expected 4."
        )

# ---------------------------------------------------------
# Build combined dataset
# ---------------------------------------------------------
vm["environment"] = "vm"
docker["environment"] = "docker"

combined = pd.concat(
    [vm, docker],
    ignore_index=True
)

combined = combined.sort_values(
    ["concurrency", "environment"]
).reset_index(drop=True)

combined.to_csv(
    RESULT_DIR / "combined_scalability_results.csv",
    index=False
)

# ---------------------------------------------------------
# Baselines
# ---------------------------------------------------------
vm_baseline = vm.loc[
    vm["concurrency"] == 1,
    "total_events_per_sec"
].iloc[0]

docker_baseline = docker.loc[
    docker["concurrency"] == 1,
    "total_events_per_sec"
].iloc[0]

# ---------------------------------------------------------
# Calculate scaling efficiency
# ---------------------------------------------------------
vm["scaling_efficiency_percent"] = (
    vm["total_events_per_sec"]
    / (vm_baseline * vm["concurrency"])
) * 100

docker["scaling_efficiency_percent"] = (
    docker["total_events_per_sec"]
    / (docker_baseline * docker["concurrency"])
) * 100

# ---------------------------------------------------------
# Throughput relative to previous level
# ---------------------------------------------------------
def add_change_column(df):
    df = df.sort_values("concurrency").copy()

    df["throughput_change_vs_previous_percent"] = (
        df["total_events_per_sec"]
        .pct_change()
        .mul(100)
    )

    df.loc[
        df["concurrency"] == 1,
        "throughput_change_vs_previous_percent"
    ] = 0.0

    return df


vm = add_change_column(vm)
docker = add_change_column(docker)

# ---------------------------------------------------------
# VM vs Docker comparison
# ---------------------------------------------------------
comparison = pd.merge(
    vm[
        [
            "concurrency",
            "total_events_per_sec",
            "scaling_efficiency_percent",
            "wall_time_seconds",
            "throughput_change_vs_previous_percent",
        ]
    ],
    docker[
        [
            "concurrency",
            "total_events_per_sec",
            "scaling_efficiency_percent",
            "wall_time_seconds",
            "throughput_change_vs_previous_percent",
        ]
    ],
    on="concurrency",
    suffixes=("_vm", "_docker")
)

comparison["docker_vs_vm_throughput_percent"] = (
    (
        comparison["total_events_per_sec_docker"]
        - comparison["total_events_per_sec_vm"]
    )
    / comparison["total_events_per_sec_vm"]
) * 100

comparison.to_csv(
    RESULT_DIR / "scalability_comparison.csv",
    index=False
)

# ---------------------------------------------------------
# Detailed summary
# ---------------------------------------------------------
summary = pd.concat(
    [
        vm.assign(environment="vm"),
        docker.assign(environment="docker"),
    ],
    ignore_index=True,
)

summary = summary[
    [
        "environment",
        "concurrency",
        "prime_limit",
        "duration_seconds",
        "total_events",
        "total_events_per_sec",
        "wall_time_seconds",
        "scaling_efficiency_percent",
        "throughput_change_vs_previous_percent",
    ]
]

summary.to_csv(
    RESULT_DIR / "scalability_summary.csv",
    index=False
)

# ---------------------------------------------------------
# Print results
# ---------------------------------------------------------
print("\nSCALABILITY PERFORMANCE SUMMARY")
print("=" * 100)
print(summary.to_string(index=False))

print("\nVM vs DOCKER THROUGHPUT")
print("=" * 100)

for _, row in comparison.iterrows():
    print(
        f"Concurrency {int(row['concurrency']):2d} | "
        f"VM: {row['total_events_per_sec_vm']:10.2f} events/s | "
        f"Docker: {row['total_events_per_sec_docker']:10.2f} events/s | "
        f"Docker vs VM: {row['docker_vs_vm_throughput_percent']:7.2f}%"
    )

# ---------------------------------------------------------
# Plot 1: Throughput scaling
# ---------------------------------------------------------
plt.figure(figsize=(9, 6))

plt.plot(
    vm["concurrency"],
    vm["total_events_per_sec"],
    marker="o",
    label="VM",
)

plt.plot(
    docker["concurrency"],
    docker["total_events_per_sec"],
    marker="o",
    label="Docker",
)

plt.xlabel("Concurrent workloads")
plt.ylabel("Aggregate throughput (events/s)")
plt.title("Scalability: VM vs Docker")
plt.xticks(expected_levels)
plt.legend()
plt.grid(True, alpha=0.3)
plt.tight_layout()

throughput_plot = PLOT_DIR / "scalability_throughput.png"

plt.savefig(
    throughput_plot,
    dpi=200,
)

plt.close()

print(f"\nThroughput plot saved to: {throughput_plot}")

# ---------------------------------------------------------
# Plot 2: Scaling efficiency
# ---------------------------------------------------------
plt.figure(figsize=(9, 6))

plt.plot(
    vm["concurrency"],
    vm["scaling_efficiency_percent"],
    marker="o",
    label="VM",
)

plt.plot(
    docker["concurrency"],
    docker["scaling_efficiency_percent"],
    marker="o",
    label="Docker",
)

plt.xlabel("Concurrent workloads")
plt.ylabel("Scaling efficiency (%)")
plt.title("Scaling Efficiency: VM vs Docker")
plt.xticks(expected_levels)
plt.legend()
plt.grid(True, alpha=0.3)
plt.tight_layout()

efficiency_plot = PLOT_DIR / "scalability_efficiency.png"

plt.savefig(
    efficiency_plot,
    dpi=200,
)

plt.close()

print(f"Efficiency plot saved to: {efficiency_plot}")

# ---------------------------------------------------------
# Plot 3: Docker vs VM throughput percentage
# ---------------------------------------------------------
plt.figure(figsize=(9, 6))

plt.plot(
    comparison["concurrency"],
    comparison["docker_vs_vm_throughput_percent"],
    marker="o",
)

plt.axhline(
    0,
    linewidth=1,
)

plt.xlabel("Concurrent workloads")
plt.ylabel("Docker vs VM throughput (%)")
plt.title("Docker Throughput Difference Relative to VM")
plt.xticks(expected_levels)
plt.tight_layout()

difference_plot = PLOT_DIR / "scalability_docker_vs_vm.png"

plt.savefig(
    difference_plot,
    dpi=200,
)

plt.close()

print(f"Docker vs VM plot saved to: {difference_plot}")

print("\nScalability analysis complete.")