# MindWave

> **Biometric-Driven Adaptive Music Therapy** — a 4-layer architecture that converts real-time Apple Watch health data into personalised AI-generated music for mental wellness.

---

## Overview

MindWave bridges physiological sensing and generative music AI. It reads live biometric signals from Apple Watch (heart rate, HRV, respiratory rate, SpO₂, and more), passes them through a neuroscience-grounded rules engine, compiles a deterministic music generation prompt, and delivers the result via the Suno AI music API — all presented through a polished, single-page therapy interface.

The system is designed around **rhythmic entrainment theory**: music tempo and texture are derived directly from a user's current physiological state, not from subjective mood tags alone. A 15% BPM reduction from the measured heart rate creates a physical anchor that guides cardiovascular rhythms downward.

---

## Architecture

```
Apple Watch / HealthKit
        │
        ▼
┌────────────────────────────────────────────────────────────┐
│  Layer 1 · Input & Validation                              │
│  StaticUserProfile + AppleWatchBiometrics (dataclasses)    │
│  Physiological range validation (HR, HRV, SpO₂, temp…)    │
└────────────────────┬───────────────────────────────────────┘
                     │
                     ▼
┌────────────────────────────────────────────────────────────┐
│  Layer 2 · Middleware Rules Engine  (BiometricProcessor)   │
│  • HR → Target BPM  (entrainment: HR × 0.85, floor 45)    │
│  • HRV < 40 ms → pink noise + continuous pad               │
│  • Resp rate > 18 br/min → cello legato + sustained synth  │
│  • Ambient noise > 70 dB → transient / peak safeguards     │
│  • Sympathetic load = current HR − resting baseline        │
└────────────────────┬───────────────────────────────────────┘
                     │
                     ▼
┌────────────────────────────────────────────────────────────┐
│  Layer 3 · LLM Compiler  (MusicPromptCompiler)             │
│  7-segment deterministic template engine                   │
│  [1] Music Type  [2] Genre  [3] Tempo  [4] Instruments     │
│  [5] Texture     [6] Emotional Anchor  [7] Constraints      │
│  Optional: LLM technical verification via OpenAI-compat.   │
└────────────────────┬───────────────────────────────────────┘
                     │
                     ▼
┌────────────────────────────────────────────────────────────┐
│  Layer 4 · Music Generation  (Suno API v5)                 │
│  POST /api/v1/generate → poll → stream/download MP3        │
│  Real-time progress tracking, cancellation, auto-playback  │
└────────────────────────────────────────────────────────────┘
```

---

## Repository Structure

```
MindWave/
├── web.html                   # Single-page therapy UI (all-in-one)
├── music_ai_module/           # Python pipeline library
│   ├── __init__.py            # Public API exports
│   ├── models.py              # Layer 1: dataclasses & validation
│   ├── processor.py           # Layer 2: BiometricProcessor
│   ├── compiler.py            # Layer 3: MusicPromptCompiler
│   ├── pipeline.py            # End-to-end orchestrator (MusicAIPipeline)
│   ├── config.py              # SystemConfig (all tunable parameters)
│   └── example.py             # Smoke-test / quick-start script
├── Music AI.ipynb             # Research notebook — full pipeline walkthrough
├── api_test.js                # Node.js Suno API integration test
├── generate_cases.js          # Batch script: generate 5 demo tracks via Suno
├── case_audio_urls.json       # Cached MP3 URLs for 5 demo cases
├── case.md                    # Clinical case definitions (input tags + prompts)
├── .env                       # API keys (not committed)
└── README.md
```

---

## Features

### Therapy Interface (`web.html`)
A fully self-contained single-page application — no build step, no dependencies to install.

| Area | Details |
|---|---|
| **Mood Input** | Free-text entry interpreted into therapy mode |
| **Mode Chips** | Deep Focus · Calm Down · Drift to Sleep · Anxiety Relief · Grounding · Energy Boost · Trauma Gentle |
| **Vibe Chips** | Anxious · Overwhelmed · Creative Flow (multi-select, up to 3) |
| **Brainwave Mapping** | Each mode maps to a clinical frequency: Gamma 40Hz / Theta 6Hz / Delta 2Hz / Alpha 10Hz / Schumann 7.83Hz / Beta 18Hz / Infra-Low 0.5Hz |
| **Vinyl Player** | Gramophone-style visualiser with EQ bars, progress scrubbing, skip ±30s |
| **Suno Generation** | One-click AI music generation via Suno V5 API with live status polling |
| **Controls Drawer** | Intensity (1–4) · Duration (15/30/45 min) · Environment (None/Rain/Noise) |

