from pathlib import Path

import pandas as pd


DATASET_CODE = "C00065A_000036"
DATA_ROOT = Path("data/raw/istac")


def find_dataset() -> Path:
    dataset_root = DATA_ROOT / DATASET_CODE

    datasets = list(dataset_root.glob("*/dataset.csv"))

    if not datasets:
        raise FileNotFoundError(
            f"No se ha encontrado dataset.csv en {dataset_root}"
        )

    return max(datasets, key=lambda path: path.stat().st_mtime)


def load_dataset() -> pd.DataFrame:
    path = find_dataset()

    print(f"Cargando: {path}")

    return pd.read_csv(
        path,
        low_memory=False,
    )


def validate_estancia_media(df: pd.DataFrame) -> None:
    """
    Comprueba que ESTANCIA_MEDIA coincide con:

        PERNOCTACIONES / VIAJEROS_ENTRADOS

    para observaciones mensuales con datos disponibles.
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
            f"Faltan columnas necesarias: {sorted(missing_columns)}"
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
            "No hay suficientes medidas para validar ESTANCIA_MEDIA."
        )
        return

    valid = pivot.dropna(
        subset=[
            "VIAJEROS_ENTRADOS",
            "PERNOCTACIONES",
            "ESTANCIA_MEDIA",
        ]
    ).copy()

    valid["ESTANCIA_MEDIA_CALCULADA"] = (
        valid["PERNOCTACIONES"]
        / valid["VIAJEROS_ENTRADOS"]
    )

    valid["DIFERENCIA"] = (
        valid["ESTANCIA_MEDIA"]
        - valid["ESTANCIA_MEDIA_CALCULADA"]
    ).abs()

    print("\n=== VALIDACIÓN ESTANCIA_MEDIA ===")
    print(f"Observaciones válidas: {len(valid)}")

    if valid.empty:
        print("No hay observaciones suficientes.")
        return

    print(
        "Diferencia máxima:",
        valid["DIFERENCIA"].max(),
    )

    tolerance = 1e-9

    invalid = valid[
        valid["DIFERENCIA"] > tolerance
    ]

    print(
        f"Observaciones fuera de tolerancia "
        f"({tolerance}): {len(invalid)}"
    )

    if len(invalid) > 0:
        print("\nPrimeras discrepancias:")
        print(
            invalid[
                [
                    "TIME_PERIOD_CODE",
                    "VIAJEROS_ENTRADOS",
                    "PERNOCTACIONES",
                    "ESTANCIA_MEDIA",
                    "ESTANCIA_MEDIA_CALCULADA",
                    "DIFERENCIA",
                ]
            ]
            .head(20)
            .to_string(index=False)
        )


def analyze_missingness_by_year(df: pd.DataFrame) -> None:
    """
    Analiza la cobertura de OBS_VALUE por año.
    """

    data = df.copy()

    data["ANIO"] = (
        data["TIME_PERIOD_CODE"]
        .astype(str)
        .str[:4]
    )

    result = (
        data.groupby("ANIO")["OBS_VALUE"]
        .agg(
            filas="size",
            valores="count",
            nulos=lambda series: series.isna().sum(),
        )
    )

    result["porcentaje_con_dato"] = (
        result["valores"]
        / result["filas"]
        * 100
    ).round(2)

    print("\n=== COBERTURA POR AÑO ===")
    print(result.to_string())


def analyze_missingness_by_nationality(
    df: pd.DataFrame,
) -> None:
    """
    Analiza la cobertura de OBS_VALUE por nacionalidad y año.
    """

    data = df.copy()

    data["ANIO"] = (
        data["TIME_PERIOD_CODE"]
        .astype(str)
        .str[:4]
    )

    result = (
        data.groupby(
            ["NACIONALIDAD_CODE", "ANIO"]
        )["OBS_VALUE"]
        .count()
        .unstack(fill_value=0)
    )

    print("\n=== OBSERVACIONES POR NACIONALIDAD Y AÑO ===")
    print(result.to_string())


def main() -> None:
    df = load_dataset()

    validate_estancia_media(df)
    analyze_missingness_by_year(df)
    analyze_missingness_by_nationality(df)


if __name__ == "__main__":
    main()