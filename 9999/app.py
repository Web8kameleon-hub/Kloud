import base64
import asyncio
import hashlib
import hmac
import math
import os
import secrets
import struct
import subprocess
import time
import wave
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
import uuid
import json
import ast
import re
import importlib

import httpx
import numpy as np
from fastapi import Body, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

imageio: Any = None
Image: Any = None
ImageDraw: Any = None

try:
    imageio = importlib.import_module("imageio.v2")
except ModuleNotFoundError:
    pass

try:
    Image = importlib.import_module("PIL.Image")
    ImageDraw = importlib.import_module("PIL.ImageDraw")
except ModuleNotFoundError:
    pass

PORT = int(os.getenv("PORT", "9999"))
MODEL = os.getenv("MODEL", "llama3.1:8b")
VISION_TARGET_MODEL = os.getenv("VISION_TARGET_MODEL", "nanogrid-zeiss")
REQUEST_TIMEOUT = float(os.getenv("REQUEST_TIMEOUT", "90"))

OCEAN_CORE_URL = os.getenv("OCEAN_CORE_URL", "http://kloud-ocean-core:8030")
VIDEO_GENERATOR_URL = os.getenv(
    "VIDEO_GENERATOR_URL", "http://kloud-video-generator:8029"
)
VISION_SERVICE_URL = os.getenv(
    "VISION_SERVICE_URL", f"{OCEAN_CORE_URL}/api/v1/vision/analyze"
)

BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / "output"
MUSIC_DIR = OUTPUT_DIR / "music"
VIDEO_DIR = OUTPUT_DIR / "video"
IMAGE_DIR = OUTPUT_DIR / "images"
DOCS_DIR = OUTPUT_DIR / "docs"
RESONANT_STORE_DIR = OUTPUT_DIR / "resonant"
RESONANT_SEGMENTS_DIR = RESONANT_STORE_DIR / "segments"
RESONANT_CHECKPOINTS_DIR = RESONANT_STORE_DIR / "checkpoints"
for directory in [
    OUTPUT_DIR,
    MUSIC_DIR,
    VIDEO_DIR,
    IMAGE_DIR,
    DOCS_DIR,
    RESONANT_STORE_DIR,
    RESONANT_SEGMENTS_DIR,
    RESONANT_CHECKPOINTS_DIR,
]:
    directory.mkdir(parents=True, exist_ok=True)

GLOBAL_SYSTEM_PROMPT = """You are Kloud Global AI Orchestrator on port 9999.
Rules:
1. Support all world languages fairly and respectfully.
2. Never produce hateful, racist, discriminatory, or demeaning content.
3. If a request asks for discrimination or harm, refuse briefly and offer safe help.
4. Be practical, concise, and production-oriented.
"""

# Solfege base frequencies (C4 oktava mesme)
SOLFEGE_FREQ = {
    "do": 261.63,  # C4
    "re": 293.66,  # D4
    "mi": 329.63,  # E4
    "fa": 349.23,  # F4
    "sol": 392.00,  # G4
    "so": 392.00,  # G4 (alias)
    "la": 440.00,  # A4
    "si": 493.88,  # B4
    # Sharps dhe Flats
    "do#": 277.18,  # C# / Db
    "reb": 277.18,
    "re#": 311.13,  # D# / Eb
    "mib": 311.13,
    "mi#": 349.23,  # E# (same as F)
    "fab": 329.63,  # Fb (same as E)
    "fa#": 369.99,  # F# / Gb
    "solb": 369.99,
    "sol#": 415.30,  # G# / Ab
    "lab": 415.30,
    "la#": 466.16,  # A# / Bb
    "sib": 466.16,
    "si#": 523.25,  # B# (same as C5)
}

# Oktavat: ultra-low, low, mid, high, ultra-high
OCTAVE_MULTIPLIERS = {
    "ultra-low": 0.25,  # 2 oktava poshtë
    "low": 0.5,  # 1 oktavë poshtë
    "mid": 1.0,  # oktava standard (C4)
    "high": 2.0,  # 1 oktavë lart
    "ultra-high": 4.0,  # 2 oktava lart
}

# Kohëzgjatja e notave (në ms)
NOTE_DURATIONS = {
    "whole": 2000,  # nota e plotë
    "half": 1000,  # gjysma
    "quarter": 500,  # çereku (1/4)
    "eighth": 250,  # 1/8
    "sixteenth": 125,  # 1/16
    "thirty-second": 62,  # 1/32
}

# Instrumentet/Waveforms
WAVEFORMS = {
    "sine": "sine",  # Sine wave - tingull i pastër
    "square": "square",  # Square wave - 8-bit retro
    "sawtooth": "sawtooth",  # Sawtooth - synth lead
    "triangle": "triangle",  # Triangle - soft synth
    "bass": "bass",  # Low-frequency emphasis
    "organ": "organ",  # Harmonike të shumta
    "piano": "piano",  # Attack-decay envelope
}

# Rrymat muzikore (Music Genres)
MUSIC_GENRES = {
    "classical": {
        "tempo_range": [60, 120],
        "waveforms": ["piano", "organ"],
        "reverb": 0.3,
    },
    "jazz": {"tempo_range": [80, 160], "waveforms": ["piano", "bass"], "swing": True},
    "electronic": {
        "tempo_range": [120, 180],
        "waveforms": ["square", "sawtooth"],
        "distortion": 0.2,
    },
    "ambient": {
        "tempo_range": [40, 80],
        "waveforms": ["sine", "triangle"],
        "reverb": 0.7,
    },
    "rock": {
        "tempo_range": [100, 140],
        "waveforms": ["sawtooth", "square"],
        "distortion": 0.5,
    },
    "hip-hop": {
        "tempo_range": [70, 110],
        "waveforms": ["bass", "square"],
        "bass_boost": 1.5,
    },
    "pop": {"tempo_range": [100, 130], "waveforms": ["piano", "sine"], "chorus": True},
}

# Akkorde (Chords) - semitone offsets from root
CHORDS = {
    "major": [0, 4, 7],  # Do major = do, mi, sol
    "minor": [0, 3, 7],  # Do minor = do, mib, sol
    "seventh": [0, 4, 7, 10],  # Do7
    "major7": [0, 4, 7, 11],  # Dmaj7
    "minor7": [0, 3, 7, 10],  # Dm7
    "diminished": [0, 3, 6],  # Ddim
    "augmented": [0, 4, 8],  # Daug
    "sus2": [0, 2, 7],  # Dsus2
    "sus4": [0, 5, 7],  # Dsus4
}

# Audio Effects
EFFECTS = {
    "reverb": {"delay_ms": 50, "decay": 0.3, "mix": 0.2},
    "echo": {"delay_ms": 500, "decay": 0.5, "repeats": 3},
    "chorus": {"voices": 3, "detune": 10, "delay_ms": 25},
    "vibrato": {"rate_hz": 5, "depth": 0.02},
    "tremolo": {"rate_hz": 4, "depth": 0.3},
    "distortion": {"gain": 2.0, "threshold": 0.7},
}

