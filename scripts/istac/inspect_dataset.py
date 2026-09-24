from __future__ import annotations

from pathlib import Path

import pandas as pd

DATASET_CODE = "C00065A_000036"
DATA_ROOT = Path("data/raw/istac")


def find_dataset() -> Path:
    """Find the most recently modified dataset file."""

    dataset_root = DATA_ROOT / DATASET_CODE

    datasets = list(dataset_root.glob("*/dataset.csv"))

    if not datasets:
        raise FileNotFoundError(
            f"No dataset.csv file found in {dataset_root}"
        )

    return max(datasets, key=lambda path: path.stat().st_mtime)


def load_dataset(path: Path) -> pd.DataFrame:
    """Load a dataset from the given path."""

    print(f"Loading: {path}")

    return pd.read_csv(
        path,
        low_memory=False,
    )


def print_basic_information(df: pd.DataFrame) -> None:
    """Print basic information about the dataset."""

    print("\n=== BASIC INFORMATION ===")
    print(f"Rows: {len(df):,}")
    print(f"Columns: {len(df.columns)}")

    print("\nColumns:")
    for column in df.columns:
        print(f"  - {column}")


def print_missing_values(df: pd.DataFrame) -> None:
    """Print missing value counts and percentages by column."""

    print("\n=== MISSING VALUES ===")

    missing = (
        df.isna()
        .sum()
        .sort_values(ascending=False)
    )

    result = pd.DataFrame(
        {
            "missing": missing,
            "percentage": (
                missing / len(df) * 100
            ).round(2),
        }
    )

    print(
        result[result["missing"] > 0].to_string()
    )


def print_dimensions(df: pd.DataFrame) -> None:
    """Print the main dimension values and their frequencies."""

    print("\n=== MAIN DIMENSIONS ===")

    dimensions = [
        "MEDIDAS_CODE",
        "TIME_PERIOD_CODE",
        "TERRITORIO_CODE",
        "NACIONALIDAD_CODE",
        "ALOJAMIENTO_TURISTICO_TIPO_CODE",
    ]

    for column in dimensions:
        if column not in df.columns:
            continue

        print(f"\n--- {column} ---")
        print(
            df[column]
            .value_counts(dropna=False)
            .head(20)
            .to_string()
        )


def main() -> None:
    """Run the dataset inspection."""

    dataset_path = find_dataset()
    df = load_dataset(dataset_path)

    print_basic_information(df)
    print_missing_values(df)
    print_dimensions(df)


if __name__ == "__main__":
    main()