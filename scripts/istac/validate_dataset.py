from __future__ import annotations

from pathlib import Path

import pandas as pd

DATASET_CODE = "C00065A_000036"
DATA_ROOT = Path("data/raw/istac")

# Tenerife municipalities published in the cube. The rest of the island
# is aggregated in ES709_O ("Resto de Tenerife").
TENERIFE_MUNICIPALITY_CODES = (
    "38001",  # Adeje
    "38006",  # Arona
    "38017",  # Granadilla de Abona
    "38019",  # Guía de Isora
    "38023",  # San Cristóbal de La Laguna
    "38028",  # Puerto de la Cruz
    "38035",  # San Miguel de Abona
    "38038",  # Santa Cruz de Tenerife
    "38040",  # Santiago del Teide
)


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


def classify_missing_values(df: pd.DataFrame) -> pd.Series:
    """
    Classify each observation as:

        observed, not_available, confidential or not_published

    not_published means OBS_VALUE is missing without any status or
    confidentiality code.
    """

    missing = df["OBS_VALUE"].isna()
    not_available = df["ESTADO_OBSERVACION_CODE"].notna()
    confidential = df["CONFIDENCIALIDAD_OBSERVACION_CODE"].notna()

    status = pd.Series("observed", index=df.index)
    status[missing & not_available] = "not_available"
    status[missing & confidential] = "confidential"
    status[missing & ~not_available & ~confidential] = "not_published"

    return status


def analyze_not_published(df: pd.DataFrame) -> None:
    """
    Describe the observations that are missing without any status or
    confidentiality code.
    """

    data = df.copy()

    data["STATUS"] = classify_missing_values(data)
    data["GRANULARITY"] = (
        data["TIME_PERIOD_CODE"]
        .str.contains(r"-M\d{2}$", regex=True)
        .map({True: "monthly", False: "annual"})
    )
    data["YEAR"] = (
        data["TIME_PERIOD_CODE"]
        .astype(str)
        .str[:4]
        .astype(int)
    )

    print("\n=== OBSERVATION STATUS CLASSIFICATION ===")
    print(data["STATUS"].value_counts().to_string())

    not_published = data[data["STATUS"] == "not_published"]

    result = (
        not_published.groupby(
            ["NACIONALIDAD_CODE", "GRANULARITY"]
        )["YEAR"]
        .agg(
            rows="size",
            years=lambda years: sorted(years.unique()),
        )
    )

    print("\n=== NOT PUBLISHED OBSERVATIONS ===")
    print(result.to_string())

    rows_by_territory = (
        not_published["TERRITORIO_CODE"]
        .value_counts()
        .unique()
    )

    print(
        "Distinct row counts by territory:",
        rows_by_territory.tolist(),
    )


def _max_absolute_difference(
    total: pd.Series,
    parts: pd.DataFrame,
) -> tuple[int, float]:
    """
    Compare a total against the sum of its parts, ignoring rows where
    any value is missing.
    """

    comparison = pd.concat(
        [total.rename("TOTAL"), parts],
        axis=1,
    ).dropna()

    difference = (
        comparison["TOTAL"]
        - comparison.drop(columns="TOTAL").sum(axis=1)
    ).abs()

    return len(difference), float(difference.max())


def validate_nationality_hierarchy(df: pd.DataFrame) -> None:
    """
    Validate the nationality hierarchy on monthly additive measures:

        _T       = ES + 5000_XES
        5000_XES = sum of countries + 5000_XES_O
    """

    monthly = df[
        df["TIME_PERIOD_CODE"].str.contains(r"-M\d{2}$", regex=True)
        & df["MEDIDAS_CODE"].isin(
            ["PERNOCTACIONES", "VIAJEROS_ENTRADOS"]
        )
    ]

    pivot = monthly.pivot_table(
        index=["MEDIDAS_CODE", "TERRITORIO_CODE", "TIME_PERIOD_CODE"],
        columns="NACIONALIDAD_CODE",
        values="OBS_VALUE",
        aggfunc="first",
    )

    countries = [
        code
        for code in pivot.columns
        if code not in {"_T", "ES", "5000_XES", "5000_XES_O"}
    ]

    print("\n=== NATIONALITY HIERARCHY ===")

    checked, difference = _max_absolute_difference(
        pivot["_T"],
        pivot[["ES", "5000_XES"]],
    )
    print(
        f"_T = ES + 5000_XES -> checked: {checked}, "
        f"maximum difference: {difference}"
    )

    # Countries not published in a period are included in 5000_XES_O.
    parts = pivot[countries].fillna(0)
    parts["5000_XES_O"] = pivot["5000_XES_O"]

    checked, difference = _max_absolute_difference(
        pivot["5000_XES"],
        parts,
    )
    print(
        f"5000_XES = countries + 5000_XES_O -> checked: {checked}, "
        f"maximum difference: {difference}"
    )


