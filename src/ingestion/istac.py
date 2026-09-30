from __future__ import annotations

import argparse
import hashlib
import json
import logging
import os
from datetime import UTC, datetime
from pathlib import Path

import requests
from dotenv import load_dotenv

LOGGER = logging.getLogger(__name__)

DEFAULT_BASE_URL = (
    "https://datos.canarias.es/api/estadisticas/"
    "statistical-resources/v1.0/datasets/ISTAC"
)

DEFAULT_DATASET_ID = "C00065A_000036"
DEFAULT_FORMAT = "csv"


def build_url(dataset_id: str, version: str, fmt: str, base_url: str) -> str:
    """Build the URL of an ISTAC statistical resource."""
    return f"{base_url.rstrip('/')}/{dataset_id}/{version}.{fmt}"


def get_latest_version(
    dataset_id: str,
    base_url: str,
    timeout: int = 30,
) -> str:
    """Return the latest available ISTAC dataset version."""
    url = f"{base_url.rstrip('/')}/{dataset_id}"

    LOGGER.info("Checking latest ISTAC version: %s", url)

    response = requests.get(
        url,
        params={"limit": 1000},
        timeout=timeout,
        headers={
            "Accept": "application/json",
            "User-Agent": "tenerife-data-intelligence/0.1",
        },
    )
    response.raise_for_status()

    payload = response.json()
    datasets = payload.get("dataset")

    if not isinstance(datasets, list) or not datasets:
        raise ValueError(
            f"No dataset versions found for {dataset_id}."
        )

    versions: list[tuple[tuple[int, ...], str]] = []

    for dataset in datasets:
        if not isinstance(dataset, dict):
            continue

        self_link = dataset.get("selfLink")

        if not isinstance(self_link, dict):
            continue

        href = self_link.get("href")

        if not isinstance(href, str):
            continue

        version = href.rstrip("/").rsplit("/", maxsplit=1)[-1]
        parts = version.split(".")

        if not parts or not all(part.isdigit() for part in parts):
            continue

        version_key = tuple(int(part) for part in parts)
        versions.append((version_key, version))

    if not versions:
        raise ValueError(
            f"No valid versions found for dataset {dataset_id}."
        )

    latest_version = max(
        versions,
        key=lambda item: item[0],
    )[1]

    LOGGER.info(
        "Latest ISTAC version detected: %s",
        latest_version,
    )

    return latest_version


def download_dataset(
    url: str,
    output_path: Path,
    timeout: int = 120,
) -> tuple[Path, str]:
    """
    Download a dataset and return its path and SHA-256 checksum.
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)

    LOGGER.info("Downloading %s", url)

    sha256 = hashlib.sha256()

    with requests.get(
        url,
        stream=True,
        timeout=timeout,
        headers={"User-Agent": "tenerife-data-intelligence/0.1"},
    ) as response:
        response.raise_for_status()

        with output_path.open("wb") as file_handle:
            for chunk in response.iter_content(chunk_size=1024 * 1024):
                if not chunk:
                    continue

                file_handle.write(chunk)
                sha256.update(chunk)

    checksum = sha256.hexdigest()

    LOGGER.info(
        "Saved %s (%d bytes)",
        output_path,
        output_path.stat().st_size,
    )
    LOGGER.info("SHA-256: %s", checksum)

    return output_path, checksum


def write_manifest(
    output_path: Path,
    dataset_id: str,
    version: str,
    fmt: str,
    url: str,
    checksum: str,
) -> Path:
    """Write metadata describing the downloaded dataset."""
    manifest_path = output_path.parent / "manifest.json"

    manifest = {
        "dataset_id": dataset_id,
        "version": version,
        "format": fmt,
        "source_url": url,
        "downloaded_at_utc": datetime.now(UTC).isoformat(),
        "file_name": output_path.name,
        "file_size_bytes": output_path.stat().st_size,
        "sha256": checksum,
    }

    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    LOGGER.info("Manifest saved to %s", manifest_path)

    return manifest_path

def ingest_dataset(
    dataset_id: str,
    version: str,
    fmt: str,
    raw_dir: str,
    base_url: str,
) -> tuple[Path, Path]:
    """Download an ISTAC dataset and return dataset and manifest paths."""
    url = build_url(
        dataset_id,
        version,
        fmt,
        base_url,
    )

    run_date = datetime.now(UTC).strftime("%Y-%m-%d")

    output = (
        Path(raw_dir)
        / "istac"
        / dataset_id
        / run_date
        / f"dataset.{fmt}"
    )

    downloaded_path, checksum = download_dataset(
        url,
        output,
    )

    manifest_path = write_manifest(
        downloaded_path,
        dataset_id=dataset_id,
        version=version,
        fmt=fmt,
        url=url,
        checksum=checksum,
    )

    return downloaded_path, manifest_path


def main() -> None:
    load_dotenv()

    parser = argparse.ArgumentParser(
        description="Download an ISTAC statistical cube"
    )

    parser.add_argument(
        "--dataset-id",
        default=os.getenv("ISTAC_DATASET_ID", DEFAULT_DATASET_ID),
    )

    parser.add_argument(
        "--version",
        default=None,
        help="ISTAC dataset version. If omitted, the latest version is detected automatically.",
    )

    parser.add_argument(
        "--format",
        dest="fmt",
        default=os.getenv("ISTAC_FORMAT", DEFAULT_FORMAT),
    )

    parser.add_argument(
        "--raw-dir",
        default=os.getenv("RAW_DIR", "data/raw"),
    )

    args = parser.parse_args()

    base_url = os.getenv(
        "ISTAC_BASE_URL",
        DEFAULT_BASE_URL,
    )

    version = (
        args.version
        or os.getenv("ISTAC_VERSION")
        or get_latest_version(
            dataset_id=args.dataset_id,
            base_url=base_url,
        )
    )

    dataset_path, manifest_path = ingest_dataset(
        dataset_id=args.dataset_id,
        version=version,
        fmt=args.fmt,
        raw_dir=args.raw_dir,
        base_url=base_url,
    )

    LOGGER.info("Dataset path: %s", dataset_path)
    LOGGER.info("Manifest path: %s", manifest_path)


if __name__ == "__main__":
    logging.basicConfig(
        level=os.getenv("LOG_LEVEL", "INFO"),
        format="%(asctime)s | %(levelname)s | %(message)s",
    )
    main()