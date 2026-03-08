"""
Main Pipeline — end-to-end orchestration of all three layers.

Usage (minimal)
---------------
    from music_ai_module.pipeline import MusicAIPipeline
    from music_ai_module.models import StaticUserProfile, AppleWatchBiometrics
    from datetime import datetime

    pipeline = MusicAIPipeline()

    user = StaticUserProfile(
        occupation="software_engineer",
        age=28,
        height_cm=180,
        baseline_heart_rate=65,
        chronic_stress_sources=["work_deadline"],
        music_preference="minimalist_ambient",
    )

    biometrics = AppleWatchBiometrics(
        timestamp=datetime.now(),
        heart_rate=102,
        heart_rate_variability=35.5,
        respiratory_rate=18,
        environmental_audio_exposure=68,
        body_motion={"x": 0.3, "y": 0.25, "z": 0.15},
        blood_oxygen=97.5,
        sleep_stage="awake",
    )

    result = pipeline.run(user, biometrics)
    print(result["prompt"])          # → final music generation prompt
    print(result["processed_params"]) # → Layer-2 acoustic parameters
"""

from __future__ import annotations

from typing import Dict, Optional

from .compiler import MusicPromptCompiler
from .config import SystemConfig, default_config
from .models import AppleWatchBiometrics, StaticUserProfile
from .processor import BiometricProcessor


class MusicAIPipeline:
    """
    Orchestrates Layer 1 → Layer 2 → Layer 3.

    Parameters
    ----------
    config : SystemConfig instance.  Defaults to the module-level
             ``default_config`` (reads environment variables at import time).

    Methods
    -------
    run(profile, biometrics, verify=False)
        Execute the full pipeline for a single biometric reading.
        Returns a flat result dict containing all intermediate and final outputs.
    """

    def __init__(self, config: SystemConfig = default_config) -> None:
        self.config    = config
        self.processor = BiometricProcessor(config)
        self.compiler  = MusicPromptCompiler(config)

    # ------------------------------------------------------------------
    # Primary entry point
    # ------------------------------------------------------------------

    def run(
        self,
        profile: StaticUserProfile,
        biometrics: AppleWatchBiometrics,
        verify: bool = False,
    ) -> Dict:
        """
        Execute the full pipeline.

        Pipeline steps
        ~~~~~~~~~~~~~~
        1. Validate biometric sensor data (Layer 1).
        2. Map biometrics to acoustic parameters (Layer 2).
        3. Compile 7-segment music generation prompt (Layer 3).
        4. Optionally verify prompt via LLM endpoint.

        Parameters
        ----------
        profile    : Static user profile.
        biometrics : Real-time Apple Watch snapshot.
        verify     : Forward compiled prompt to LLM for a completeness check.

        Returns
        -------
        {
            "prompt":           str,   # final music generation prompt
            "segments":         dict,  # individual prompt segments
            "metadata":         dict,  # token estimates, cost, validation
            "processed_params": dict,  # Layer-2 acoustic parameters
            "validation_errors": list, # sensor validation issues (empty = OK)
            # present when verify=True:
            "verified_prompt":      str,
            "verification_status":  str,
        }

        Raises
        ------
        ValueError
            If biometric validation fails with critical out-of-range values.
        """
        # ── Step 1: Layer-1 validation ──────────────────────────────────
        errors = biometrics.validate()
        if errors:
            # Log warnings but do not abort — use last valid reading in processor
            for err in errors:
                print(f"[WARN] Biometric validation: {err}")

        # ── Step 2: Layer-2 processing ──────────────────────────────────
        processed = self.processor.process(profile, biometrics)

        # ── Step 3 + 4: Layer-3 compilation (+ optional verification) ──
        compiled = self.compiler.compile(profile, processed, verify=verify)

        return {
            **compiled,
            "processed_params":  processed,
            "validation_errors": errors,
        }

    # ------------------------------------------------------------------
    # Convenience: pretty-print a result
    # ------------------------------------------------------------------

    @staticmethod
    def describe(result: Dict) -> None:
        """Print a human-readable summary of a pipeline result."""
        sep = "=" * 70

        print(f"\n{sep}")
        print("COMPILED MUSIC GENERATION PROMPT")
        print(sep)
        print(f"\n{result['prompt']}\n")

        print(sep)
        print("SEGMENT BREAKDOWN")
        print(sep)
        for name, content in result["segments"].items():
            print(f"\n[{name.upper()}]\n{content}\n")

        print(sep)
        print("ACOUSTIC PARAMETERS (Layer 2 output)")
        print(sep)
        rhythm    = result["processed_params"]["rhythm"]
        texture   = result["processed_params"]["texture"]
        breathing = result["processed_params"]["breathing"]
        safeguard = result["processed_params"]["safeguards"]
        print(f"  Target BPM        : {rhythm['target_bpm']}")
        print(f"  Sympathetic Load  : +{rhythm['sympathetic_load']} BPM above baseline")
        print(f"  HRV Status        : {texture['hrv_status']}")
        print(f"  Pink Noise        : {texture['apply_pink_noise']}")
        print(f"  Breathing Status  : {breathing['respiratory_status']}")
        print(f"  Environment       : {safeguard['noise_environment']}")

        print(sep)
        print("METADATA")
        print(sep)
        for key, val in result["metadata"].items():
            if isinstance(val, float) and val < 0.01:
                print(f"  {key}: {val:.2e}")
            else:
                print(f"  {key}: {val}")

        if result.get("verification_status"):
            print(f"\n  Verification      : {result['verification_status']}")