def validate_territorial_hierarchy(
    df: pd.DataFrame,
    island_code: str = "ES709",
    municipality_codes: tuple[str, ...] = TENERIFE_MUNICIPALITY_CODES,
) -> None:
    """
    Validate that an island equals the sum of its published
    municipalities plus its residual territory (<island_code>_O).
    """

    residual_code = f"{island_code}_O"
    territories = [island_code, residual_code, *municipality_codes]

    missing_territories = set(territories) - set(df["TERRITORIO_CODE"])

    if missing_territories:
        print(
            f"\nTerritories not found: {sorted(missing_territories)}"
        )
        return

    island = df[
        df["TERRITORIO_CODE"].isin(territories)
        & df["TIME_PERIOD_CODE"].str.contains(r"-M\d{2}$", regex=True)
        & (df["NACIONALIDAD_CODE"] == "_T")
        & df["MEDIDAS_CODE"].isin(
            ["PERNOCTACIONES", "VIAJEROS_ENTRADOS"]
        )
    ]

    pivot = island.pivot_table(
        index=["MEDIDAS_CODE", "TIME_PERIOD_CODE"],
        columns="TERRITORIO_CODE",
        values="OBS_VALUE",
        aggfunc="first",
    )

    checked, difference = _max_absolute_difference(
        pivot[island_code],
        pivot[[*municipality_codes, residual_code]],
    )

    print(f"\n=== TERRITORIAL HIERARCHY ({island_code}) ===")
    print(f"Published municipalities: {len(municipality_codes)}")
    print(
        f"{island_code} = municipalities + {residual_code} -> "
        f"checked: {checked}, maximum difference: {difference}"
    )


def validate_annual_vs_monthly(df: pd.DataFrame) -> None:
    """
    Compare annual observations with the sum of their 12 monthly
    observations, by measure.
    """

    measures = [
        "PERNOCTACIONES",
        "VIAJEROS_ENTRADOS",
        "VIAJEROS_ALOJADOS",
    ]

    data = df[df["MEDIDAS_CODE"].isin(measures)].copy()
    data["YEAR"] = data["TIME_PERIOD_CODE"].astype(str).str[:4]
    is_monthly = data["TIME_PERIOD_CODE"].str.contains(
        r"-M\d{2}$",
        regex=True,
    )

    keys = [
        "MEDIDAS_CODE",
        "TERRITORIO_CODE",
        "NACIONALIDAD_CODE",
        "YEAR",
    ]

    monthly = (
        data[is_monthly]
        .groupby(keys)["OBS_VALUE"]
        .agg(monthly_sum="sum", monthly_values="count")
    )

    annual = (
        data[~is_monthly]
        .set_index(keys)["OBS_VALUE"]
        .rename("annual")
    )

    comparison = monthly.join(annual, how="inner").dropna(
        subset=["annual"]
    )
    comparison = comparison[comparison["monthly_values"] == 12].copy()

    comparison["mismatch"] = (
        comparison["annual"] - comparison["monthly_sum"]
    ).abs() > 0.5

    print("\n=== ANNUAL VS SUM OF MONTHS ===")
    print(
        comparison.groupby("MEDIDAS_CODE")["mismatch"]
        .agg(checked="size", mismatches="sum")
        .to_string()
    )

    additive_mismatches = (
        comparison[comparison["mismatch"]]
        .reset_index()
        .query("MEDIDAS_CODE != 'VIAJEROS_ALOJADOS'")
        .groupby(["NACIONALIDAD_CODE", "YEAR"])
        .size()
    )

    print("\nMismatches in additive measures:")
    print(additive_mismatches.to_string())


def main() -> None:
    """Run all dataset validation checks."""

    df = load_dataset()

    validate_estancia_media(df)
    analyze_missingness_by_year(df)
    analyze_missingness_by_nationality(df)
    identify_new_nationalities(df)
    analyze_observation_status(df)
    analyze_confidentiality(df)
    analyze_not_published(df)
    validate_nationality_hierarchy(df)
    validate_territorial_hierarchy(df)
    validate_annual_vs_monthly(df)


if __name__ == "__main__":
    main()