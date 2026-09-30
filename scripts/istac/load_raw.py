from __future__ import annotations

import argparse
import hashlib
import json
import logging
import subprocess
from pathlib import Path

LOGGER = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_ROOT = PROJECT_ROOT / "data"
SQL_FILE = PROJECT_ROOT / "sql" / "02_load_raw_istac.sql"

EXPECTED_DATASET_ID = "C00065A_000036"


def calculate_sha256(file_path: Path) -> str:
    """Calculate the SHA-256 checksum of a file."""
    sha256 = hashlib.sha256()

    with file_path.open("rb") as file_handle:
        for chunk in iter(lambda: file_handle.read(1024 * 1024), b""):
            sha256.update(chunk)

    return sha256.hexdigest()


def load_manifest(manifest_path: Path) -> dict:
    """Load and validate the ingestion manifest."""
    manifest_path = manifest_path.resolve()

    if not manifest_path.is_file():
        raise FileNotFoundError(f"Manifest not found: {manifest_path}")

    if DATA_ROOT not in manifest_path.parents:
        raise ValueError("Manifest must be located under the data directory.")

    with manifest_path.open(encoding="utf-8") as file_handle:
        manifest = json.load(file_handle)

    required_fields = {
        "dataset_id",
        "version",
        "format",
        "source_url",
        "file_name",
        "file_size_bytes",
        "sha256",
    }

    missing_fields = required_fields - manifest.keys()

    if missing_fields:
        raise ValueError(
            f"Manifest is missing required fields: {sorted(missing_fields)}"
        )

    if manifest["dataset_id"] != EXPECTED_DATASET_ID:
        raise ValueError(
            f"Unsupported dataset: {manifest['dataset_id']}. "
            f"Expected {EXPECTED_DATASET_ID}."
        )

    if manifest["format"] != "csv":
        raise ValueError(
            f"Unsupported format: {manifest['format']}. Expected csv."
        )

    return manifest


def resolve_csv_path(manifest_path: Path, manifest: dict) -> Path:
    """Resolve the CSV path referenced by the manifest."""
    csv_path = (manifest_path.parent / manifest["file_name"]).resolve()

    if not csv_path.is_file():
        raise FileNotFoundError(f"CSV file not found: {csv_path}")

    if DATA_ROOT not in csv_path.parents:
        raise ValueError("CSV file must be located under the data directory.")

    return csv_path


def validate_source(csv_path: Path, manifest: dict) -> None:
    """Validate file size and SHA-256 against the manifest."""
    actual_size = csv_path.stat().st_size
    expected_size = int(manifest["file_size_bytes"])

    if actual_size != expected_size:
        raise ValueError(
            f"File size mismatch: expected {expected_size}, "
            f"got {actual_size}."
        )

    actual_sha256 = calculate_sha256(csv_path)
    expected_sha256 = manifest["sha256"]

    if actual_sha256 != expected_sha256:
        raise ValueError(
            f"SHA-256 mismatch: expected {expected_sha256}, "
            f"got {actual_sha256}."
        )

    LOGGER.info("Source validation passed.")
    LOGGER.info("File size: %d bytes", actual_size)
    LOGGER.info("SHA-256: %s", actual_sha256)


def build_container_path(csv_path: Path) -> str:
    """Map a host data path to the Docker /data mount."""
    relative_path = csv_path.relative_to(DATA_ROOT)
    return f"/data/{relative_path.as_posix()}"


def run_loader(manifest_path: Path, manifest: dict, csv_path: Path) -> None:
    """Execute the generic PostgreSQL RAW loader."""
    container_csv_path = build_container_path(csv_path)

    ingestion_date = manifest.get("downloaded_at_utc", "")[:10]

    if not ingestion_date:
        raise ValueError("Manifest does not contain downloaded_at_utc.")

    command = [
        "docker",
        "compose",
        "exec",
        "-T",
        "postgres",
        "psql",
        "-U",
        "tenerife",
        "-d",
        "tenerife",
        "-v",
        "ON_ERROR_STOP=1",
        "-v",
        f"csv_file={container_csv_path}",
        "-v",
        f"dataset_code={manifest['dataset_id']}",
        "-v",
        f"source_version={manifest['version']}",
        "-v",
        f"snapshot_date={ingestion_date}",
        "-v",
        f"source_url={manifest['source_url']}",
        "-v",
        f"source_sha256={manifest['sha256']}",
        "-v",
        f"source_file_size_bytes={manifest['file_size_bytes']}",
        "-v",
        f"source_file_name={manifest['file_name']}",
        "-f",
        "/sql/02_load_raw_istac.sql",
    ]

    LOGGER.info(
        "Loading dataset %s version %s into RAW.",
        manifest["dataset_id"],
        manifest["version"],
    )

    subprocess.run(
        command,
        cwd=PROJECT_ROOT,
        check=True,
    )

    LOGGER.info("RAW load completed successfully.")
    LOGGER.info("Manifest: %s", manifest_path)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Load an ISTAC manifest into the PostgreSQL RAW layer."
    )

    parser.add_argument(
        "--manifest",
        type=Path,
        required=True,
        help="Path to the ISTAC ingestion manifest.",
    )

    args = parser.parse_args()

    manifest_path = args.manifest.resolve()
    manifest = load_manifest(manifest_path)
    csv_path = resolve_csv_path(manifest_path, manifest)

    validate_source(csv_path, manifest)
    run_loader(manifest_path, manifest, csv_path)


if __name__ == "__main__":
    logging.basicConfig(
        level="INFO",
        format="%(asctime)s | %(levelname)s | %(message)s",
    )
    main()