### Profile Modal
5-step therapy onboarding form:
1. **Basic Information** — Name, age, gender, contact
2. **Physical Health** — Hearing, chronic conditions, medication, sleep quality (slider)
3. **Emotional Landscape** — Current state (up to 3), treatment goals, fluctuation pattern
4. **Music Preferences** — Styles, sounds to avoid, rhythm preference (slider), volume sensitivity
5. **Treatment History** — Previous therapy, types, session count, effectiveness

Profile data persists to `localStorage` and auto-restores on reload.

### Biometric Monitor (Vitals Modal)
Displays a live Apple Watch biometric snapshot with derived clinical analysis:

| Metric | Source | Notes |
|---|---|---|
| Heart Rate | HealthKit | ECG-style sparkline animation |
| HRV · SDNN | HealthKit | 8-bar trend chart; threshold alert at < 40 ms |
| Stress Score | Derived | Circular ring gauge, colour-graded (green/amber/red) |
| Respiratory Rate | HealthKit | Instrument selection trigger at > 18 br/min |
| Blood Oxygen SpO₂ | HealthKit | Alert below 94% |
| Wrist Temperature | HealthKit | Warning above 37.5 °C |
| Ambient Noise | HealthKit | Safeguard trigger above 70 dB |
| Body Motion (XYZ) | Accelerometer | Three-axis bar visualisation |
| Sleep Stage | HealthKit | Awake / Core / Deep / REM |
| **Layer 2 Analysis** | Computed | Target BPM · Sympathetic Load · HRV Status · Acoustic Texture · Instrument Set · Noise Safeguard |

### Demo Cases
Five pre-loaded clinical demonstration cases, each with a full profile, biometric snapshot, and a pre-generated Suno V5 track:

| ID | Patient | Condition | Track |
|---|---|---|---|
| `case_001` | Xiao Wang, 28M | Work anxiety, post-work brain tension | *Midnight Window Seat* |
| `case_002` | Lao Li, 62F | Insomnia, auditory sensitivity | *Moonlight Between Breaths* |
| `case_003` | Xiao Chen, 21M | Attention deficit, study distraction | *Pure Function* |
| `case_004` | Li Tongxue, 28M | PhD thesis anxiety, late-night lab | *Night Shift in Soft Gold* |
| `case_005` | Prof. Zhang, 45M | Dual research/teaching pressure, existential anxiety | *Autumn Tenure* |

Clicking a case instantly loads: profile data into the modal, mood input and mode/vibe chips, biometric data into the Vitals monitor, and begins playing the cached MP3.

---

## Python Module (`music_ai_module`)

### Installation

```bash
pip install openai numpy
```

No additional packages are required for core pipeline operation.

### Quick Start

```python
from datetime import datetime
from music_ai_module import MusicAIPipeline, SystemConfig
from music_ai_module.models import StaticUserProfile, AppleWatchBiometrics

user = StaticUserProfile(
    occupation="software_engineer",
    age=28,
    height_cm=180,
    baseline_heart_rate=65,
    chronic_stress_sources=["work_deadline", "sleep_quality"],
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

pipeline = MusicAIPipeline()
result = pipeline.run(user, biometrics)

print(result["prompt"])           # → final Suno prompt string
print(result["processed_params"]) # → Layer 2 acoustic parameters
MusicAIPipeline.describe(result)  # → formatted console summary
```

### Run the Smoke Test

```bash
python music_ai_module/example.py            # no API calls
python music_ai_module/example.py --verify   # optional LLM verification (~$0.0005)
```

### Configuration

All parameters are centralised in `SystemConfig` and can be overridden via environment variables:

