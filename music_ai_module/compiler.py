"""
Layer 3: Music Prompt Compiler

Transforms structured acoustic parameters (from Layer 2) into a
standardised 7-segment natural-language prompt for music generation APIs
(Suno, Stable Audio, etc.).

Design principles
-----------------
DETERMINISTIC — The compiler is a rule-based template engine, not a creative
agent.  The same inputs always produce the same prompt, making every output
fully traceable to a specific physiological measurement.

OPTIONAL VERIFICATION — An OpenAI-compatible LLM (via Yun API) may be called
to perform a lightweight technical completeness check.  The system prompt
explicitly forbids the model from adding creative elements (temperature = 0.1).

7-Segment prompt structure
--------------------------
[1] Music Type       — fixed: "Pure instrumental music, generative and continuous"
[2] Genre            — derived from occupation lookup table
[3] Tempo            — exact BPM integer from entrainment calculation
[4] Instruments      — selected by respiratory rate & HRV status
[5] Acoustic Texture — conditional pink noise / continuous pad activation
[6] Emotional Anchor — narrative framing keyed to sympathetic load level
[7] Constraints      — explicit musical prohibitions (no transients, no dissonance…)
"""

from __future__ import annotations

from typing import Dict

from openai import OpenAI

from .config import SystemConfig, default_config
from .models import StaticUserProfile


# ---------------------------------------------------------------------------
# Genre lookup keyed by occupation
# ---------------------------------------------------------------------------

GENRE_MAP: Dict[str, str] = {
    "software_engineer": (
        "Minimalist electronic, complexity-free, logic-uncluttered, "
        "supports focus without cognitive interference"
    ),
    "student": (
        "Focus-oriented ambient, concentration-supportive, "
        "background presence, non-intrusive harmonic motion"
    ),
    "healthcare_worker": (
        "Grounding meditative ambient, nervous system stabilizing, "
        "emotionally safe, clinically calibrated for high-stress recovery"
    ),
    "default": "Meditative ambient, grounding, calming, emotionally neutral",
}


