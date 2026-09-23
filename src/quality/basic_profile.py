from __future__ import annotations

import json
from pathlib import Path

import pandas as pd


def profile_csv(path: str | Path) -> dict:
    df = pd.read_csv(path, low_memory=False)
    return {
        "rows": len(df),
        "columns": len(df.columns),
        "column_names": list(df.columns),
        "null_counts": df.isna().sum().to_dict(),
        "duplicate_rows": int(df.duplicated().sum()),
        "dtypes": {column: str(dtype) for column, dtype in df.dtypes.items()},
    }


def save_profile(path: str | Path, profile: dict) -> None:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(profile, ensure_ascii=False, indent=2), encoding="utf-8")
