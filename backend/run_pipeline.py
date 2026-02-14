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
- Timing per step for visibility (SCRUM-41)

SCRUM-40:
- Error handling with clear messages at the top level

SCRUM-43:
- Summary of generated outputs (datasets / db / models / figures)
- Persist summary to notebooks/figures/outputsummary.txt

SCRUM-44:
- Verification of required file creation (fail if missing)

SCRUM-45:
- Helpful next steps displayed at end

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

# Expected artifacts (used for basic sanity checks + summary)
CLEANED_CSV = PROJECT_ROOT / "cleaned_spotify_data.csv"
RAW_CSV = PROJECT_ROOT / "songs_with_audio_features.csv"
DB_FILE = PROJECT_ROOT / "spotify_data.db"

MODELS_DIR = PROJECT_ROOT / "models"
FIGURES_DIR = PROJECT_ROOT / "notebooks" / "figures"

SUMMARY_TXT = FIGURES_DIR / "outputsummary.txt"

# SCRUM-44: required outputs (pipeline must create these)
REQUIRED_OUTPUTS = {
    "Cleaned dataset": CLEANED_CSV,
    "Output summary": SUMMARY_TXT,
}


# -----------------------------
# Helpers
# -----------------------------
def _banner(title: str) -> None:
    line = "=" * 60
    print(f"\n{line}\n{title}\n{line}")


def _fmt_bytes(n: int) -> str:
    """Human-readable file sizes."""
    size = float(n)
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if size < 1024:
            return f"{size:.0f}{unit}"
        size /= 1024
    return f"{size:.1f}PB"


def _file_line(label: str, path: Path) -> str:
    """Return a single status line for a file."""
    if path.exists():
        size = _fmt_bytes(path.stat().st_size)
        return f"✅ {label}: {path.name} ({size})  →  {path}"
    return f"❌ {label}: NOT FOUND  →  {path}"


def _dir_summary(label: str, dir_path: Path, pattern: str = "*") -> str:
    """Return a single status line for a folder + matching file count."""
    if not dir_path.exists():
        return f"❌ {label}: folder not found  →  {dir_path}"
    files = sorted(dir_path.glob(pattern))
    if not files:
        return f"⚠️  {label}: no files found  →  {dir_path}"
    return f"✅ {label}: {len(files)} file(s)  →  {dir_path}"


