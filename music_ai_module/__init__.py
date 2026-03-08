"""
music_ai_module
===============

Biometric-to-music pipeline: converts Apple Watch physiological data into
a standardised music generation prompt via a 4-layer architecture.

Public API
----------
    from music_ai_module import MusicAIPipeline, SystemConfig
    from music_ai_module.models import StaticUserProfile, AppleWatchBiometrics
"""

from .config import SystemConfig, default_config
from .compiler import MusicPromptCompiler
from .models import AppleWatchBiometrics, StaticUserProfile
from .pipeline import MusicAIPipeline
from .processor import BiometricProcessor

__all__ = [
    "MusicAIPipeline",
    "BiometricProcessor",
    "MusicPromptCompiler",
    "SystemConfig",
    "default_config",
    "StaticUserProfile",
    "AppleWatchBiometrics",
]
