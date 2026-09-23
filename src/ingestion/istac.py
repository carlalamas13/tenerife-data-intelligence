from __future__ import annotations

import argparse
import logging
import os
from datetime import datetime, timezone
from pathlib import Path

import requests
from dotenv import load_dotenv

LOGGER = logging.getLogger(__name__)


def build_url(dataset_id: str, version: str, fmt: str, base_url: str) -> str:
    return f"{base_url.rstrip('/')}/{dataset_id}/{version}.{fmt}"


def download_dataset(url: str, output_path: Path, timeout: int = 120) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    LOGGER.info("Downloading %s", url)

    with requests.get(url, stream=True, timeout=timeout, headers={"User-Agent": "tenderife-data-intelligence/0.1"}) as response:
        response.raise_for_status()
        with output_path.open("wb") as file_handle:
            for chunk in response.iter_content(chunk_size=1024 * 1024):
                if chunk:
                    file_handle.write(chunk)

    LOGGER.info("Saved %s (%d bytes)", output_path, output_path.stat().st_size)
    return output_path


def main() -> None:
    load_dotenv()

    parser = argparse.ArgumentParser(description="Download an ISTAC statistical cube")
    parser.add_argument("--dataset-id", default=os.getenv("ISTAC_DATASET_ID", "C00065A_000001"))
    parser.add_argument("--version", default=os.getenv("ISTAC_VERSION", "1.70"))
    parser.add_argument("--format", dest="fmt", default=os.getenv("ISTAC_FORMAT", "csv"))
    parser.add_argument("--raw-dir", default=os.getenv("RAW_DIR", "data/raw"))
    args = parser.parse_args()

    base_url = os.getenv(
        "ISTAC_BASE_URL",
        "https://datos.canarias.es/api/estadisticas/statistical-resources/v1.0/datasets/ISTAC",
    )

    url = build_url(args.dataset_id, args.version, args.fmt, base_url)
    run_date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    output = Path(args.raw_dir) / "istac" / args.dataset_id / run_date / f"dataset.{args.fmt}"

    download_dataset(url, output)


if __name__ == "__main__":
    logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"), format="%(asctime)s | %(levelname)s | %(message)s")
    main()