| Parameter | Default | Description |
|---|---|---|
| `OPENAI_API_KEY` | — | LLM API key (optional verification only) |
| `LLM_BASE_URL` | `https://api.zyai.online/v1` | OpenAI-compatible endpoint |
| `LLM_MODEL` | `gpt-3.5-turbo` | Model for prompt verification |
| `SUNO_API_KEY` | — | Suno music generation key |
| `min_bpm` | 45 | Hard floor for entrainment BPM |
| `max_bpm` | 140 | Hard ceiling for entrainment BPM |
| `rhythm_reduction_pct` | 15.0 | Entrainment reduction (%) |
| `hrv_safety_threshold` | 40.0 ms | HRV below which masking activates |
| `max_noise_db` | 70.0 dB | Noise above which safeguards fire |
| `sample_interval_s` | 30 s | Biometric sampling interval |
| `feedback_loop_s` | 180 s | Duration of one intervention cycle |
| `cycles_per_session` | 3 | Cycles per full therapy session |
| `hr_smoothing_window` | 5 | Moving-average window for HR filter |

### Layer 2 Mapping Logic

```
Heart Rate → Target BPM
    target = max(45, HR × 0.85)
    Rhythmic entrainment effect: 15% reduction triggers measurable HR descent

HRV (SDNN) → Acoustic Texture
    < 40 ms  →  pink noise broadband masking + continuous synthesizer pad
    ≥ 40 ms  →  clean instruments with natural resonance

Respiratory Rate → Instrument Set
    > 18 br/min  →  cello_legato + sustained_synth  (guides exhalation lengthening)
    ≤ 18 br/min  →  piano + ambient_strings

Ambient Noise → Safety Constraints
    > 70 dB  →  forbid sharp transients, high-freq peaks, percussive hits

Sympathetic Load → Emotional Anchor
    = current HR − resting baseline HR
    > 20 BPM  →  deep grounding, vagal tone rebalancing
    > 10 BPM  →  calm deactivation, breath recovery
    ≤ 10 BPM  →  focus support, transparent presence
```

---

## Demo Track Generation

To regenerate the five demo case tracks (requires Suno API key in `.env`):

```bash
node generate_cases.js
```

The script submits all five prompts sequentially, polls until completion, and saves the resulting MP3 URLs to `case_audio_urls.json`. Each generation takes approximately 1–3 minutes per track.

---

## Suno API Integration

The web interface uses the [sunoapi.org](https://sunoapi.org) third-party wrapper:

```
POST  https://api.sunoapi.org/api/v1/generate
GET   https://api.sunoapi.org/api/v1/generate/record-info?taskId=…
```

- Model: **V5** (instrumental, non-custom mode)
- Prompt cap: 500 characters
- Poll interval: 5 seconds, timeout: 7 minutes
- Status flow: `PENDING → TEXT_SUCCESS → FIRST_SUCCESS → SUCCESS`

Your API key is stored only in `localStorage` and is never forwarded to any server other than the Suno endpoint.

---

## Neuroscience Basis

| Principle | Implementation |
|---|---|
| **Rhythmic Entrainment** | Music BPM set 15% below heart rate; repeated auditory stimuli entrain cardiovascular rhythms via baroreflex modulation |
| **HRV & Vagal Tone** | SDNN < 40 ms indicates sympathetic dominance; acoustic masking (pink noise) reduces perceived threat and supports parasympathetic re-engagement |
| **Respiratory Synchronisation** | Sustained legato instruments at slow tempos naturally extend exhalation cycles, activating the parasympathetic nervous system |
| **Brainwave Entrainment** | Binaural beat frequencies embedded at clinically relevant bands: Delta (2 Hz, sleep), Theta (6 Hz, relaxation), Alpha (10 Hz, anxiety relief), Gamma (40 Hz, focus) |
| **Environmental Acoustic Safety** | Above 70 dB ambient, sharp transients risk startle responses; constraints are applied automatically |

---

## Design System

The UI is built on a dark glass-morphism aesthetic:

- **Fonts**: Cormorant Garamond (display) · Outfit (body) · JetBrains Mono (data)
- **Colour palette**: Deep space black `#030305`, layered white-alpha glass surfaces
- **Animations**: Organic morphing background (UnicornStudio), EQ bar waveforms, vinyl record rotation, floating music notes, CSS entrances with staggered blur-up reveals
- **Framework**: Tailwind CSS (CDN) · Iconify icons · No build toolchain required

---

## Environment Setup

Create a `.env` file in the project root:

```env
API_KEY=your_suno_api_key_here
```

For the Python module's LLM verification feature:

```env
OPENAI_API_KEY=your_llm_key
LLM_BASE_URL=https://api.zyai.online/v1
LLM_MODEL=gpt-3.5-turbo
```

---

## License

See [LICENSE](LICENSE) for details.