class MusicPromptCompiler:
    """
    Compile a music generation prompt from Layer-2 acoustic parameters.

    Usage
    -----
    >>> compiler = MusicPromptCompiler()
    >>> result = compiler.compile(user_profile, processed_params)
    >>> print(result["prompt"])

    Optionally verify the prompt with the LLM endpoint:
    >>> result = compiler.compile(user_profile, processed_params, verify=True)
    """

    def __init__(self, config: SystemConfig = default_config) -> None:
        self.config = config
        self._client = OpenAI(
            api_key=config.llm_api_key,
            base_url=config.llm_base_url,
        )

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def compile(
        self,
        profile: StaticUserProfile,
        processed_params: Dict,
        verify: bool = False,
    ) -> Dict:
        """
        Build the 7-segment prompt and return a result dictionary.

        Parameters
        ----------
        profile          : Static user profile (for occupation-based genre).
        processed_params : Output dict from ``BiometricProcessor.process()``.
        verify           : If True, send the compiled prompt to the LLM
                           for a technical completeness check (~$0.0005).

        Returns
        -------
        {
            "prompt":   str,           # final prompt string
            "segments": dict,          # individual segment contents
            "metadata": dict,          # token estimate, cost, validation
            # added when verify=True:
            "verified_prompt": str,
            "verification_status": str,
        }
        """
        segments = self._build_segments(profile, processed_params)
        prompt = self._join_segments(segments)
        metadata = self._build_metadata(prompt, processed_params)

        result: Dict = {
            "prompt":   prompt,
            "segments": segments,
            "metadata": metadata,
        }

        if verify:
            result = self._verify(result)

        return result

    # ------------------------------------------------------------------
    # Segment builders (one method per segment)
    # ------------------------------------------------------------------

    def _build_segments(
        self,
        profile: StaticUserProfile,
        params: Dict,
    ) -> Dict[str, str]:
        rhythm    = params["rhythm"]
        texture   = params["texture"]
        breathing = params["breathing"]
        safeguard = params["safeguards"]

        return {
            "music_type":      self._seg_music_type(),
            "genre":           self._seg_genre(profile),
            "tempo":           self._seg_tempo(rhythm),
            "instruments":     self._seg_instruments(breathing),
            "texture":         self._seg_texture(texture),
            "emotional_anchor": self._seg_emotional_anchor(rhythm),
            "constraints":     self._seg_constraints(safeguard),
        }

    def _seg_music_type(self) -> str:
        return "Pure instrumental music, generative and continuous"

    def _seg_genre(self, profile: StaticUserProfile) -> str:
        return GENRE_MAP.get(profile.occupation, GENRE_MAP["default"])

    def _seg_tempo(self, rhythm: Dict) -> str:
        bpm = max(
            self.config.min_bpm,
            min(self.config.max_bpm, rhythm["target_bpm"]),
        )
        return f"Tempo {bpm} BPM"

    def _seg_instruments(self, breathing: Dict) -> str:
        instruments = ", ".join(breathing["instrument_set"])
        return f"Instruments: {instruments}"

    def _seg_texture(self, texture: Dict) -> str:
        elements = []
        if texture["apply_pink_noise"]:
            elements.append(
                "pink noise broadband masking foundation "
                "(1/f spectrum for threat isolation)"
            )
        if texture["apply_pad_texture"]:
            elements.append(
                "continuous synthesizer pad (seamless harmonic grounding)"
            )
        if elements:
            return "Acoustic texture: " + "; ".join(elements)
        return "Acoustic texture: clean, unadorned instruments with natural resonance"

    def _seg_emotional_anchor(self, rhythm: Dict) -> str:
        load = rhythm["sympathetic_load"]
        if load > 20:
            return (
                "Emotional anchor: Deep nervous system grounding, "
                "immediate safety establishment, vagal tone rebalancing, "
                "parasympathetic activation cues, trauma-informed gentle progression"
            )
        if load > 10:
            return (
                "Emotional anchor: Calm supportive presence, "
                "gentle deactivation of arousal, "
                "spacious harmonic movement allowing breath recovery"
            )
        return (
            "Emotional anchor: Supportive focus state, "
            "minimal emotional narrative, "
            "transparent presence supporting user's agency"
        )

    def _seg_constraints(self, safeguard: Dict) -> str:
        items = []
        if safeguard["forbid_sharp_transients"]:
            items.append(
                "FORBIDDEN: Sharp transient attacks or sudden envelope spikes "
                "(startle trigger prevention)"
            )
        if safeguard["forbid_high_freq_peaks"]:
            items.append(
                "FORBIDDEN: High-frequency peaks above 8 kHz "
                "(environmental noise summation prevents masking)"
            )
        if safeguard["forbid_percussive_hits"]:
            items.append(
                "FORBIDDEN: Percussive hits, drums, or impact sounds "
                "(sudden acoustic threats)"
            )
        # Always-on constraints
        items += [
            "FORBIDDEN: Sudden volume jumps or dynamic compression artifacts",
            "FORBIDDEN: Dissonant intervals or tonal instability "
            "(harmonic threat detection)",
        ]
        return "Strict negative constraints: " + "; ".join(items)

    # ------------------------------------------------------------------
    # Assembly helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _join_segments(segments: Dict[str, str]) -> str:
        ordered = [
            "music_type",
            "genre",
            "tempo",
            "instruments",
            "texture",
            "emotional_anchor",
            "constraints",
        ]
        return " | ".join(segments[k] for k in ordered if segments.get(k))

    @staticmethod
    def _build_metadata(prompt: str, params: Dict) -> Dict:
        token_estimate = int(len(prompt.split()) * 1.3)
        rhythm  = params["rhythm"]
        texture = params["texture"]
        return {
            "prompt_length_chars":          len(prompt),
            "prompt_length_tokens_estimate": token_estimate,
            "target_bpm":                   rhythm["target_bpm"],
            "sympathetic_load":             rhythm["sympathetic_load"],
            "hrv_status":                   texture["hrv_status"],
            "api_cost_estimate_usd":        token_estimate * 0.00002,
            "validation_status":            "pass" if len(prompt) < 2000 else "warning",
        }

    # ------------------------------------------------------------------
    # Optional LLM verification
    # ------------------------------------------------------------------

    def _verify(self, result: Dict) -> Dict:
        """
        Send the compiled prompt to the Yun API for a lightweight technical
        completeness check.  The LLM is strictly constrained: temperature 0.1,
        max 200 tokens, system prompt forbids creative additions.
        """
        raw_prompt = result["prompt"]
        try:
            response = self._client.chat.completions.create(
                model=self.config.llm_model,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are a music production prompt engineer. "
                            "Your ONLY task is to verify technical completeness "
                            "and clarity of music generation prompts. "
                            "DO NOT add creative elements, subjective descriptions, "
                            "or artistic interpretations. "
                            "Only verify: 1) All required fields present, "
                            "2) BPM is an exact number, "
                            "3) Instruments are realistic, "
                            "4) Constraints are unambiguous. "
                            "Return ONLY the prompt text "
                            "(optionally with minor clarity fixes). "
                            "NO explanations, NO additions, NO creative changes."
                        ),
                    },
                    {
                        "role": "user",
                        "content": (
                            f"Verify technical completeness of this music prompt:"
                            f"\n\n{raw_prompt}"
                        ),
                    },
                ],
                temperature=0.1,
                max_tokens=200,
                timeout=10,
            )
            result["verified_prompt"]      = response.choices[0].message.content.strip()
            result["verification_status"]  = "success"
            result["verification_cost_usd"] = 0.0005
        except Exception as exc:
            result["verification_status"] = "skipped"
            result["verification_error"]  = str(exc)

        return result
