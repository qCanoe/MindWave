"""
Layer 1: Multi-Modal Data Input Models

Defines the data structures for static user profiles and real-time
Apple Watch biometric readings.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Dict, List


# ---------------------------------------------------------------------------
# Validation bounds (physiologically plausible ranges)
# ---------------------------------------------------------------------------

VALID_RANGES = {
    "heart_rate":              (30, 200),   # BPM
    "heart_rate_variability":  (5,  250),   # ms (SDNN)
    "respiratory_rate":        (8,  30),    # breaths/min
    "wrist_temperature":       (35, 42),    # °C
    "blood_oxygen":            (85, 100),   # SpO2 %
    "environmental_audio":     (20, 130),   # dB
}


@dataclass
class StaticUserProfile:
    """
    User static characteristics — captured at onboarding, updated quarterly.

    Fields
    ------
    occupation            : Occupational context used for genre/style mapping.
                            Supported values: "software_engineer", "student",
                            "healthcare_worker", or any string (falls back to default).
    age                   : Age in years.
    height_cm             : Height in centimetres (reserved for future normalisation).
    baseline_heart_rate   : Resting heart rate in BPM, taken after 5-min rest.
    chronic_stress_sources: List of known chronic stressors (narrative context).
    music_preference      : Aesthetic direction string (e.g. "minimalist_ambient").
    """

    occupation: str
    age: int
    height_cm: float
    baseline_heart_rate: int
    chronic_stress_sources: List[str] = field(default_factory=list)
    music_preference: str = "ambient"


@dataclass
class AppleWatchBiometrics:
    """
    Real-time biometric snapshot from Apple Watch.

    Required fields are sampled every 30–60 s via HealthKit.
    Optional fields depend on device generation and user permissions.

    Fields
    ------
    timestamp                  : UTC datetime of measurement.
    heart_rate                 : Instantaneous heart rate in BPM.
    heart_rate_variability     : SDNN in milliseconds.
    respiratory_rate           : Breaths per minute.
    environmental_audio_exposure: Ambient noise level in dB.
    body_motion                : 3-axis accelerometer dict {"x", "y", "z"} in g.
    wrist_temperature          : Skin temperature in °C (optional).
    blood_oxygen               : SpO2 percentage (optional).
    sleep_stage                : Current sleep stage: "awake", "core", "deep", "rem"
                                 (optional — only available during sleep tracking).
    """

    timestamp: datetime
    heart_rate: int
    heart_rate_variability: float
    respiratory_rate: int
    environmental_audio_exposure: float
    body_motion: Dict[str, float]
    wrist_temperature: Optional[float] = None
    blood_oxygen: Optional[float] = None
    sleep_stage: Optional[str] = None

    def validate(self) -> List[str]:
        """
        Check all sensor values are within physiologically plausible bounds.

        Returns a list of error strings. Empty list means all data is valid.
        """
        errors: List[str] = []

        checks = [
            ("heart_rate",             self.heart_rate),
            ("heart_rate_variability", self.heart_rate_variability),
            ("respiratory_rate",       self.respiratory_rate),
            ("environmental_audio",    self.environmental_audio_exposure),
        ]

        if self.wrist_temperature is not None:
            checks.append(("wrist_temperature", self.wrist_temperature))
        if self.blood_oxygen is not None:
            checks.append(("blood_oxygen", self.blood_oxygen))

        for field_name, value in checks:
            lo, hi = VALID_RANGES[field_name]
            if not (lo <= value <= hi):
                errors.append(
                    f"{field_name} value {value} is outside valid range [{lo}, {hi}]"
                )

        return errors
