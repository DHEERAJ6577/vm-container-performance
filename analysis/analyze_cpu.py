import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
INPUT_FILE = BASE_DIR / "results" / "cpu" / "analysis_cpu_results.csv"
OUTPUT_DIR = BASE_DIR / "results" / "cpu"
PLOT_DIR = BASE_DIR / "plots"

PLOT_DIR.mkdir(parents=True, exist_ok=True)

df = pd.read_csv(INPUT_FILE)

metric = "events_per_second"

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
        "VM mean events/sec",
        "Docker mean events/sec",
        "Docker difference vs VM (%)"
    ],
    "value": [
        vm_mean,
        docker_mean,
        difference_percent
    ]
})

summary.to_csv(
    OUTPUT_DIR / "cpu_summary.csv",
    index=False
)

comparison.to_csv(
    OUTPUT_DIR / "cpu_comparison.csv",
    index=False
)

print("\nCPU PERFORMANCE SUMMARY")
print("=" * 50)
print(summary.to_string(index=False))

print("\nDocker vs VM")
print("=" * 50)
print(f"VM mean       : {vm_mean:.2f} events/sec")
print(f"Docker mean   : {docker_mean:.2f} events/sec")
print(f"Difference    : {difference_percent:.3f}%")

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
plt.ylabel("Events per second")
plt.title("CPU Benchmark: VM vs Docker")
plt.xticks(range(1, 6))
plt.legend()
plt.tight_layout()

plot_file = PLOT_DIR / "cpu_vm_vs_docker_runs.png"
plt.savefig(plot_file, dpi=200)
plt.close()

print(f"\nPlot saved to: {plot_file}")
print(f"Summary saved to: {OUTPUT_DIR / 'cpu_summary.csv'}")
