from __future__ import annotations

import argparse
import logging
import subprocess
import sys
from pathlib import Path

from scripts.istac.validate_dataset import find_dataset

LOGGER = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DBT_PROJECT_DIR = PROJECT_ROOT / "dbt" / "tenerife_dbt"


def run_command(command: list[str], description: str, cwd: Path) -> None:
    """Run a command and stop the pipeline if it fails."""
    LOGGER.info("%s", description)

    subprocess.run(
        command,
        cwd=cwd,
        check=True,
    )


def main() -> None:
    """Run the complete ISTAC ingestion pipeline."""

    parser = argparse.ArgumentParser(
        description="Run the complete ISTAC ingestion pipeline."
    )

    parser.add_argument(
        "--version",
        required=True,
        help="ISTAC dataset version to ingest.",
    )

    args = parser.parse_args()

    # Step 1: download the dataset and generate its manifest.
    run_command(
        [
            sys.executable,
            "-m",
            "src.ingestion.istac",
            "--version",
            args.version,
        ],
        "Step 1/4: downloading ISTAC dataset.",
        PROJECT_ROOT,
    )

    # Step 2: identify the dataset just downloaded.
    dataset_path = find_dataset()
    manifest_path = dataset_path.parent / "manifest.json"

    LOGGER.info("Dataset selected: %s", dataset_path)
    LOGGER.info("Manifest selected: %s", manifest_path)

    # Step 3: run the quality gate against the exact snapshot.
    run_command(
        [
            sys.executable,
            "-m",
            "scripts.istac.validate_dataset",
            "--dataset",
            str(dataset_path),
        ],
        "Step 2/4: running ISTAC quality gate.",
        PROJECT_ROOT,
    )

    # Step 4: load the validated snapshot into RAW.
    run_command(
        [
            sys.executable,
            "scripts/istac/load_raw.py",
            "--manifest",
            str(manifest_path),
        ],
        "Step 3/4: loading validated snapshot into RAW.",
        PROJECT_ROOT,
    )

    # Step 5: rebuild all dbt models and tests.
    run_command(
        [
            "dbt",
            "build",
        ],
        "Step 4/4: running dbt build.",
        DBT_PROJECT_DIR,
    )

    LOGGER.info("ISTAC pipeline completed successfully.")


if __name__ == "__main__":
    logging.basicConfig(
        level="INFO",
        format="%(asctime)s | %(levelname)s | %(message)s",
    )
    main()