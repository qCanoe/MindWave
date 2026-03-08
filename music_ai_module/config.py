"""
System Configuration

Single source of truth for all tunable parameters.
Override defaults by setting environment variables before importing.
"""

import os
from dataclasses import dataclass


@dataclass
class SystemConfig:
    """
    Central configuration for the biometric-to-music pipeline.

    All values can be overridden via environment variables at import time.

    LLM / API
    ---------
    llm_api_key   : API key for the LLM verification endpoint.
    llm_base_url  : Base URL for the OpenAI-compatible LLM endpoint.
    llm_model     : Model name used for optional prompt verification.
    suno_api_key  : API key for Suno music generation (optional — Layer 4).

    Music Generation
    ----------------
    min_bpm               : Hard floor for generated music tempo.
    max_bpm               : Hard ceiling for generated music tempo.
    rhythm_reduction_pct  : Percentage by which current HR is reduced to derive
                            the target entrainment BPM (default 15 %).

    Physiological Thresholds
    ------------------------
    hrv_safety_threshold  : HRV (ms) below which acoustic masking is activated.
    max_noise_db          : Ambient noise level (dB) above which safety
                            constraints (no transients, no high-freq peaks) fire.

    Timing
    ------
    sample_interval_s      : Seconds between biometric readings.
    feedback_loop_s        : Duration of one music-intervention cycle.
    cycles_per_session     : How many cycles constitute a full session.

    Smoothing
    ---------
    hr_smoothing_window    : Number of HR samples used in the moving-average filter.
    """

    # LLM / API
    llm_api_key: str = os.environ.get(
        "OPENAI_API_KEY", ""
    )
    llm_base_url: str = os.environ.get(
        "LLM_BASE_URL", "https://api.zyai.online/v1"
    )
    llm_model: str = os.environ.get("LLM_MODEL", "gpt-3.5-turbo")
    suno_api_key: str = os.environ.get("SUNO_API_KEY", "")

    # Music generation bounds
    min_bpm: int = 45
    max_bpm: int = 140
    rhythm_reduction_pct: float = 15.0

    # Physiological thresholds
    hrv_safety_threshold: float = 40.0   # ms
    max_noise_db: float = 70.0           # dB

    # Timing
    sample_interval_s: int = 30
    feedback_loop_s: int = 180
    cycles_per_session: int = 3

    # HR smoothing
    hr_smoothing_window: int = 5


# Module-level default instance — importable directly
default_config = SystemConfig()