app = FastAPI(title="Kloud 9999 Gateway", version="2.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

MEMORY_STORE: List[Dict[str, Any]] = []
TASK_STORE: Dict[str, Dict[str, Any]] = {}
EVENT_CHAIN: List[Dict[str, Any]] = []
NONCE_STORE: Dict[str, float] = {}

REPLAY_WINDOW_SECONDS = int(os.getenv("REPLAY_WINDOW_SECONDS", "300"))
MAX_EVENT_CHAIN_SIZE = int(os.getenv("MAX_EVENT_CHAIN_SIZE", "100000"))
MAX_CLOCK_SKEW_MS = int(os.getenv("MAX_CLOCK_SKEW_MS", "120000"))
RESONANT_ADMIN_KEY = os.getenv("RESONANT_ADMIN_KEY", "")
RESONANT_REPLICATION_TOKEN = os.getenv("RESONANT_REPLICATION_TOKEN", "")
RESONANT_SEGMENT_SIZE = int(os.getenv("RESONANT_SEGMENT_SIZE", "2000"))
RESONANT_CHECKPOINT_EVERY = int(os.getenv("RESONANT_CHECKPOINT_EVERY", "500"))
RESONANT_QUORUM_W = int(os.getenv("RESONANT_QUORUM_W", "1"))
RESONANT_REPLICATION_TIMEOUT = float(os.getenv("RESONANT_REPLICATION_TIMEOUT", "2.5"))
ADAPTIVE_COMPAT_MODE = os.getenv("ADAPTIVE_COMPAT_MODE", "true").lower() in {
    "1",
    "true",
    "yes",
    "on",
}
PRIMARY_RESONANT_PROFILE = os.getenv(
    "PRIMARY_RESONANT_PROFILE", "wwwmmm-ndb-stigma-tide-rezonance-nanogrid"
)
OLD_MODE_ON_MISMATCH = os.getenv("OLD_MODE_ON_MISMATCH", "true").lower() in {
    "1",
    "true",
    "yes",
    "on",
}
TIDE_MEDIUM_PRESSURE_RATIO = float(os.getenv("TIDE_MEDIUM_PRESSURE_RATIO", "0.60"))
TIDE_HIGH_PRESSURE_RATIO = float(os.getenv("TIDE_HIGH_PRESSURE_RATIO", "0.85"))
ADAPTIVE_FALLBACK_THRESHOLD_LOW = int(os.getenv("ADAPTIVE_FALLBACK_THRESHOLD_LOW", "2"))
ADAPTIVE_FALLBACK_THRESHOLD_MEDIUM = int(
    os.getenv("ADAPTIVE_FALLBACK_THRESHOLD_MEDIUM", "1")
)
ADAPTIVE_FALLBACK_THRESHOLD_HIGH = int(
    os.getenv("ADAPTIVE_FALLBACK_THRESHOLD_HIGH", "0")
)
RESONANT_PEERS = [
    peer.strip().rstrip("/")
    for peer in os.getenv("RESONANT_PEERS", "").split(",")
    if peer.strip()
]
RESONANT_METRICS: Dict[str, int] = {
    "resonant_events_total": 0,
    "resonant_events_adaptive_total": 0,
    "resonant_events_replicated_out_total": 0,
    "resonant_events_replicated_in_total": 0,
    "resonant_replication_failures_total": 0,
    "resonant_quorum_failures_total": 0,
    "resonant_replay_rejections_total": 0,
    "resonant_signature_failures_total": 0,
    "resonant_chain_integrity_failures_total": 0,
    "resonant_recovery_runs_total": 0,
    "resonant_recovery_corrupt_lines_total": 0,
    "resonant_key_rotation_total": 0,
    "resonant_old_mode_fallback_total": 0,
    "resonant_fake_concepts_quarantined_total": 0,
    "resonant_rejected_non_real_total": 0,
    "resonant_rollbacks_total": 0,
}
ADAPTIVE_MISMATCH_COUNTERS: Dict[str, int] = {}
WWWMMM_GATE_ENABLED = os.getenv("WWWMMM_GATE_ENABLED", "true").lower() in {
    "1",
    "true",
    "yes",
    "on",
}
FAKE_CONCEPT_FILTER_ENABLED = os.getenv(
    "FAKE_CONCEPT_FILTER_ENABLED", "true"
).lower() in {
    "1",
    "true",
    "yes",
    "on",
}
ROLLOUT_PERCENTAGE = int(os.getenv("RESONANT_ROLLOUT_PERCENTAGE", "25"))
REAL_DATA_ONLY_MODE = os.getenv("REAL_DATA_ONLY_MODE", "true").lower() in {
    "1",
    "true",
    "yes",
    "on",
}


def _utc_iso_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _safe_json_dumps(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def _load_keyring() -> Dict[str, str]:
    ring: Dict[str, str] = {}
    raw = os.getenv("RESONANT_KEYS", "").strip()
    if raw:
        for item in raw.split(","):
            pair = item.strip()
            if not pair or ":" not in pair:
                continue
            key_id, secret_value = pair.split(":", 1)
            key_id = key_id.strip()
            secret_value = secret_value.strip()
            if key_id and secret_value:
                ring[key_id] = secret_value

    if not ring:
        default_kid = os.getenv("RESONANT_ACTIVE_KEY_ID", "k1")
        default_secret = os.getenv("RESONANT_SIGNING_KEY", "dev-resonant-key")
        ring[default_kid] = default_secret
    return ring


KEYRING: Dict[str, str] = _load_keyring()
ACTIVE_KEY_ID = os.getenv("RESONANT_ACTIVE_KEY_ID", next(iter(KEYRING.keys())))


def _canonical_event_message(
    event_type: str,
    payload: Dict[str, Any],
    writer_id: str,
    nonce: str,
    client_ts_ms: int,
    prev_hash: str,
) -> str:
    return "|".join(
        [
            event_type,
            _safe_json_dumps(payload),
            writer_id,
            nonce,
            str(client_ts_ms),
            prev_hash,
        ]
    )


def _sign_hmac_sha256(secret_value: str, message: str) -> str:
    return hmac.new(
        secret_value.encode("utf-8"), message.encode("utf-8"), hashlib.sha256
    ).hexdigest()


def _purge_old_nonces(now_ts: float) -> None:
    expired = [key for key, expires_at in NONCE_STORE.items() if expires_at <= now_ts]
    for key in expired:
        NONCE_STORE.pop(key, None)


def _is_replay_nonce(writer_id: str, nonce: str, now_ts: float) -> bool:
    key = f"{writer_id}:{nonce}"
    _purge_old_nonces(now_ts)
    if key in NONCE_STORE:
        return True
    NONCE_STORE[key] = now_ts + REPLAY_WINDOW_SECONDS
    return False


def _latest_chain_hash() -> str:
    if not EVENT_CHAIN:
        return "GENESIS"
    return str(EVENT_CHAIN[-1]["chain_hash"])


def _compute_chain_hash(event_record: Dict[str, Any]) -> str:
    canonical = _safe_json_dumps(event_record)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def _append_event_record(record: Dict[str, Any]) -> None:
    EVENT_CHAIN.append(record)
    if len(EVENT_CHAIN) > MAX_EVENT_CHAIN_SIZE:
        EVENT_CHAIN.pop(0)


def _segment_id_for_event(event_index: int) -> int:
    return ((event_index - 1) // max(1, RESONANT_SEGMENT_SIZE)) + 1


def _segment_path_for_event(event_index: int) -> Path:
    segment_id = _segment_id_for_event(event_index)
    return RESONANT_SEGMENTS_DIR / f"events-{segment_id:08d}.jsonl"


def _checkpoint_path() -> Path:
    return RESONANT_CHECKPOINTS_DIR / "latest-checkpoint.json"


def _persist_event_to_disk(event_record: Dict[str, Any]) -> None:
    segment_path = _segment_path_for_event(int(event_record["event_index"]))
    line = _safe_json_dumps(event_record) + "\n"
    with segment_path.open("a", encoding="utf-8") as file_handle:
        file_handle.write(line)


def _persist_checkpoint() -> None:
    checkpoint = {
        "timestamp_utc": _utc_iso_now(),
        "events_total": len(EVENT_CHAIN),
        "latest_event_index": EVENT_CHAIN[-1]["event_index"] if EVENT_CHAIN else 0,
        "latest_chain_hash": _latest_chain_hash(),
        "segment_size": RESONANT_SEGMENT_SIZE,
    }
    _checkpoint_path().write_text(_safe_json_dumps(checkpoint), encoding="utf-8")


def _event_exists(event_id: str) -> bool:
    return any(item.get("event_id") == event_id for item in EVENT_CHAIN)


def _restore_event_chain_from_disk() -> Dict[str, int]:
    EVENT_CHAIN.clear()
    loaded = 0
    corrupted = 0

    segment_paths = sorted(RESONANT_SEGMENTS_DIR.glob("events-*.jsonl"))
    for segment_path in segment_paths:
        with segment_path.open("r", encoding="utf-8") as file_handle:
            for line in file_handle:
                row = line.strip()
                if not row:
                    continue
                try:
                    event_record = json.loads(row)
                    if not isinstance(event_record, dict):
                        corrupted += 1
                        continue
                    if (
                        "chain_hash" not in event_record
                        or "event_index" not in event_record
                    ):
                        corrupted += 1
                        continue
                    EVENT_CHAIN.append(event_record)
                    if len(EVENT_CHAIN) > MAX_EVENT_CHAIN_SIZE:
                        EVENT_CHAIN.pop(0)
                    loaded += 1
                except json.JSONDecodeError:
                    corrupted += 1

    if corrupted > 0:
        RESONANT_METRICS["resonant_recovery_corrupt_lines_total"] += corrupted

    RESONANT_METRICS["resonant_recovery_runs_total"] += 1
    return {"loaded": loaded, "corrupted": corrupted}


async def _replicate_event_to_peer(
    peer_base_url: str, event_record: Dict[str, Any]
) -> bool:
    headers: Dict[str, str] = {}
    if RESONANT_REPLICATION_TOKEN:
        headers["x-resonant-replication-token"] = RESONANT_REPLICATION_TOKEN

    endpoint = f"{peer_base_url}/api/v1/resonant/replicate"
    try:
        async with httpx.AsyncClient(
            timeout=httpx.Timeout(RESONANT_REPLICATION_TIMEOUT)
        ) as client:
            response = await client.post(endpoint, json=event_record, headers=headers)
        return response.status_code < 300
    except Exception:
        return False


async def _replicate_with_quorum(event_record: Dict[str, Any]) -> Dict[str, Any]:
    if not RESONANT_PEERS:
        return {
            "required": 1,
            "acks": 1,
            "peers": 0,
            "ok": True,
        }

    tasks = [_replicate_event_to_peer(peer, event_record) for peer in RESONANT_PEERS]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    peer_acks = sum(1 for result in results if result is True)
    peer_failures = len(RESONANT_PEERS) - peer_acks

    RESONANT_METRICS["resonant_events_replicated_out_total"] += peer_acks
    RESONANT_METRICS["resonant_replication_failures_total"] += max(0, peer_failures)

    required = max(1, min(RESONANT_QUORUM_W, len(RESONANT_PEERS) + 1))
    total_acks = 1 + peer_acks  # local write counts as one ack
    ok = total_acks >= required
    if not ok:
        RESONANT_METRICS["resonant_quorum_failures_total"] += 1

    return {
        "required": required,
        "acks": total_acks,
        "peers": len(RESONANT_PEERS),
        "ok": ok,
    }


def _chain_integrity(limit: int = 1000) -> Dict[str, Any]:
    if not EVENT_CHAIN:
        return {
            "ok": True,
            "checked_events": 0,
            "reason": "empty-chain",
        }

    window = EVENT_CHAIN[-max(1, limit) :]
    previous_hash = (
        "GENESIS" if window[0]["event_index"] == 1 else window[0]["prev_hash"]
    )
    for item in window:
        if item["prev_hash"] != previous_hash:
            return {
                "ok": False,
                "checked_events": len(window),
                "broken_at_event_index": item["event_index"],
                "reason": "prev_hash_mismatch",
            }
        verification_copy = dict(item)
        chain_hash = verification_copy.pop("chain_hash")
        recomputed = _compute_chain_hash(verification_copy)
        if chain_hash != recomputed:
            return {
                "ok": False,
                "checked_events": len(window),
                "broken_at_event_index": item["event_index"],
                "reason": "chain_hash_mismatch",
            }
        previous_hash = item["chain_hash"]

    return {
        "ok": True,
        "checked_events": len(window),
    }


def _tide_pressure_ratio() -> float:
    return min(len(EVENT_CHAIN) / float(MAX_EVENT_CHAIN_SIZE), 1.0)


def _tide_state() -> str:
    pressure = _tide_pressure_ratio()
    if pressure >= TIDE_HIGH_PRESSURE_RATIO:
        return "high"
    if pressure >= TIDE_MEDIUM_PRESSURE_RATIO:
        return "medium"
    return "low"


def _fallback_threshold_for_tide(tide_state: str) -> int:
    if tide_state == "high":
        return max(0, ADAPTIVE_FALLBACK_THRESHOLD_HIGH)
    if tide_state == "medium":
        return max(0, ADAPTIVE_FALLBACK_THRESHOLD_MEDIUM)
    return max(0, ADAPTIVE_FALLBACK_THRESHOLD_LOW)


_RECOVERY_BOOT = _restore_event_chain_from_disk()


@app.post("/api/v1/music/ai-generate")
async def ai_generate_melody(request: Request, body: dict = Body(...)):
    prompt = (
        body.get("prompt")
        or "Krijo një melodi të nxehtë, ritmike, me motiv lalalalaaaa la/la, stil modern."
    )
    llm_prompt = f"Krijo një sekuencë notash solfezh (do, re, mi, fa, sol, la, si) për këtë kërkesë: {prompt}. Jep si JSON array: [{'{'}'note': 'do', 'duration': 'quarter', 'octave': 'mid'{'}'}, ...]. Mund të shtosh waveform, genre."
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(
                OCEAN_CORE_URL + "/api/v1/llm/generate",
                json={"prompt": llm_prompt, "max_tokens": 256},
            )
            resp.raise_for_status()
            data = resp.json()
            match = re.search(r"\[.*\]", data.get("text", ""), re.DOTALL)
            if match:
                seq = ast.literal_eval(match.group(0))
                sequence = [
                    {
                        "id": str(i + 1),
                        "note": n.get("note", "do"),
                        "duration": n.get("duration", "quarter"),
                        "octave": n.get("octave", "mid"),
                    }
                    for i, n in enumerate(seq)
                    if n.get("note") in SOLFEGE_FREQ
                ]
                waveform = data.get("waveform") or "sine"
                genre = data.get("genre") or "pop"
                return {"sequence": sequence, "waveform": waveform, "genre": genre}
    except Exception as e:
        return {"error": str(e)}
    return {"error": "AI nuk mundi të gjenerojë melodi"}


class ChatRequest(BaseModel):
    message: Optional[str] = None
    query: Optional[str] = None
    model: Optional[str] = None
    language_hint: Optional[str] = None


class DiscussionRequest(BaseModel):
    topic: str
    personas: Optional[List[str]] = None
    rounds: int = 2


class VisionAnalyzeRequest(BaseModel):
    image_base64: str
    prompt: str = "Describe this image in detail."


class VisionCreateRequest(BaseModel):
    prompt: str
    width: int = 1024
    height: int = 768


class DocumentReadRequest(BaseModel):
    content: str
    summarize: bool = True


class DocumentWriteRequest(BaseModel):
    topic: str
    language: str = "en"
    doc_type: str = "report"
    length: str = "medium"


class MusicCreateRequest(BaseModel):
    notes: List[str] = Field(
        default_factory=lambda: ["do", "re", "mi", "fa", "sol", "la", "si"]
    )
    durations: Optional[List[str]] = Field(
        default=None
    )  # Lista e kohëzgjatjeve për çdo notë: "whole", "half", "quarter", etc.
    octaves: Optional[List[str]] = Field(
        default=None
    )  # Lista e oktavave për çdo notë: "low", "mid", "high", etc.
    waveform: str = "sine"  # Lloji i valës: "sine", "square", "sawtooth", "triangle", "bass", "organ", "piano"
    tempo_bpm: int = 120  # Beats per minute
    output_format: str = "wav"  # Format: "wav" ose "mp3"
    genre: Optional[str] = (
        None  # Rrymë muzikore: "classical", "jazz", "electronic", "ambient", "rock", "hip-hop", "pop"
    )
    effects: Optional[List[str]] = Field(
        default=None
    )  # Efekte: ["reverb", "echo", "chorus", "vibrato", "tremolo", "distortion"]
    chords: Optional[List[str]] = Field(
        default=None
    )  # Akkorde për notes: ["major", "minor", "seventh", etc.]
    polyphony: bool = False  # Nëse True, luaj notat njëkohësisht (chord mode)


class BinaryAlgebraRequest(BaseModel):
    sequence: List[str] = Field(
        default_factory=lambda: ["do", "re", "mi", "fa", "sol", "la", "si"]
    )
    operation: str = "xor"


class VideoCreateRequest(BaseModel):
    title: str
    subtitles: Optional[List[str]] = None
    fps: int = 12
    seconds: int = 6


class VideoProcessRequest(BaseModel):
    video_base64: str


class AudioTranscribeRequest(BaseModel):
    audio_base64: str
    language: str = "auto"


class MemoryStoreRequest(BaseModel):
    text: str
    tags: List[str] = Field(default_factory=list)
    source: str = "manual"


class MemorySearchRequest(BaseModel):
    query: str
    limit: int = 10


class TaskCreateRequest(BaseModel):
    title: str
    objective: str
    priority: str = "normal"
    input_data: Dict[str, Any] = Field(default_factory=dict)


class WorkflowRunRequest(BaseModel):
    workflow: str = "global_multimodal"
    prompt: str
    language_hint: Optional[str] = None
    include_docs: bool = True
    include_vision: bool = False
    include_video: bool = False


class PublishToBlogRequest(BaseModel):
    doc_path: str
    title: Optional[str] = None
    description: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    publish_to_linkedin: bool = True


class ResonantEventWriteRequest(BaseModel):
    event_type: str
    payload: Dict[str, Any] = Field(default_factory=dict)
    writer_id: str
    nonce: str
    client_ts_ms: int
    signature: str
    key_id: Optional[str] = None


class ResonantKeyRotateRequest(BaseModel):
    new_key_id: Optional[str] = None
    new_secret: Optional[str] = None


class ResonantAdaptiveWriteRequest(BaseModel):
    event_type: str
    payload: Dict[str, Any] = Field(default_factory=dict)
    writer_id: Optional[str] = None
    nonce: Optional[str] = None
    client_ts_ms: Optional[int] = None
    signature: Optional[str] = None
    key_id: Optional[str] = None
    profile: Optional[str] = "adaptive"


class ResonantRolloutRequest(BaseModel):
    resonant_percentage: int = Field(ge=0, le=100)


def _legacy_percentage() -> int:
    return max(0, 100 - max(0, min(100, ROLLOUT_PERCENTAGE)))


def _fake_concept_reason(payload: Dict[str, Any]) -> Optional[str]:
    if not FAKE_CONCEPT_FILTER_ENABLED:
        return None
    if payload.get("fake_concept") is True or payload.get("is_fake") is True:
        return "payload-flagged-fake"

    text_blob = _safe_json_dumps(payload).lower()
    suspicious_tokens = ["fake concept", "fake_concept", "fabricated", "hallucinated"]
    for token in suspicious_tokens:
        if token in text_blob:
            return f"token:{token}"
    return None


def _non_real_writer_reason(writer_id: Optional[str]) -> Optional[str]:
    writer = (writer_id or "").strip().lower()
    if not writer:
        return "missing-writer-id"
    blocked_tokens = ("test", "demo", "fake", "mock", "sample", "synthetic")
    for token in blocked_tokens:
        if token in writer:
            return f"writer-id-contains:{token}"
    return None


async def _post_json(
    url: str, payload: Dict[str, Any], timeout: float = REQUEST_TIMEOUT
) -> Dict[str, Any]:
    async with httpx.AsyncClient(timeout=httpx.Timeout(timeout)) as client:
        response = await client.post(url, json=payload)
    if response.status_code >= 400:
        raise HTTPException(status_code=response.status_code, detail=response.text)
    return response.json()


async def _ocean_generate_text(prompt: str, max_tokens: int = 1024) -> str:
    payload = {
        "prompt": prompt,
        "max_tokens": max_tokens,
    }
    data = await _post_json(
        f"{OCEAN_CORE_URL}/api/v1/llm/generate", payload, timeout=120.0
    )
    text = str(data.get("text", "")).strip()
    return text or "Model returned empty output."


def _memory_score(query: str, text: str) -> int:
    query_terms = set(query.lower().split())
    text_terms = set(text.lower().split())
    return len(query_terms.intersection(text_terms))


@app.get("/")
async def root():
    return {
        "service": "9999/app.py",
        "status": "running",
        "multilingual": True,
        "features": [
            "chat",
            "discussion",
            "voice",
            "documents_reader",
            "documents_writer",
            "photo_vision_analyze",
            "photo_create",
            "video_create",
            "video_process",
            "music_create_mp3_mp4",
            "binary_algebra_do_re_mi",
            "memory_store_and_search",
            "task_engine",
            "workflow_engine",
            "external_video_generator_bridge",
            "resonant_status",
            "resonant_event_chain",
            "resonant_adaptive_ingest",
            "resonant_metrics",
            "system_self_check",
        ],
    }


@app.get("/health")
async def health():
    return {
        "status": "ok",
        "port": PORT,
        "model": MODEL,
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
    }


@app.get("/status")
async def status():
    _purge_old_nonces(time.time())
    return {
        "service": "9999/app.py",
        "status": "running",
        "port": PORT,
        "resonant": {
            "event_chain_len": len(EVENT_CHAIN),
            "active_key_id": ACTIVE_KEY_ID,
            "known_keys": sorted(KEYRING.keys()),
            "replay_window_seconds": REPLAY_WINDOW_SECONDS,
            "primary_profile": PRIMARY_RESONANT_PROFILE,
            "old_mode_on_mismatch": OLD_MODE_ON_MISMATCH,
        },
        "recovery_boot": _RECOVERY_BOOT,
        "timestamp_utc": _utc_iso_now(),
    }


@app.get("/api/v1/resonant/status")
async def resonant_status():
    integrity = _chain_integrity(limit=1000)
    now_ts = time.time()
    _purge_old_nonces(now_ts)
    tide_state = _tide_state()
    pressure_ratio = round(_tide_pressure_ratio(), 6)

    if not integrity["ok"]:
        RESONANT_METRICS["resonant_chain_integrity_failures_total"] += 1

    return {
        "status": "ok" if integrity["ok"] else "degraded",
        "ndb": {
            "signal_quality": 1.0 if integrity["ok"] else 0.6,
            "delta": 0.0 if integrity["ok"] else 0.4,
        },
        "tide": {
            "state": tide_state,
            "pressure_ratio": pressure_ratio,
            "fallback_threshold": _fallback_threshold_for_tide(tide_state),
        },
        "stigma": {
            "events_total": len(EVENT_CHAIN),
            "latest_chain_hash": _latest_chain_hash(),
            "integrity": integrity,
        },
        "security_envelope": {
            "active_key_id": ACTIVE_KEY_ID,
            "key_count": len(KEYRING),
            "recent_nonce_count": len(NONCE_STORE),
            "replay_window_seconds": REPLAY_WINDOW_SECONDS,
            "max_clock_skew_ms": MAX_CLOCK_SKEW_MS,
        },
        "replication": {
            "peers": RESONANT_PEERS,
            "quorum_write": max(1, min(RESONANT_QUORUM_W, len(RESONANT_PEERS) + 1)),
        },
        "kameleon": {
            "primary_profile": PRIMARY_RESONANT_PROFILE,
            "fallback_old_mode": OLD_MODE_ON_MISMATCH,
        },
        "rollout": {
            "resonant_percentage": max(0, min(100, ROLLOUT_PERCENTAGE)),
            "legacy_percentage": _legacy_percentage(),
            "rollback_one_action": "POST /api/v1/resonant/rollback",
        },
        "quality_gates": {
            "wwwmmm_gate_enabled": WWWMMM_GATE_ENABLED,
            "fake_concept_filter_enabled": FAKE_CONCEPT_FILTER_ENABLED,
            "real_data_only_mode": REAL_DATA_ONLY_MODE,
            "wwwmmm_verdict": "pass" if WWWMMM_GATE_ENABLED else "bypassed",
        },
        "timestamp_utc": _utc_iso_now(),
    }


@app.get("/api/v1/resonant/events")
async def resonant_events(limit: int = 100):
    bounded_limit = max(1, min(limit, 1000))
    return {
        "count": len(EVENT_CHAIN),
        "items": EVENT_CHAIN[-bounded_limit:],
        "latest_chain_hash": _latest_chain_hash(),
    }


@app.post("/api/v1/resonant/events")
async def resonant_events_write(req: ResonantEventWriteRequest):
    if REAL_DATA_ONLY_MODE:
        writer_reason = _non_real_writer_reason(req.writer_id)
        if writer_reason:
            RESONANT_METRICS["resonant_rejected_non_real_total"] += 1
            raise HTTPException(
                status_code=422, detail=f"non-real input rejected: {writer_reason}"
            )

        fake_reason = _fake_concept_reason(req.payload)
        if fake_reason:
            RESONANT_METRICS["resonant_rejected_non_real_total"] += 1
            raise HTTPException(
                status_code=422, detail=f"non-real input rejected: {fake_reason}"
            )

    now_ts = time.time()
    now_ms = int(now_ts * 1000)
    if abs(now_ms - req.client_ts_ms) > MAX_CLOCK_SKEW_MS:
        raise HTTPException(
            status_code=400, detail="client_ts_ms outside acceptable skew"
        )

    if _is_replay_nonce(req.writer_id, req.nonce, now_ts):
        RESONANT_METRICS["resonant_replay_rejections_total"] += 1
        raise HTTPException(
            status_code=409, detail="replay detected: nonce already used"
        )

    key_id = req.key_id or ACTIVE_KEY_ID
    secret_value = KEYRING.get(key_id)
    if not secret_value:
        raise HTTPException(status_code=401, detail="unknown key_id")

    prev_hash = _latest_chain_hash()
    canonical_message = _canonical_event_message(
        event_type=req.event_type,
        payload=req.payload,
        writer_id=req.writer_id,
        nonce=req.nonce,
        client_ts_ms=req.client_ts_ms,
        prev_hash=prev_hash,
    )
    expected_signature = _sign_hmac_sha256(secret_value, canonical_message)
    if not hmac.compare_digest(expected_signature, req.signature):
        RESONANT_METRICS["resonant_signature_failures_total"] += 1
        raise HTTPException(status_code=401, detail="invalid signature")

    event_index = len(EVENT_CHAIN) + 1
    event_record: Dict[str, Any] = {
        "event_index": event_index,
        "event_id": str(uuid.uuid4()),
        "event_type": req.event_type,
        "payload": req.payload,
        "writer_id": req.writer_id,
        "nonce": req.nonce,
        "client_ts_ms": req.client_ts_ms,
        "server_ts_utc": _utc_iso_now(),
        "key_id": key_id,
        "prev_hash": prev_hash,
        "signature": req.signature,
    }
    event_record["chain_hash"] = _compute_chain_hash(event_record)
    _append_event_record(event_record)
    _persist_event_to_disk(event_record)
    RESONANT_METRICS["resonant_events_total"] += 1

    if event_index % max(1, RESONANT_CHECKPOINT_EVERY) == 0:
        _persist_checkpoint()

    quorum = await _replicate_with_quorum(event_record)

    return {
        "status": "accepted" if quorum["ok"] else "accepted_local_only",
        "event_index": event_index,
        "chain_hash": event_record["chain_hash"],
        "prev_hash": prev_hash,
        "replication": quorum,
    }


@app.post("/api/v1/resonant/events/adaptive")
async def resonant_events_write_adaptive(req: ResonantAdaptiveWriteRequest):
    requested_profile = req.profile or PRIMARY_RESONANT_PROFILE
    normalized_profile = requested_profile.strip().lower()
    tide_state = _tide_state()
    fallback_threshold = _fallback_threshold_for_tide(tide_state)

    if REAL_DATA_ONLY_MODE:
        writer_reason = _non_real_writer_reason(req.writer_id)
        if writer_reason:
            RESONANT_METRICS["resonant_rejected_non_real_total"] += 1
            raise HTTPException(
                status_code=422, detail=f"non-real input rejected: {writer_reason}"
            )

        if not (req.signature and req.nonce and req.client_ts_ms and req.writer_id):
            RESONANT_METRICS["resonant_rejected_non_real_total"] += 1
            raise HTTPException(
                status_code=422,
                detail="non-real input rejected: signed modern envelope required in REAL_DATA_ONLY_MODE",
            )

    fake_reason = _fake_concept_reason(req.payload)
    if fake_reason:
        RESONANT_METRICS["resonant_fake_concepts_quarantined_total"] += 1
        RESONANT_METRICS["resonant_rejected_non_real_total"] += 1
        raise HTTPException(
            status_code=422, detail=f"non-real input rejected: {fake_reason}"
        )

    new_first_payload = {
        "profile": normalized_profile,
        "source": "adaptive",
        "compat": False,
        "signals": {
            "wwwmmm": True,
            "ndb": True,
            "stigma": True,
            "tide": True,
            "rezonance": True,
            "nanogrid": True,
        },
        "data": req.payload,
    }

    # First try the modern/new profile path.
    if req.signature and req.nonce and req.client_ts_ms and req.writer_id:
        try:
            result = await resonant_events_write(
                ResonantEventWriteRequest(
                    event_type=req.event_type,
                    payload=new_first_payload,
                    writer_id=req.writer_id,
                    nonce=req.nonce,
                    client_ts_ms=req.client_ts_ms,
                    signature=req.signature,
                    key_id=req.key_id,
                )
            )
            RESONANT_METRICS["resonant_events_adaptive_total"] += 1
            ADAPTIVE_MISMATCH_COUNTERS[req.writer_id] = 0
            result["mode"] = "new-first-modern"
            result["profile"] = normalized_profile
            result["tide_state"] = tide_state
            return result
        except HTTPException as modern_error:
            if not OLD_MODE_ON_MISMATCH:
                raise modern_error
            fallback_reason = modern_error.detail
            mismatch_key = req.writer_id
    else:
        fallback_reason = "missing modern signature envelope"
        mismatch_key = req.writer_id or f"legacy-{normalized_profile}"

    mismatch_count = ADAPTIVE_MISMATCH_COUNTERS.get(mismatch_key, 0) + 1
    ADAPTIVE_MISMATCH_COUNTERS[mismatch_key] = mismatch_count

    if mismatch_count <= fallback_threshold:
        raise HTTPException(
            status_code=428,
            detail={
                "message": "new profile is enforced before old mode fallback",
                "profile": normalized_profile,
                "tide_state": tide_state,
                "mismatch_count": mismatch_count,
                "fallback_threshold": fallback_threshold,
            },
        )

    # Fallback to old mode only if adaptation is allowed.
    if not ADAPTIVE_COMPAT_MODE:
        raise HTTPException(status_code=400, detail="adaptive compat mode is disabled")

    writer_id = req.writer_id or "legacy-adaptive"
    nonce = req.nonce or secrets.token_hex(12)
    client_ts_ms = req.client_ts_ms or int(time.time() * 1000)
    key_id = req.key_id or ACTIVE_KEY_ID
    secret_value = KEYRING.get(key_id)
    if not secret_value:
        raise HTTPException(status_code=401, detail="unknown key_id")

    prev_hash = _latest_chain_hash()
    old_mode_payload = {
        "profile": "old-modus",
        "source": "adaptive-fallback",
        "compat": True,
        "fallback_reason": fallback_reason,
        "target_profile": normalized_profile,
        "signals": {
            "wwwmmm": True,
            "ndb": True,
            "stigma": True,
            "tide": True,
            "rezonance": True,
            "nanogrid": True,
        },
        "data": req.payload,
    }
    canonical_message = _canonical_event_message(
        event_type=req.event_type,
        payload=old_mode_payload,
        writer_id=writer_id,
        nonce=nonce,
        client_ts_ms=client_ts_ms,
        prev_hash=prev_hash,
    )
    signature = _sign_hmac_sha256(secret_value, canonical_message)

    result = await resonant_events_write(
        ResonantEventWriteRequest(
            event_type=req.event_type,
            payload=old_mode_payload,
            writer_id=writer_id,
            nonce=nonce,
            client_ts_ms=client_ts_ms,
            signature=signature,
            key_id=key_id,
        )
    )
    RESONANT_METRICS["resonant_events_adaptive_total"] += 1
    RESONANT_METRICS["resonant_old_mode_fallback_total"] += 1
    ADAPTIVE_MISMATCH_COUNTERS[mismatch_key] = 0
    result["mode"] = "old-modus-fallback"
    result["profile"] = normalized_profile
    result["fallback_reason"] = fallback_reason
    result["tide_state"] = tide_state
    result["fallback_threshold"] = fallback_threshold
    return result


@app.post("/api/v1/resonant/replicate")
async def resonant_replicate_ingest(event_record: Dict[str, Any], request: Request):
    if RESONANT_REPLICATION_TOKEN:
        incoming = request.headers.get("x-resonant-replication-token", "")
        if incoming != RESONANT_REPLICATION_TOKEN:
            raise HTTPException(status_code=403, detail="replication token required")

    event_id = str(event_record.get("event_id", "")).strip()
    if not event_id:
        raise HTTPException(status_code=400, detail="event_id required")

    if _event_exists(event_id):
        return {"status": "duplicate", "event_id": event_id}

    required_fields = [
        "event_index",
        "prev_hash",
        "chain_hash",
        "signature",
        "writer_id",
    ]
    for key in required_fields:
        if key not in event_record:
            raise HTTPException(status_code=400, detail=f"missing field: {key}")

    local_prev_hash = _latest_chain_hash()
    if str(event_record["prev_hash"]) != local_prev_hash:
        raise HTTPException(status_code=409, detail="replication prev_hash mismatch")

    verification_copy = dict(event_record)
    incoming_chain_hash = str(verification_copy.pop("chain_hash"))
    recomputed_hash = _compute_chain_hash(verification_copy)
    if incoming_chain_hash != recomputed_hash:
        raise HTTPException(status_code=400, detail="invalid chain_hash")

    _append_event_record(event_record)
    _persist_event_to_disk(event_record)
    RESONANT_METRICS["resonant_events_replicated_in_total"] += 1
    RESONANT_METRICS["resonant_events_total"] += 1

    event_index = int(event_record["event_index"])
    if event_index % max(1, RESONANT_CHECKPOINT_EVERY) == 0:
        _persist_checkpoint()

    return {
        "status": "replicated",
        "event_id": event_id,
        "event_index": event_index,
    }


@app.post("/api/v1/resonant/keys/rotate")
async def resonant_rotate_keys(req: ResonantKeyRotateRequest, request: Request):
    global ACTIVE_KEY_ID

    admin_header = request.headers.get("x-resonant-admin-key", "")
    if not RESONANT_ADMIN_KEY or admin_header != RESONANT_ADMIN_KEY:
        raise HTTPException(status_code=403, detail="admin key required")

    next_key_id = req.new_key_id or f"k{len(KEYRING) + 1}"
    next_secret = req.new_secret or secrets.token_hex(32)
    KEYRING[next_key_id] = next_secret
    ACTIVE_KEY_ID = next_key_id
    RESONANT_METRICS["resonant_key_rotation_total"] += 1

    return {
        "status": "rotated",
        "active_key_id": ACTIVE_KEY_ID,
        "known_keys": sorted(KEYRING.keys()),
        "rotated_at_utc": _utc_iso_now(),
    }


@app.get("/api/v1/resonant/metrics")
async def resonant_metrics():
    integrity = _chain_integrity(limit=1000)
    tide_state = _tide_state()
    return {
        **RESONANT_METRICS,
        "resonant_chain_integrity_ok": 1 if integrity["ok"] else 0,
        "resonant_events_in_memory": len(EVENT_CHAIN),
        "tide_state": tide_state,
        "tide_pressure_ratio": round(_tide_pressure_ratio(), 6),
        "adaptive_fallback_threshold": _fallback_threshold_for_tide(tide_state),
        "adaptive_mismatch_active_writers": len(ADAPTIVE_MISMATCH_COUNTERS),
        "replay_window_seconds": REPLAY_WINDOW_SECONDS,
        "quorum_write_required": max(
            1, min(RESONANT_QUORUM_W, len(RESONANT_PEERS) + 1)
        ),
        "adaptive_compat_mode": ADAPTIVE_COMPAT_MODE,
        "primary_profile": PRIMARY_RESONANT_PROFILE,
        "old_mode_on_mismatch": OLD_MODE_ON_MISMATCH,
        "wwwmmm_gate_enabled": WWWMMM_GATE_ENABLED,
        "fake_concept_filter_enabled": FAKE_CONCEPT_FILTER_ENABLED,
        "real_data_only_mode": REAL_DATA_ONLY_MODE,
        "rollout_resonant_percentage": max(0, min(100, ROLLOUT_PERCENTAGE)),
        "rollout_legacy_percentage": _legacy_percentage(),
        "tide_medium_pressure_ratio": TIDE_MEDIUM_PRESSURE_RATIO,
        "tide_high_pressure_ratio": TIDE_HIGH_PRESSURE_RATIO,
        "timestamp_utc": _utc_iso_now(),
    }


@app.get("/api/v1/resonant/rollout")
async def resonant_rollout_status():
    return {
        "resonant_percentage": max(0, min(100, ROLLOUT_PERCENTAGE)),
        "legacy_percentage": _legacy_percentage(),
        "rollback_one_action": "POST /api/v1/resonant/rollback",
        "wwwmmm_gate_enabled": WWWMMM_GATE_ENABLED,
        "fake_concept_filter_enabled": FAKE_CONCEPT_FILTER_ENABLED,
        "timestamp_utc": _utc_iso_now(),
    }


@app.post("/api/v1/resonant/rollout")
async def resonant_rollout_set(req: ResonantRolloutRequest):
    global ROLLOUT_PERCENTAGE
    ROLLOUT_PERCENTAGE = max(0, min(100, req.resonant_percentage))
    return {
        "status": "updated",
        "resonant_percentage": ROLLOUT_PERCENTAGE,
        "legacy_percentage": _legacy_percentage(),
        "timestamp_utc": _utc_iso_now(),
    }


@app.post("/api/v1/resonant/rollback")
async def resonant_rollback_one_action():
    global ROLLOUT_PERCENTAGE
    ROLLOUT_PERCENTAGE = 0
    RESONANT_METRICS["resonant_rollbacks_total"] += 1
    return {
        "status": "rolled_back",
        "resonant_percentage": 0,
        "legacy_percentage": 100,
        "action": "one-action-rollback",
        "timestamp_utc": _utc_iso_now(),
    }


@app.get("/api/v1/tools/status")
async def tools_status() -> Dict[str, Any]:
    targets = {
        "ocean_core": f"{OCEAN_CORE_URL}/health",
        "video_generator": f"{VIDEO_GENERATOR_URL}/health",
    }
    checks: Dict[str, Any] = {}
    async with httpx.AsyncClient(timeout=httpx.Timeout(8.0)) as client:
        for key, url in targets.items():
            try:
                resp = await client.get(url)
                checks[key] = {
                    "status": "up" if resp.status_code < 500 else "degraded",
                    "code": resp.status_code,
                    "url": url,
                }
            except Exception as exc:
                checks[key] = {"status": "down", "url": url, "error": str(exc)}
    return {"checks": checks}


@app.post("/api/v1/chat")
async def chat(req: ChatRequest):
    prompt = req.message or req.query
    if not prompt:
        raise HTTPException(status_code=400, detail="message or query required")

    lang_hint = f"\nRespond in {req.language_hint}." if req.language_hint else ""
    effective_prompt = f"{GLOBAL_SYSTEM_PROMPT}{lang_hint}\n\nUser request:\n{prompt}"
    start = time.time()
    try:
        text = await _ocean_generate_text(effective_prompt, max_tokens=1024)
    except Exception:
        text = "Upstream model unavailable. Please retry in a few seconds."

    return {
        "response": text,
        "processing_time": round(time.time() - start, 2),
        "service": "9999/app.py",
    }


@app.post("/api/v1/discussion")
async def discussion(req: DiscussionRequest):
    payload = {
        "message": req.topic,
        "personas": req.personas or ["scientist", "engineer", "economist"],
        "rounds": req.rounds,
    }
    try:
        return await _post_json(
            f"{OCEAN_CORE_URL}/api/v1/debate", payload, timeout=120.0
        )
    except Exception:
        return {
            "status": "fallback",
            "message": "Debate service unavailable. Returning orchestration recommendation.",
            "next": [
                "Retry in 10 seconds",
                "Check ocean-core /health",
                "Check model availability",
            ],
        }


@app.post("/api/v1/voice/transcribe")
async def voice_transcribe(req: AudioTranscribeRequest):
    payload = {
        "audio_base64": req.audio_base64,
        "language": req.language,
    }
    try:
        return await _post_json(
            f"{OCEAN_CORE_URL}/api/v1/audio/transcribe", payload, timeout=120.0
        )
    except Exception:
        return {
            "status": "fallback",
            "message": "Voice transcription unavailable from ocean-core right now.",
            "next": [
                "Check /api/v1/tools/status",
                "Verify ocean-core multimodal dependencies",
            ],
        }


@app.post("/api/v1/vision/analyze")
async def vision_analyze(req: VisionAnalyzeRequest):
    payload = {
        "image_base64": req.image_base64,
        "prompt": req.prompt,
    }
    try:
        result = await _post_json(VISION_SERVICE_URL, payload, timeout=120.0)
        if isinstance(result, dict):
            result.setdefault("requested_model", VISION_TARGET_MODEL)
        return result
    except HTTPException as exc:
        raise HTTPException(
            status_code=exc.status_code,
            detail=(
                f"Vision upstream failed for model '{VISION_TARGET_MODEL}': "
                f"{exc.detail}"
            ),
        ) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=503,
            detail=(
                f"Vision service unavailable for model '{VISION_TARGET_MODEL}'. "
                f"Error: {exc}"
            ),
        ) from exc


@app.post("/api/v1/vision/create")
async def vision_create(req: VisionCreateRequest):
    if Image is None or ImageDraw is None:
        raise HTTPException(status_code=503, detail="Pillow is not installed")

    image = Image.new("RGB", (req.width, req.height), color=(18, 24, 38))
    draw = ImageDraw.Draw(image)
    now = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    lines = ["Kloud Vision Creator", req.prompt[:120], f"UTC: {now}"]
    y = 50
    for line in lines:
        draw.text((40, y), line, fill=(235, 245, 255))
        y += 42

    out_path = IMAGE_DIR / f"vision-{now}.png"
    image.save(out_path, format="PNG")
    with out_path.open("rb") as file_handle:
        image_b64 = base64.b64encode(file_handle.read()).decode("utf-8")

    return {"status": "success", "image_file": str(out_path), "image_base64": image_b64}


@app.post("/api/v1/document/read")
async def document_read(req: DocumentReadRequest):
    if not req.content.strip():
        raise HTTPException(status_code=400, detail="content is required")

    summary = None
    if req.summarize:
        summary_prompt = (
            "Summarize documents clearly and factually.\n\n"
            f"Summarize this:\n\n{req.content[:20000]}"
        )
        try:
            summary = await _ocean_generate_text(summary_prompt, max_tokens=900)
        except Exception:
            summary = "Summary unavailable right now."

    return {
        "status": "success",
        "chars": len(req.content),
        "words": len(req.content.split()),
        "summary": summary,
    }


@app.post("/api/v1/document/write")
async def document_write(req: DocumentWriteRequest):
    prompt = (
        f"Write a {req.doc_type} in {req.language}. "
        f"Length: {req.length}. Topic: {req.topic}."
    )
    try:
        text = await _ocean_generate_text(
            f"Write structured, professional documents.\n\n{prompt}",
            max_tokens=1400,
        )
    except Exception:
        text = "Document generation temporarily unavailable."

    ts = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    file_path = DOCS_DIR / f"{req.doc_type}-{ts}.md"
    file_path.write_text(text, encoding="utf-8")

    return {"status": "success", "file": str(file_path), "content": text}


@app.post("/api/v1/video/create")
async def video_create(req: VideoCreateRequest):
    if imageio is None:
        raise HTTPException(status_code=503, detail="imageio is not installed")
    if Image is None or ImageDraw is None:
        raise HTTPException(status_code=503, detail="Pillow is not installed")

    subtitles = req.subtitles or [
        req.title,
        "Kloud 9999 Video Creator",
        "Multimodal Automation",
    ]
    frame_count = max(req.fps * req.seconds, len(subtitles) * req.fps)
    ts = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    output_path = VIDEO_DIR / f"generated-{ts}.mp4"

    writer = imageio.get_writer(str(output_path), fps=req.fps)
    try:
        for index in range(frame_count):
            image = Image.new("RGB", (1280, 720), color=(10, 16, 28))
            draw = ImageDraw.Draw(image)
            line = subtitles[min(index // req.fps, len(subtitles) - 1)]
            draw.text((60, 300), f"{req.title}", fill=(255, 230, 120))
            draw.text((60, 360), line[:100], fill=(230, 245, 255))
            draw.text(
                (60, 410), f"frame {index + 1}/{frame_count}", fill=(170, 200, 255)
            )
            writer.append_data(np.array(image))
    finally:
        writer.close()

    return {"status": "success", "video_file": str(output_path), "format": "mp4"}


@app.post("/api/v1/video/create/external")
async def video_create_external(req: VideoCreateRequest):
    payload = {
        "topic": req.title,
        "tone": "professional",
        "duration_seconds": req.seconds,
    }
    try:
        return await _post_json(
            f"{VIDEO_GENERATOR_URL}/generate", payload, timeout=60.0
        )
    except Exception as exc:
        raise HTTPException(
            status_code=500, detail=f"External video generator failed: {exc}"
        ) from exc


@app.post("/api/v1/video/process")
async def video_process(req: VideoProcessRequest):
    ts = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    in_path = VIDEO_DIR / f"uploaded-{ts}.mp4"
    out_path = VIDEO_DIR / f"processed-{ts}.mp4"
    raw = base64.b64decode(req.video_base64)
    in_path.write_bytes(raw)

    cmd = [
        "ffmpeg",
        "-y",
        "-i",
        str(in_path),
        "-vf",
        "fps=15,scale=960:-1",
        "-c:v",
        "libx264",
        "-preset",
        "veryfast",
        "-an",
        str(out_path),
    ]
    process = subprocess.run(cmd, capture_output=True, text=True)
    if process.returncode != 0:
        raise HTTPException(
            status_code=500, detail=f"Video processing failed: {process.stderr[-300:]}"
        )

    return {
        "status": "success",
        "input_file": str(in_path),
        "output_file": str(out_path),
    }


@app.post("/api/v1/music/create")
async def music_create(req: MusicCreateRequest):
    """
    Krijon muzikë profesionale me:
    - Nota solfege + sharps/flats (do, do#, reb, re, etc.)
    - Kohëzgjatje (whole, half, quarter, eighth, sixteenth, thirty-second)
    - Oktava (ultra-low, low, mid, high, ultra-high)
    - Waveforms (sine, square, sawtooth, triangle, bass, organ, piano)
    - Genres (classical, jazz, electronic, ambient, rock, hip-hop, pop)
    - Effects (reverb, echo, chorus, vibrato, tremolo, distortion)
    - Chords (major, minor, seventh, diminished, augmented, sus2, sus4)
    - Polyphony (luaj disp nota njëkohësisht)
    """
    sample_rate = 44100
    audio = []

    # Genre auto-config
    if req.genre and req.genre.lower() in MUSIC_GENRES:
        genre_settings = MUSIC_GENRES[req.genre.lower()]
        if not req.effects:
            req.effects = []
            if genre_settings.get("reverb"):
                req.effects.append("reverb")
            if genre_settings.get("distortion"):
                req.effects.append("distortion")
            if genre_settings.get("chorus"):
                req.effects.append("chorus")

    num_notes = len(req.notes)
    durations = req.durations if req.durations else ["quarter"] * num_notes
    octaves = req.octaves if req.octaves else ["mid"] * num_notes
    chords = req.chords if req.chords else [""] * num_notes

    if len(durations) < num_notes:
        durations += ["quarter"] * (num_notes - len(durations))
    if len(octaves) < num_notes:
        octaves += ["mid"] * (num_notes - len(octaves))
    if len(chords) < num_notes:
        chords += [""] * (num_notes - len(chords))

    def semitone_offset_to_freq(base_freq, semitones):
        """Konverton semitone offset në frekuencë"""
        return base_freq * (2 ** (semitones / 12.0))

    def generate_wave(freq, duration_sec, waveform_type, apply_effects=True):
        """Gjeneron valë për një frekuencë dhe kohëzgjatje"""
        samples = int(sample_rate * duration_sec)
        wave_data = []

        for n in range(samples):
            t = n / sample_rate
            value = 0.0

            if waveform_type == "sine":
                value = 0.35 * math.sin(2 * math.pi * freq * t)
            elif waveform_type == "square":
                value = 0.25 * (1 if math.sin(2 * math.pi * freq * t) > 0 else -1)
            elif waveform_type == "sawtooth":
                value = 0.25 * (2 * (t * freq - math.floor(t * freq + 0.5)))
            elif waveform_type == "triangle":
                saw = 2 * (t * freq - math.floor(t * freq + 0.5))
                value = 0.25 * (2 * abs(saw) - 1)
            elif waveform_type == "bass":
                value = 0.4 * math.sin(2 * math.pi * freq * t) + 0.2 * math.sin(
                    2 * math.pi * (freq / 2) * t
                )
            elif waveform_type == "organ":
                value = (
                    0.25 * math.sin(2 * math.pi * freq * t)
                    + 0.15 * math.sin(2 * math.pi * freq * 3 * t)
                    + 0.10 * math.sin(2 * math.pi * freq * 5 * t)
                )
            elif waveform_type == "piano":
                envelope = math.exp(-3.0 * t / duration_sec)
                value = envelope * 0.35 * math.sin(2 * math.pi * freq * t)
            else:
                value = 0.35 * math.sin(2 * math.pi * freq * t)

            # Apply vibrato effect
            if apply_effects and req.effects and "vibrato" in req.effects:
                vibrato_rate = 5.0  # Hz
                vibrato_depth = 0.02
                freq_mod = freq * (
                    1 + vibrato_depth * math.sin(2 * math.pi * vibrato_rate * t)
                )
                value = 0.35 * math.sin(2 * math.pi * freq_mod * t)

            # Apply tremolo effect
            if apply_effects and req.effects and "tremolo" in req.effects:
                tremolo_rate = 4.0
                tremolo_depth = 0.3
                amp_mod = 1 - tremolo_depth * (
                    0.5 + 0.5 * math.sin(2 * math.pi * tremolo_rate * t)
                )
                value *= amp_mod

            wave_data.append(value)

        return wave_data

    for i, note_name in enumerate(req.notes):
        base_freq = SOLFEGE_FREQ.get(note_name.lower())
        if not base_freq:
            continue

        octave_mult = OCTAVE_MULTIPLIERS.get(octaves[i].lower(), 1.0)
        root_freq = base_freq * octave_mult

        duration_key = durations[i].lower()
        note_duration_ms = NOTE_DURATIONS.get(duration_key, 500)
        note_duration_sec = note_duration_ms / 1000.0

        waveform = req.waveform.lower()

        # Chord mode: luaj disa frekuenca njëkohësisht
        if chords[i] and chords[i].lower() in CHORDS:
            chord_intervals = CHORDS[chords[i].lower()]
            chord_waves = []
            for semitone_offset in chord_intervals:
                chord_freq = semitone_offset_to_freq(root_freq, semitone_offset)
                chord_waves.append(
                    generate_wave(
                        chord_freq, note_duration_sec, waveform, apply_effects=False
                    )
                )

            # Mix chord voices
            samples = len(chord_waves[0])
            for n in range(samples):
                mixed_value = sum(wave[n] for wave in chord_waves) / len(chord_waves)

                # Apply effects
                if req.effects and "distortion" in req.effects:
                    if abs(mixed_value) > 0.7:
                        mixed_value = 0.7 * (1 if mixed_value > 0 else -1)

                audio.append(int(mixed_value * 32767))

        elif req.polyphony and i < num_notes - 1:
            # Polyphony mode: mix current dhe next note
            next_freq = SOLFEGE_FREQ.get(req.notes[i + 1].lower(), root_freq)
            next_freq *= OCTAVE_MULTIPLIERS.get(
                octaves[min(i + 1, len(octaves) - 1)].lower(), 1.0
            )

            wave_data1 = generate_wave(root_freq, note_duration_sec, waveform)
            wave_data2 = generate_wave(next_freq, note_duration_sec, waveform)

            samples = min(len(wave_data1), len(wave_data2))
            for n in range(samples):
                mixed = (wave_data1[n] + wave_data2[n]) / 2
                audio.append(int(mixed * 32767))

        else:
            # Single note mode
            wave_data = generate_wave(root_freq, note_duration_sec, waveform)
            for value in wave_data:
                # Apply distortion
                if req.effects and "distortion" in req.effects:
                    if abs(value) > 0.7:
                        value = 0.7 * (1 if value > 0 else -1)
                audio.append(int(value * 32767))

    if not audio:
        raise HTTPException(status_code=400, detail="No valid notes provided")

    # Apply reverb/echo effects (post-processing)
    if req.effects and "reverb" in req.effects:
        reverb_delay = int(sample_rate * 0.05)  # 50ms
        reverb_decay = 0.3
        reverb_audio = audio[:]
        for i in range(reverb_delay, len(audio)):
            reverb_audio[i] += int(audio[i - reverb_delay] * reverb_decay)
            reverb_audio[i] = max(-32767, min(32767, reverb_audio[i]))
        audio = reverb_audio

    if req.effects and "echo" in req.effects:
        echo_delay = int(sample_rate * 0.5)  # 500ms
        echo_decay = 0.5
        echo_audio = audio[:]
        for repeat in range(2):
            offset = echo_delay * (repeat + 1)
            for i in range(len(audio)):
                if i + offset < len(echo_audio):
                    echo_audio[i + offset] += int(
                        audio[i] * (echo_decay ** (repeat + 1))
                    )
                    echo_audio[i + offset] = max(
                        -32767, min(32767, echo_audio[i + offset])
                    )
        audio = echo_audio

    ts = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    wav_path = MUSIC_DIR / f"melody-{ts}.wav"
    with wave.open(str(wav_path), "w") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(struct.pack("<" + "h" * len(audio), *audio))

    if req.output_format.lower() == "mp3":
        mp3_path = MUSIC_DIR / f"melody-{ts}.mp3"
        cmd = ["ffmpeg", "-y", "-i", str(wav_path), str(mp3_path)]
        proc = subprocess.run(cmd, capture_output=True, text=True)
        if proc.returncode == 0:
            return FileResponse(
                str(mp3_path), media_type="audio/mpeg", filename=f"melody-{ts}.mp3"
            )

    return FileResponse(
        str(wav_path), media_type="audio/wav", filename=f"melody-{ts}.wav"
    )


@app.post("/api/v1/algebra/binary-solfege")
async def algebra_binary_solfege(req: BinaryAlgebraRequest):
    binary_map = {
        "do": "001",
        "re": "010",
        "mi": "011",
        "fa": "100",
        "sol": "101",
        "so": "101",
        "la": "110",
        "si": "111",
    }
    bits: List[str] = []
    for item in req.sequence:
        mapped = binary_map.get(item.lower())
        if mapped:
            bits.append(mapped)
    if not bits:
        raise HTTPException(
            status_code=400, detail="Sequence has no valid solfege notes"
        )

    values = [int(item, 2) for item in bits]
    result = values[0]
    op = req.operation.lower()
    for value in values[1:]:
        if op == "xor":
            result ^= value
        elif op == "and":
            result &= value
        elif op == "or":
            result |= value
        else:
            raise HTTPException(status_code=400, detail="operation must be xor|and|or")

    return {
        "input_notes": req.sequence,
        "binary_values": bits,
        "operation": op,
        "result_decimal": result,
        "result_binary": format(result, "03b"),
    }


@app.post("/api/v1/memory/store")
async def memory_store(req: MemoryStoreRequest):
    if not req.text.strip():
        raise HTTPException(status_code=400, detail="text is required")
    memory_id = str(uuid.uuid4())[:12]
    item = {
        "id": memory_id,
        "text": req.text,
        "tags": req.tags,
        "source": req.source,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    MEMORY_STORE.append(item)
    return {"status": "stored", "memory": item, "count": len(MEMORY_STORE)}


@app.post("/api/v1/memory/search")
async def memory_search(req: MemorySearchRequest):
    if not req.query.strip():
        raise HTTPException(status_code=400, detail="query is required")
    scored = []
    for item in MEMORY_STORE:
        score = _memory_score(req.query, item.get("text", ""))
        if score > 0:
            scored.append({"score": score, **item})
    scored.sort(key=lambda item: item["score"], reverse=True)
    return {"query": req.query, "results": scored[: max(1, req.limit)]}


@app.get("/api/v1/memory")
async def memory_list(limit: int = 50):
    return {
        "count": len(MEMORY_STORE),
        "items": MEMORY_STORE[-max(1, min(limit, 200)) :],
    }


@app.post("/api/v1/tasks/create")
async def tasks_create(req: TaskCreateRequest):
    task_id = str(uuid.uuid4())[:12]
    item = {
        "id": task_id,
        "title": req.title,
        "objective": req.objective,
        "priority": req.priority,
        "input_data": req.input_data,
        "status": "created",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "result": None,
    }
    TASK_STORE[task_id] = item
    return item


@app.get("/api/v1/tasks")
async def tasks_list():
    return {"count": len(TASK_STORE), "tasks": list(TASK_STORE.values())}


@app.get("/api/v1/tasks/{task_id}")
async def tasks_get(task_id: str):
    task = TASK_STORE.get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="task not found")
    return task


@app.post("/api/v1/tasks/{task_id}/run")
async def tasks_run(task_id: str):
    task = TASK_STORE.get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="task not found")

    task["status"] = "running"
    task["updated_at"] = datetime.now(timezone.utc).isoformat()

    prompt = f"Task: {task['title']}\nObjective: {task['objective']}\nInput: {task['input_data']}"
    task_prompt = (
        GLOBAL_SYSTEM_PROMPT + "\nExecute tasks with actionable outputs.\n\n" + prompt
    )
    try:
        output = await _ocean_generate_text(task_prompt, max_tokens=1200)
        if not output:
            output = "Task finished with empty model output."
        task["result"] = output
        task["status"] = "completed"
    except Exception as exc:
        task["result"] = f"Task run failed: {exc}"
        task["status"] = "failed"

    task["updated_at"] = datetime.now(timezone.utc).isoformat()
    return task


@app.post("/api/v1/workflows/run")
async def workflows_run(req: WorkflowRunRequest):
    steps: List[Dict[str, Any]] = []

    chat_result = await chat(
        ChatRequest(message=req.prompt, language_hint=req.language_hint)
    )
    steps.append({"step": "chat", "ok": True, "result": chat_result})

    if req.include_docs:
        doc_result = await document_write(
            DocumentWriteRequest(
                topic=req.prompt,
                language=req.language_hint or "en",
                doc_type="report",
                length="medium",
            )
        )
        steps.append({"step": "document_write", "ok": True, "result": doc_result})

    if req.include_video:
        video_result = await video_create(
            VideoCreateRequest(
                title=f"Workflow video: {req.prompt[:60]}",
                subtitles=["Kloud 9999", req.prompt[:90], "Workflow complete"],
                fps=10,
                seconds=5,
            )
        )
        steps.append({"step": "video_create", "ok": True, "result": video_result})

    return {
        "workflow": req.workflow,
        "status": "completed",
        "steps": steps,
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
    }


@app.get("/api/v1/files/list")
async def files_list(kind: str = "all"):
    mapping = {
        "music": MUSIC_DIR,
        "video": VIDEO_DIR,
        "images": IMAGE_DIR,
        "docs": DOCS_DIR,
    }
    if kind == "all":
        result = {}
        for key, key_folder in mapping.items():
            result[key] = [
                entry.name for entry in key_folder.glob("*") if entry.is_file()
            ]
        return result
    target_folder: Optional[Path] = mapping.get(kind)
    if not target_folder:
        raise HTTPException(
            status_code=400, detail="kind must be one of: all,music,video,images,docs"
        )
    return {
        "kind": kind,
        "files": [entry.name for entry in target_folder.glob("*") if entry.is_file()],
    }


@app.get("/api/v1/system/self-check")
async def system_self_check():
    tools = await tools_status()
    return {
        "service": "9999/app.py",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "memory_items": len(MEMORY_STORE),
        "tasks_total": len(TASK_STORE),
        "tools": tools,
        "output_counts": {
            "music": len([entry for entry in MUSIC_DIR.glob("*") if entry.is_file()]),
            "video": len([entry for entry in VIDEO_DIR.glob("*") if entry.is_file()]),
            "images": len([entry for entry in IMAGE_DIR.glob("*") if entry.is_file()]),
            "docs": len([entry for entry in DOCS_DIR.glob("*") if entry.is_file()]),
        },
    }


@app.post("/api/v1/publish/blog")
async def publish_blog(req: PublishToBlogRequest):
    """Publikim i dokumentave në GitHub kloud-blog repo"""
    try:
        doc_path = Path(req.doc_path)
        if not doc_path.exists():
            raise HTTPException(
                status_code=404, detail=f"Document not found: {req.doc_path}"
            )

        # Try to import and use BlogPublisher
        try:
            import sys

            sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
            from publish_to_blog import BlogPublisher

            publisher = BlogPublisher()
            if not publisher.clone_or_update_repo():
                return {"status": "error", "message": "Failed to sync blog repository"}

            # Prepare publication
            content = doc_path.read_text(encoding="utf-8")
            metadata = {
                "title": req.title or doc_path.stem,
                "description": req.description or content[:200],
                "tags": req.tags,
                "date": datetime.now(timezone.utc).isoformat(),
                "source": "kloud-9999",
            }

            # Write to blog
            post_filename = f"{datetime.now().strftime('%Y-%m-%d')}-{doc_path.stem}.md"
            post_path = publisher.posts_dir / post_filename
            post_path.write_text(
                f"---\n{json.dumps(metadata, indent=2)}\n---\n\n{content}",
                encoding="utf-8",
            )

            # Git commit and push
            git_add = subprocess.run(
                ["git", "-C", str(publisher.blog_dir), "add", "-A"],
                capture_output=True,
                text=True,
            )
            if git_add.returncode != 0:
                return {"status": "error", "message": git_add.stderr.strip()}

            git_commit = subprocess.run(
                [
                    "git",
                    "-C",
                    str(publisher.blog_dir),
                    "commit",
                    "-m",
                    f"Publish: {metadata['title']}",
                ],
                capture_output=True,
                text=True,
            )
            if (
                git_commit.returncode != 0
                and "nothing to commit" not in git_commit.stdout.lower()
            ):
                return {"status": "error", "message": git_commit.stderr.strip()}

            git_push = subprocess.run(
                ["git", "-C", str(publisher.blog_dir), "push", "origin", "main"],
                capture_output=True,
                text=True,
            )
            if git_push.returncode != 0:
                return {"status": "error", "message": git_push.stderr.strip()}

            return {
                "status": "success",
                "published": True,
                "post_file": post_filename,
                "metadata": metadata,
                "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            }
        except ImportError:
            return {
                "status": "warning",
                "published": False,
                "message": "BlogPublisher not available, but route is functional",
                "would_publish": req.title or doc_path.stem,
            }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        }


@app.get("/api/v1/publish/status")
async def publish_status():
    """Status i publishing system"""
    return {
        "status": "operational",
        "service": "BlogPublisher (9999)",
        "endpoints": {
            "publish": "POST /api/v1/publish/blog",
            "status": "GET /api/v1/publish/status",
        },
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host=os.getenv("HOST", "0.0.0.0"), port=PORT)
