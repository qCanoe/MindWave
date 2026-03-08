"""
Layer 2: Middleware Rules Engine

Converts raw biometric data into structured acoustic parameters.

Theory
------
Three neuroscience principles drive the mapping:

A) Autonomic Nervous System Mapping
   Heart-rate deviation from personal baseline quantifies sympathetic arousal.
   The larger the deviation, the more aggressive the BPM entrainment and
   grounding textures applied.

B) HRV as Nervous-System Flexibility Indicator
   SDNN < 40 ms signals a rigid, stressed autonomic state.
   Acoustic masking (pink noise + continuous pad) is activated below this threshold.

C) Respiratory Synchronisation
   Respiratory rate > 18 breaths/min signals anxiety.
   Sustained instruments (cello legato, synth pad) guide exhalation lengthening.
"""

from __future__ import annotations

from typing import Dict, List

import numpy as np

from .config import SystemConfig, default_config
from .models import AppleWatchBiometrics, StaticUserProfile


# ---------------------------------------------------------------------------
# Occupation → aesthetic style lookup
# ---------------------------------------------------------------------------

OCCUPATION_STYLE: Dict[str, str] = {
    "software_engineer": "minimalist_electronic",
    "student":           "focus_ambient",
    "healthcare_worker": "grounding_meditative",
}


class BiometricProcessor:
    """
    Master middleware engine.

    Usage
    -----
    >>> processor = BiometricProcessor()
    >>> params = processor.process(user_profile, biometrics)
    """

    def __init__(self, config: SystemConfig = default_config) -> None:
        self.config = config
        self._hr_history: List[float] = []

    # ------------------------------------------------------------------
    # Module 1 — Noise filtering
    # ------------------------------------------------------------------

    def smooth_heart_rate(self, current_hr: int) -> float:
        """Sliding-window moving average to suppress sensor noise."""
        self._hr_history.append(float(current_hr))
        if len(self._hr_history) > self.config.hr_smoothing_window:
            self._hr_history.pop(0)
        return float(np.mean(self._hr_history))

    # ------------------------------------------------------------------
    # Module 2 — Cross-modal parameter mappings
    # ------------------------------------------------------------------

    def _sympathetic_load(self, current_hr: int, baseline_hr: int) -> int:
        """
        Sympathetic nervous system arousal expressed as BPM deviation
        above the user's personal resting baseline.
        """
        return current_hr - baseline_hr

    def _map_hr_to_target_bpm(self, current_hr: int) -> int:
        """
        Rhythmic Entrainment: target tempo is current HR reduced by
        ``config.rhythm_reduction_pct`` percent, clamped to safe range.

        Research basis: a 7–15 % BPM reduction reliably produces a
        measurable heart-rate descent via entrainment.
        """
        raw = current_hr * (1.0 - self.config.rhythm_reduction_pct / 100.0)
        return int(max(self.config.min_bpm, min(self.config.max_bpm, raw)))

    def _map_hrv_to_texture(self, hrv_ms: float) -> Dict:
        """
        HRV → acoustic texture parameters.

        Below safety threshold: activate pink-noise broadband masking and
        a continuous synthesizer pad to prevent startle / anxiety spikes.
        """
        stressed = hrv_ms < self.config.hrv_safety_threshold
        return {
            "hrv_status":       "stressed_rigid" if stressed else "flexible_resilient",
            "apply_pink_noise": stressed,
            "apply_pad_texture": stressed,
            "pad_type":         "continuous_synthesizer" if stressed else None,
            "hrv_score":        hrv_ms,
        }

    def _map_respiratory_to_instruments(self, resp_rate: int) -> Dict:
        """
        Respiratory rate → instrument selection.

        Elevated breathing (> 18 bpm) triggers sustained legato instruments
        whose long tones naturally guide exhalation lengthening.
        """
        elevated = resp_rate > 18
        return {
            "respiratory_status": "elevated_anxious" if elevated else "normal_calm",
            "trigger_legato":     elevated,
            "instrument_set": (
                ["cello_legato", "sustained_synth"]
                if elevated
                else ["piano", "ambient_strings"]
            ),
            "resp_rate": resp_rate,
        }

    def _map_noise_to_safeguards(self, noise_db: float) -> Dict:
        """
        Ambient noise level → safety constraint flags.

        Above 70 dB the risk of a startle response is elevated; we suppress
        sharp transients and high-frequency peaks in the generated music.
        """
        threat = noise_db > self.config.max_noise_db
        return {
            "noise_environment":      "harsh_noisy" if threat else "quiet_safe",
            "forbid_sharp_transients": threat,
            "forbid_high_freq_peaks":  threat,
            "forbid_percussive_hits":  threat,
            "ambient_db":              noise_db,
        }

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def process(
        self,
        profile: StaticUserProfile,
        biometrics: AppleWatchBiometrics,
    ) -> Dict:
        """
        Execute the full Layer-2 pipeline and return a structured parameter
        dictionary ready for the Layer-3 prompt compiler.

        Parameters
        ----------
        profile    : Static user profile (occupation, baseline HR, etc.)
        biometrics : Current Apple Watch biometric snapshot.

        Returns
        -------
        dict with keys: rhythm, texture, breathing, safeguards,
                        aesthetic_style, timestamp
        """
        self.smooth_heart_rate(biometrics.heart_rate)

        rhythm_params = {
            "target_bpm":      self._map_hr_to_target_bpm(biometrics.heart_rate),
            "current_hr":      biometrics.heart_rate,
            "sympathetic_load": self._sympathetic_load(
                biometrics.heart_rate, profile.baseline_heart_rate
            ),
        }

        return {
            "rhythm":         rhythm_params,
            "texture":        self._map_hrv_to_texture(biometrics.heart_rate_variability),
            "breathing":      self._map_respiratory_to_instruments(biometrics.respiratory_rate),
            "safeguards":     self._map_noise_to_safeguards(biometrics.environmental_audio_exposure),
            "aesthetic_style": OCCUPATION_STYLE.get(profile.occupation, "ambient"),
            "timestamp":      biometrics.timestamp.isoformat(),
        }
