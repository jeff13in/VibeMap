"""
SCRUM-35: Master Pipeline Script

Goal:
- Run the entire VibeMap pipeline end-to-end with ONE command
- Execute steps in order
- Use the active venv interpreter (sys.executable)
- Fail fast with clear errors
- Always run from project root so paths stay consistent

SCRUM-37:
- Add clear progress indicators for each step (start/end/fail)
- Optional timing per step for visibility

Run:
    python run_pipeline.py

Optional:
    python run_pipeline.py --skip-generate
    python run_pipeline.py --skip-eda
    python run_pipeline.py --only recommender
"""

from __future__ import annotations

import argparse
import subprocess
import sys
import time
from pathlib import Path


# -----------------------------
# Paths / config
# -----------------------------
PROJECT_ROOT = Path(__file__).resolve().parent

# Expected artifacts (used for basic sanity checks)
CLEANED_CSV = PROJECT_ROOT / "cleaned_spotify_data.csv"
RAW_CSV = PROJECT_ROOT / "songs_with_audio_features.csv"
DB_FILE = PROJECT_ROOT / "spotify_data.db"


# -----------------------------
# Helpers
# -----------------------------
def _banner(title: str) -> None:
    line = "=" * 60
    print(f"\n{line}\n{title}\n{line}")


def run_step(script_name: str) -> None:
    """
    Run a python script as a subprocess using the current interpreter.
    Ensures:
      - correct working directory (PROJECT_ROOT)
      - fail-fast behavior on non-zero exit code
      - clear progress framing for SCRUM-37
    """
    script_path = PROJECT_ROOT / script_name
    if not script_path.exists():
        raise FileNotFoundError(f"Missing script: {script_path}")

    _banner(f"▶ START: {script_name}")
    print(f"cwd    : {PROJECT_ROOT}")
    print(f"python : {sys.executable}\n")

    start = time.perf_counter()

    # Run script and stream output directly to terminal
    result = subprocess.run(
        [sys.executable, str(script_path)],
        cwd=str(PROJECT_ROOT),
        check=False,
    )

    elapsed = time.perf_counter() - start

    if result.returncode != 0:
        _banner(f"❌ FAIL: {script_name}")
        raise RuntimeError(
            f"Pipeline failed at '{script_name}' (exit code {result.returncode})"
        )

    _banner(f"✅ DONE: {script_name}  (took {elapsed:.2f}s)")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the VibeMap pipeline end-to-end.")
    parser.add_argument(
        "--skip-generate",
        action="store_true",
        help="Skip data_generator.py (use existing raw CSV/DB if present).",
    )
    parser.add_argument(
        "--skip-eda",
        action="store_true",
        help="Skip exploratory_analysis.py.",
    )
    parser.add_argument(
        "--only",
        choices=["generate", "clean", "eda", "cluster", "recommender"],
        help="Run only a single step.",
    )
    return parser.parse_args()


# -----------------------------
# Main pipeline
# -----------------------------
def main() -> None:
    args = parse_args()

    steps = [
        ("generate", "data_generator.py"),
        ("clean", "data_cleaner.py"),
        ("eda", "exploratory_analysis.py"),
        ("cluster", "clustering.py"),
        ("recommender", "recommender.py"),
    ]

    # Handle --only
    if args.only:
        mapping = {k: v for k, v in steps}
        _banner("🚀 VibeMap Master Pipeline (single step)")
        run_step(mapping[args.only])
        print("\n🎉 Done (single step).")
        return

    # Optional skipping behavior
    pipeline_scripts: list[str] = []

    if args.skip_generate:
        print("\nℹ️ Skipping data generation step (--skip-generate).")
        if not RAW_CSV.exists() and not DB_FILE.exists():
            print(
                f"⚠️ Warning: '{RAW_CSV.name}' and '{DB_FILE.name}' not found. "
                "Data cleaning may fail if it expects raw inputs."
            )
    else:
        pipeline_scripts.append("data_generator.py")

    pipeline_scripts.append("data_cleaner.py")

    if args.skip_eda:
        print("\nℹ️ Skipping EDA step (--skip-eda).")
    else:
        pipeline_scripts.append("exploratory_analysis.py")

    pipeline_scripts.append("clustering.py")
    pipeline_scripts.append("recommender.py")

    _banner("🚀 VibeMap Master Pipeline")
    print(f"Project root: {PROJECT_ROOT}")
    print(f"Using python: {sys.executable}")
    print("Steps to run:")
    for s in pipeline_scripts:
        print(f"  - {s}")

    # Run steps in order
    for script in pipeline_scripts:
        run_step(script)

    # Post-check: cleaned dataset should exist after cleaning
    if CLEANED_CSV.exists():
        print(f"\n✅ Output check: found {CLEANED_CSV.name}")
    else:
        print(
            f"\n⚠️ Output check: {CLEANED_CSV.name} not found "
            "(data_cleaner may not have produced it)."
        )

    print("\n🎉 Pipeline complete!")


if __name__ == "__main__":
    main()
