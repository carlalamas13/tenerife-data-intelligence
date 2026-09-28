import pandas as pd
import pytest

from src.quality.istac import (
    classify_observation_status,
    max_absolute_difference,
)


def test_classify_observation_status() -> None:
    df = pd.DataFrame(
        {
            "OBS_VALUE": [10.0, None, None, None],
            "ESTADO_OBSERVACION_CODE": [None, "O", None, None],
            "CONFIDENCIALIDAD_OBSERVACION_CODE": [
                None,
                None,
                "C",
                None,
            ],
        }
    )

    result = classify_observation_status(df)

    assert result.tolist() == [
        "observed",
        "not_available",
        "confidential",
        "not_published",
    ]


def test_classify_observation_status_requires_columns() -> None:
    df = pd.DataFrame(
        {
            "OBS_VALUE": [10.0],
        }
    )

    with pytest.raises(ValueError):
        classify_observation_status(df)


def test_max_absolute_difference() -> None:
    total = pd.Series([10.0, 20.0, 30.0])

    parts = pd.DataFrame(
        {
            "PART_A": [4.0, 10.0, 15.0],
            "PART_B": [6.0, 9.0, 14.0],
        }
    )

    checked, difference = max_absolute_difference(total, parts)

    assert checked == 3
    assert difference == 1.0


def test_max_absolute_difference_ignores_missing_values() -> None:
    total = pd.Series([10.0, None, 30.0])

    parts = pd.DataFrame(
        {
            "PART_A": [4.0, 10.0, 15.0],
            "PART_B": [6.0, 9.0, None],
        }
    )

    checked, difference = max_absolute_difference(total, parts)

    assert checked == 1
    assert difference == 0.0


def test_max_absolute_difference_with_no_complete_rows() -> None:
    total = pd.Series([None])

    parts = pd.DataFrame(
        {
            "PART_A": [None],
            "PART_B": [None],
        }
    )

    checked, difference = max_absolute_difference(total, parts)

    assert checked == 0
    assert pd.isna(difference)