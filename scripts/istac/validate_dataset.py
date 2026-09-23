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


def load_dataset() -> pd.DataFrame:
    """Load the most recently available dataset."""

    path = find_dataset()

    print(f"Loading: {path}")

    return pd.read_csv(
        path,
        low_memory=False,
    )


def validate_estancia_media(df: pd.DataFrame) -> None:
    """
    Validate that ESTANCIA_MEDIA matches:

        PERNOCTACIONES / VIAJEROS_ENTRADOS

    for monthly observations with available data.
    """

    required_columns = {
        "TERRITORIO_CODE",
        "NACIONALIDAD_CODE",
        "ALOJAMIENTO_TURISTICO_TIPO_CODE",
        "TIME_PERIOD_CODE",
        "MEDIDAS_CODE",
        "OBS_VALUE",
    }

    missing_columns = required_columns - set(df.columns)

    if missing_columns:
        raise ValueError(
            f"Required columns are missing: {sorted(missing_columns)}"
        )

    subset = df[
        (df["TERRITORIO_CODE"] == "ES709")
        & (df["NACIONALIDAD_CODE"] == "_T")
        & (df["ALOJAMIENTO_TURISTICO_TIPO_CODE"] == "_T")
        & (df["TIME_PERIOD_CODE"].str.contains(r"-M\d{2}$", regex=True))
    ].copy()

    pivot = (
        subset.pivot_table(
            index="TIME_PERIOD_CODE",
            columns="MEDIDAS_CODE",
            values="OBS_VALUE",
            aggfunc="first",
        )
        .reset_index()
    )

    required_measures = {
        "VIAJEROS_ENTRADOS",
        "PERNOCTACIONES",
        "ESTANCIA_MEDIA",
    }

    if not required_measures.issubset(pivot.columns):
        print(
            "Not enough measures are available to validate ESTANCIA_MEDIA."
        )
        return

    valid = pivot.dropna(
        subset=[
            "VIAJEROS_ENTRADOS",
            "PERNOCTACIONES",
            "ESTANCIA_MEDIA",
        ]
    ).copy()

    valid["ESTANCIA_MEDIA_CALCULATED"] = (
        valid["PERNOCTACIONES"]
        / valid["VIAJEROS_ENTRADOS"]
    )

    valid["DIFFERENCE"] = (
        valid["ESTANCIA_MEDIA"]
        - valid["ESTANCIA_MEDIA_CALCULATED"]
    ).abs()

    print("\n=== ESTANCIA_MEDIA VALIDATION ===")
    print(f"Valid observations: {len(valid)}")

    if valid.empty:
        print("No sufficient observations are available.")
        return

    print(
        "Maximum difference:",
        valid["DIFFERENCE"].max(),
    )

    tolerance = 1e-9

    invalid = valid[
        valid["DIFFERENCE"] > tolerance
    ]

    print(
        f"Observations outside tolerance "
        f"({tolerance}): {len(invalid)}"
    )

    if len(invalid) > 0:
        print("\nFirst discrepancies:")
        print(
            invalid[
                [
                    "TIME_PERIOD_CODE",
                    "VIAJEROS_ENTRADOS",
                    "PERNOCTACIONES",
                    "ESTANCIA_MEDIA",
                    "ESTANCIA_MEDIA_CALCULATED",
                    "DIFFERENCE",
                ]
            ]
            .head(20)
            .to_string(index=False)
        )


def analyze_missingness_by_year(df: pd.DataFrame) -> None:
    """Analyze OBS_VALUE coverage by year."""

    data = df.copy()

    data["YEAR"] = (
        data["TIME_PERIOD_CODE"]
        .astype(str)
        .str[:4]
    )

    result = (
        data.groupby("YEAR")["OBS_VALUE"]
        .agg(
            rows="size",
            values="count",
            missing=lambda series: series.isna().sum(),
        )
    )

    result["coverage_percentage"] = (
        result["values"]
        / result["rows"]
        * 100
    ).round(2)

    print("\n=== COVERAGE BY YEAR ===")
    print(result.to_string())


