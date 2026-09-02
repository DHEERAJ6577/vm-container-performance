import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = BASE_DIR / "results" / "memory" / "raw"
OUTPUT_DIR = BASE_DIR / "results" / "memory"
PLOT_DIR = BASE_DIR / "plots"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
PLOT_DIR.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------
# Workload definitions
# ---------------------------------------------------------
datasets = {
    "sequential_write": {
        "vm": RAW_DIR / "vm_write_seq.csv",
        "docker": RAW_DIR / "docker_write_seq.csv",
    },
    "sequential_read": {
        "vm": RAW_DIR / "vm_read_seq.csv",
        "docker": RAW_DIR / "docker_read_seq.csv",
    },
    "random_write": {
        "vm": RAW_DIR / "vm_write_rnd.csv",
        "docker": RAW_DIR / "docker_write_rnd.csv",
    },
    "random_read": {
        "vm": RAW_DIR / "vm_read_rnd.csv",
        "docker": RAW_DIR / "docker_read_rnd.csv",
    },
}

frames = []

# ---------------------------------------------------------
# Load and validate all datasets
# ---------------------------------------------------------
for workload, environments in datasets.items():
    for environment, file_path in environments.items():

        if not file_path.exists():
            raise FileNotFoundError(f"Missing dataset: {file_path}")

        df = pd.read_csv(file_path)

        required_columns = {
            "timestamp",
            "environment",
            "run_id",
            "threads",
            "operation",
            "access_mode",
            "block_size",
            "total_size",
            "throughput_mib_per_sec",
            "total_time_seconds",
        }

        missing = required_columns - set(df.columns)

        if missing:
            raise ValueError(
                f"{file_path} is missing columns: {sorted(missing)}"
            )

        # Only official runs are allowed.
        df = df[df["run_id"].between(1, 5)].copy()

        if len(df) != 5:
            raise ValueError(
                f"{file_path} contains {len(df)} official runs; expected exactly 5."
            )

        expected_environment = environment

        if not (df["environment"] == expected_environment).all():
            raise ValueError(
                f"{file_path} contains unexpected environment values."
            )

        df["workload"] = workload

        frames.append(df)

# ---------------------------------------------------------
# Combined 40-row dataset
# ---------------------------------------------------------
combined = pd.concat(frames, ignore_index=True)

combined = combined.sort_values(
    ["workload", "environment", "run_id"]
).reset_index(drop=True)

combined.to_csv(
    OUTPUT_DIR / "combined_memory_results.csv",
    index=False
)

# ---------------------------------------------------------
# Statistical summary
# ---------------------------------------------------------
summary = (
    combined
    .groupby(["workload", "environment"])["throughput_mib_per_sec"]
    .agg(
        mean="mean",
        median="median",
        std_dev="std",
        minimum="min",
        maximum="max",
        runs="count",
    )
    .reset_index()
)

summary["coefficient_of_variation_percent"] = (
    summary["std_dev"] / summary["mean"] * 100
)

summary = summary[
    [
        "workload",
        "environment",
        "runs",
        "mean",
        "median",
        "std_dev",
        "coefficient_of_variation_percent",
        "minimum",
        "maximum",
    ]
]

summary.to_csv(
    OUTPUT_DIR / "memory_summary.csv",
    index=False
)

# ---------------------------------------------------------
# VM vs Docker comparison
# ---------------------------------------------------------
comparison_rows = []

workload_order = [
    "sequential_write",
    "sequential_read",
    "random_write",
    "random_read",
]

for workload in workload_order:

    vm_mean = summary.loc[
        (summary["workload"] == workload)
        & (summary["environment"] == "vm"),
        "mean",
    ].iloc[0]

    docker_mean = summary.loc[
        (summary["workload"] == workload)
        & (summary["environment"] == "docker"),
        "mean",
    ].iloc[0]

    vm_cv = summary.loc[
        (summary["workload"] == workload)
        & (summary["environment"] == "vm"),
        "coefficient_of_variation_percent",
    ].iloc[0]

    docker_cv = summary.loc[
        (summary["workload"] == workload)
        & (summary["environment"] == "docker"),
        "coefficient_of_variation_percent",
    ].iloc[0]

    difference_percent = (
        (docker_mean - vm_mean) / vm_mean
    ) * 100

    comparison_rows.append(
        {
            "workload": workload,
            "vm_mean_mib_per_sec": vm_mean,
            "docker_mean_mib_per_sec": docker_mean,
            "docker_difference_vs_vm_percent": difference_percent,
            "vm_cv_percent": vm_cv,
            "docker_cv_percent": docker_cv,
        }
    )

comparison = pd.DataFrame(comparison_rows)

comparison.to_csv(
    OUTPUT_DIR / "memory_comparison.csv",
    index=False
)

# ---------------------------------------------------------
# Console output
# ---------------------------------------------------------
print("\nMEMORY PERFORMANCE SUMMARY")
print("=" * 90)
print(summary.to_string(index=False))

print("\nVM vs DOCKER")
print("=" * 90)

for _, row in comparison.iterrows():
    print(
        f"{row['workload']:20s} | "
        f"VM: {row['vm_mean_mib_per_sec']:12.2f} MiB/s | "
        f"Docker: {row['docker_mean_mib_per_sec']:12.2f} MiB/s | "
        f"Difference: {row['docker_difference_vs_vm_percent']:7.2f}%"
    )

# ---------------------------------------------------------
# Plot 1: Mean throughput by workload
# ---------------------------------------------------------
plt.figure(figsize=(10, 6))

plot_data = comparison.copy()

x = range(len(plot_data))
width = 0.35

plt.bar(
    [i - width / 2 for i in x],
    plot_data["vm_mean_mib_per_sec"],
    width=width,
    label="VM",
)

plt.bar(
    [i + width / 2 for i in x],
    plot_data["docker_mean_mib_per_sec"],
    width=width,
    label="Docker",
)

plt.xticks(
    list(x),
    [
        "Sequential Write",
        "Sequential Read",
        "Random Write",
        "Random Read",
    ],
    rotation=15,
)

plt.ylabel("Mean throughput (MiB/s)")
plt.xlabel("Memory workload")
plt.title("Memory Performance: VM vs Docker")
plt.legend()
plt.tight_layout()

plot_file = PLOT_DIR / "memory_vm_vs_docker.png"
plt.savefig(plot_file, dpi=200)
plt.close()

print(f"\nMean comparison plot saved to: {plot_file}")

# ---------------------------------------------------------
# Plot 2: Individual runs
# ---------------------------------------------------------
figures = {
    "sequential_write": "Sequential Write",
    "sequential_read": "Sequential Read",
    "random_write": "Random Write",
    "random_read": "Random Read",
}

for workload, title in figures.items():

    plt.figure(figsize=(8, 5))

    for environment in ["vm", "docker"]:

        values = combined.loc[
            (combined["workload"] == workload)
            & (combined["environment"] == environment),
            "throughput_mib_per_sec",
        ].to_numpy()

        plt.plot(
            range(1, len(values) + 1),
            values,
            marker="o",
            label=environment.upper(),
        )

    plt.xlabel("Run")
    plt.ylabel("Memory throughput (MiB/s)")
    plt.title(f"{title}: VM vs Docker")
    plt.xticks(range(1, 6))
    plt.legend()
    plt.tight_layout()

    plot_file = PLOT_DIR / f"memory_{workload}_runs.png"
    plt.savefig(plot_file, dpi=200)
    plt.close()

    print(f"Run plot saved to: {plot_file}")

print("\nAnalysis complete.")
