"""
Quick smoke-test for the music_ai_module.

Run from the project root:
    python music_ai_module/example.py

No external API calls are made unless you pass --verify.
"""

import argparse
import os
import sys
from datetime import datetime

# Allow running from project root without installing the package
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from music_ai_module import (
    MusicAIPipeline,
    SystemConfig,
    StaticUserProfile,
    AppleWatchBiometrics,
)


def main(verify: bool = False) -> None:
    # ── User profile (one-time onboarding data) ──────────────────────────
    user = StaticUserProfile(
        occupation="software_engineer",
        age=28,
        height_cm=180,
        baseline_heart_rate=65,
        chronic_stress_sources=["work_deadline", "sleep_quality"],
        music_preference="minimalist_ambient",
    )

    # ── Simulated Apple Watch biometrics ─────────────────────────────────
    biometrics = AppleWatchBiometrics(
        timestamp=datetime.now(),
        heart_rate=102,               # elevated (baseline 65)
        heart_rate_variability=35.5,  # below 40 ms threshold → stressed
        respiratory_rate=18,          # borderline elevated
        environmental_audio_exposure=68,  # quiet-safe zone (<70 dB)
        body_motion={"x": 0.3, "y": 0.25, "z": 0.15},
        blood_oxygen=97.5,
        sleep_stage="awake",
    )

    # ── Pipeline ─────────────────────────────────────────────────────────
    config   = SystemConfig()          # reads env vars; falls back to defaults
    pipeline = MusicAIPipeline(config)

    result = pipeline.run(user, biometrics, verify=verify)
    MusicAIPipeline.describe(result)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="music_ai_module smoke test")
    parser.add_argument(
        "--verify",
        action="store_true",
        help="Send compiled prompt to LLM API for verification (~$0.0005)",
    )
    args = parser.parse_args()
    main(verify=args.verify)