def analyze_missingness_by_nationality(
    df: pd.DataFrame,
) -> None:
    """Analyze OBS_VALUE coverage by nationality and year."""

    data = df.copy()

    data["YEAR"] = (
        data["TIME_PERIOD_CODE"]
        .astype(str)
        .str[:4]
    )

    result = (
        data.groupby(
            ["NACIONALIDAD_CODE", "YEAR"]
        )["OBS_VALUE"]
        .count()
        .unstack(fill_value=0)
    )

    print("\n=== OBSERVATIONS BY NATIONALITY AND YEAR ===")
    print(result.to_string())


def identify_new_nationalities(
    df: pd.DataFrame,
    reference_year: int = 2021,
) -> None:
    """
    Identify nationalities with no observations before the reference
    year and observations from the reference year onwards.
    """

    data = df.copy()

    data["YEAR"] = (
        data["TIME_PERIOD_CODE"]
        .astype(str)
        .str[:4]
        .astype(int)
    )

    coverage = (
        data.groupby(
            ["NACIONALIDAD_CODE", "YEAR"]
        )["OBS_VALUE"]
        .count()
        .unstack(fill_value=0)
    )

    previous_years = [
        year
        for year in coverage.columns
        if year < reference_year
    ]

    future_years = [
        year
        for year in coverage.columns
        if year >= reference_year
    ]

    if not previous_years or not future_years:
        print(
            "\nNot enough temporal coverage to identify "
            "new nationalities."
        )
        return

    new_nationalities = coverage[
        (coverage[previous_years].sum(axis=1) == 0)
        & (coverage[future_years].sum(axis=1) > 0)
    ]

    print(
        "\n=== NATIONALITIES WITH NEW OBSERVATIONS ==="
    )

    if new_nationalities.empty:
        print("No nationalities matching the pattern were found.")
        return

    print(
        new_nationalities[
            future_years
        ].to_string()
    )


def analyze_observation_status(df: pd.DataFrame) -> None:
    """
    Analyze the relationship between OBS_VALUE and
    ESTADO_OBSERVACION_CODE.
    """

    print("\n=== OBSERVATION STATUS ===")

    columns = [
        "OBS_VALUE",
        "ESTADO_OBSERVACION_CODE",
    ]

    subset = df[columns].copy()

    result = (
        subset.groupby(
            "ESTADO_OBSERVACION_CODE",
            dropna=False,
        )
        .agg(
            rows=("OBS_VALUE", "size"),
            values=("OBS_VALUE", "count"),
            missing=("OBS_VALUE", lambda series: series.isna().sum()),
        )
        .sort_values("rows", ascending=False)
    )

    result["missing_percentage"] = (
        result["missing"]
        / result["rows"]
        * 100
    ).round(2)

    print(result.to_string())


def analyze_confidentiality(df: pd.DataFrame) -> None:
    """
    Analyze the relationship between OBS_VALUE and
    CONFIDENCIALIDAD_OBSERVACION_CODE.
    """

    print("\n=== OBSERVATION CONFIDENTIALITY ===")

    columns = [
        "OBS_VALUE",
        "CONFIDENCIALIDAD_OBSERVACION_CODE",
    ]

    subset = df[columns].copy()

    result = (
        subset.groupby(
            "CONFIDENCIALIDAD_OBSERVACION_CODE",
            dropna=False,
        )
        .agg(
            rows=("OBS_VALUE", "size"),
            values=("OBS_VALUE", "count"),
            missing=("OBS_VALUE", lambda series: series.isna().sum()),
        )
        .sort_values("rows", ascending=False)
    )

    result["missing_percentage"] = (
        result["missing"]
        / result["rows"]
        * 100
    ).round(2)

    print(result.to_string())


def main() -> None:
    """Run all dataset validation checks."""

    df = load_dataset()

    validate_estancia_media(df)
    analyze_missingness_by_year(df)
    analyze_missingness_by_nationality(df)
    identify_new_nationalities(df)
    analyze_observation_status(df)
    analyze_confidentiality(df)


if __name__ == "__main__":
    main()