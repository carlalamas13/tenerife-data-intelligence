from __future__ import annotations

import pandas as pd

REQUIRED_STATUS_COLUMNS = {
    "OBS_VALUE",
    "ESTADO_OBSERVACION_CODE",
    "CONFIDENCIALIDAD_OBSERVACION_CODE",
}


def classify_observation_status(df: pd.DataFrame) -> pd.Series:
    """
    Classify each observation according to its published status.

    Possible values are:
        observed
        not_published
        not_available
        confidential
    """
    missing_columns = REQUIRED_STATUS_COLUMNS - set(df.columns)

    if missing_columns:
        raise ValueError(
            f"Required columns are missing: {sorted(missing_columns)}"
        )

    missing = df["OBS_VALUE"].isna()
    not_available = df["ESTADO_OBSERVACION_CODE"].notna()
    confidential = df["CONFIDENCIALIDAD_OBSERVACION_CODE"].notna()

    status = pd.Series("observed", index=df.index, dtype="string")

    status.loc[missing & not_available] = "not_available"
    status.loc[missing & confidential] = "confidential"
    status.loc[missing & ~not_available & ~confidential] = "not_published"

    return status


def max_absolute_difference(
    total: pd.Series,
    parts: pd.DataFrame,
) -> tuple[int, float]:
    """
    Compare a total against the sum of its parts.

    Rows with missing values are excluded from the comparison.

    Returns:
        Number of checked rows and maximum absolute difference.
    """
    comparison = pd.concat(
        [total.rename("TOTAL"), parts],
        axis=1,
    ).dropna()

    if comparison.empty:
        return 0, float("nan")

    difference = (
        comparison["TOTAL"]
        - comparison.drop(columns="TOTAL").sum(axis=1)
    ).abs()

    return len(difference), float(difference.max())