def run_step(script_name: str) -> None:
    """
    Run a python script as a subprocess using the current interpreter.
    Ensures:
      - correct working directory (PROJECT_ROOT)
      - fail-fast behavior on non-zero exit code
      - clear progress framing (SCRUM-37)
      - step timing (SCRUM-41)
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
# SCRUM-43 summary builders
# -----------------------------
def build_output_summary_lines() -> list[str]:
    """Build SCRUM-43 output summary as a list of text lines."""
    lines: list[str] = []
    lines.append("=" * 60)
    lines.append("📦 OUTPUT SUMMARY (SCRUM-43)")
    lines.append("=" * 60)

    # Core outputs
    lines.append(_file_line("Cleaned dataset", CLEANED_CSV))
    lines.append(_file_line("Raw dataset (csv)", RAW_CSV))
    lines.append(_file_line("SQLite database", DB_FILE))

    # Common output folders
    lines.append(_dir_summary("Models folder", MODELS_DIR))
    lines.append(_dir_summary("Figures folder", FIGURES_DIR))

    # Model artifacts
    lines.append("")  # blank line
    lines.append("Model artifacts:")
    if MODELS_DIR.exists():
        model_files = sorted(MODELS_DIR.glob("*.pkl"))
        if model_files:
            for f in model_files:
                lines.append(f"  - {f.name} ({_fmt_bytes(f.stat().st_size)})")
        else:
            lines.append("  - none")
    else:
        lines.append("  - models folder not found")

    # Figure artifacts
    lines.append("")  # blank line
    lines.append("Figure artifacts:")
    if FIGURES_DIR.exists():
        fig_files = sorted(list(FIGURES_DIR.glob("*.png")) + list(FIGURES_DIR.glob("*.jpg")))
        if fig_files:
            for f in fig_files[:10]:
                lines.append(f"  - {f.name} ({_fmt_bytes(f.stat().st_size)})")
            if len(fig_files) > 10:
                lines.append(f"  ... and {len(fig_files) - 10} more")
        else:
            lines.append("  - none")
    else:
        lines.append("  - figures folder not found")

    return lines


def print_output_summary() -> None:
    """Print SCRUM-43 output summary to terminal."""
    for line in build_output_summary_lines():
        print(line)


def write_output_summary_txt() -> None:
    """Write SCRUM-43 output summary to notebooks/figures/outputsummary.txt."""
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    content = "\n".join(build_output_summary_lines())
    SUMMARY_TXT.write_text(content, encoding="utf-8")


# -----------------------------
# SCRUM-44 verification
# -----------------------------
def verify_required_outputs() -> None:
    """
    Verify that required pipeline outputs exist.
    Fail the pipeline if any are missing.
    """
    missing: list[str] = []
    for label, path in REQUIRED_OUTPUTS.items():
        if not path.exists():
            missing.append(f"- {label}: {path}")

    if missing:
        _banner("❌ OUTPUT VERIFICATION FAILED (SCRUM-44)")
        print("The following required outputs are missing:")
        for m in missing:
            print(m)
        raise RuntimeError("Required pipeline outputs were not created")

    _banner("✅ OUTPUT VERIFICATION PASSED (SCRUM-44)")


# -----------------------------
# SCRUM-45 next steps
# -----------------------------
def print_next_steps() -> None:
    """Print helpful next steps after pipeline completion."""
    _banner("➡️  NEXT STEPS (SCRUM-45)")

    print("Here’s what you can do next:\n")

    print("1️⃣ Review generated outputs:")
    print(f"   - Cleaned dataset: {CLEANED_CSV}")
    print(f"   - Output summary: {SUMMARY_TXT}")
    print(f"   - Models folder:  {MODELS_DIR}")
    print(f"   - Figures folder: {FIGURES_DIR}\n")

    print("2️⃣ Explore results:")
    print("   - Open notebooks/figures to review EDA plots")
    print("   - Inspect outputsummary.txt for a run receipt\n")

    print("3️⃣ Use the recommender:")
    print("   - Run: python recommender.py")
    print("   - Integrate results into the VibeMap website module\n")

    print("4️⃣ Re-run specific stages if needed:")
    print("   - Only recommender: python run_pipeline.py --only recommender")
    print("   - Skip data generation: python run_pipeline.py --skip-generate")
    print("   - Skip EDA: python run_pipeline.py --skip-eda\n")

    print("5️⃣ Debugging tips:")
    print("   - If a step failed, scroll up to the ❌ FAIL banner")
    print("   - Verify required files exist for skipped steps")


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

        _banner("📦 OUTPUT SUMMARY (SCRUM-43)")
        print_output_summary()
        write_output_summary_txt()
        print(f"\n📝 Output summary saved to: {SUMMARY_TXT}")

        verify_required_outputs()
        print_next_steps()

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

    # SCRUM-43: Summary of generated outputs + persist to txt
    _banner("📦 OUTPUT SUMMARY (SCRUM-43)")
    print_output_summary()
    write_output_summary_txt()
    print(f"\n📝 Output summary saved to: {SUMMARY_TXT}")

    # SCRUM-44: verify required outputs exist
    verify_required_outputs()

    # SCRUM-45: show helpful next steps
    print_next_steps()

    print("\n🎉 Pipeline complete!")


if __name__ == "__main__":
    # SCRUM-40: top-level error handling with clear message
    try:
        main()
    except Exception as e:
        print("\n" + "=" * 60)
        print("❌ PIPELINE FAILED")
        print("=" * 60)
        print(f"Error: {type(e).__name__}: {e}")
        print("\nTip: Scroll up to see which step failed (▶ START / ❌ FAIL).")
        sys.exit(1)
