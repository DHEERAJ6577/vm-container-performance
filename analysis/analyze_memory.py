import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
INPUT_FILE = BASE_DIR / "results" / "memory" / "combined_memory_results.csv"
OUTPUT_DIR = BASE_DIR / "results" / "memory"
PLOT_DIR = BASE_DIR / "plots"

PLOT_DIR.mkdir(parents=True, exist_ok=True)

df = pd.read_csv(INPUT_FILE)

metric = "throughput_mib_per_sec"

summary = (
    df.groupby("environment")[metric]
    .agg(
        mean="mean",
        median="median",
        std_dev="std",
        minimum="min",
        maximum="max"
    )
    .reset_index()
)

summary["coefficient_of_variation_percent"] = (
    summary["std_dev"] / summary["mean"] * 100
)

vm_mean = summary.loc[
    summary["environment"] == "vm", "mean"
].iloc[0]

docker_mean = summary.loc[
    summary["environment"] == "docker", "mean"
].iloc[0]

difference_percent = ((docker_mean - vm_mean) / vm_mean) * 100

comparison = pd.DataFrame({
    "metric": [
        "VM mean throughput (MiB/s)",
        "Docker mean throughput (MiB/s)",
        "Docker difference vs VM (%)"
    ],
    "value": [
        vm_mean,
        docker_mean,
        difference_percent
    ]
})

summary.to_csv(
    OUTPUT_DIR / "memory_summary.csv",
    index=False
)

comparison.to_csv(
    OUTPUT_DIR / "memory_comparison.csv",
    index=False
)

print("\nMEMORY PERFORMANCE SUMMARY")
print("=" * 60)
print(summary.to_string(index=False))

print("\nDocker vs VM")
print("=" * 60)
print(f"VM mean       : {vm_mean:.2f} MiB/sec")
print(f"Docker mean   : {docker_mean:.2f} MiB/sec")
print(f"Difference    : {difference_percent:.2f}%")

plt.figure(figsize=(8, 5))

for environment in ["vm", "docker"]:
    values = df.loc[
        df["environment"] == environment,
        metric
    ].to_numpy()

    plt.scatter(
        range(1, len(values) + 1),
        values,
        label=environment.upper(),
        s=60
    )

plt.xlabel("Run")
plt.ylabel("Memory throughput (MiB/s)")
plt.title("Sequential Memory Write: VM vs Docker")
plt.xticks(range(1, 6))
plt.legend()
plt.tight_layout()

plot_file = PLOT_DIR / "memory_vm_vs_docker_runs.png"
plt.savefig(plot_file, dpi=200)
plt.close()

print(f"\nPlot saved to: {plot_file}")
