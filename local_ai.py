"""Offline-first local AI helpers for UNIVERSE AI STUDIO.

No hosted AI API is used. Text generation talks to a local Ollama server.
Optional image generation can be provided by a local ComfyUI installation.
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import tempfile
import urllib.error
import urllib.request
from pathlib import Path


OLLAMA_DEFAULT = "http://127.0.0.1:11434"
COMFYUI_DEFAULT = "http://127.0.0.1:8188"


def _get_json(url: str, timeout: int = 3):
    request = urllib.request.Request(url, headers={"Accept": "application/json"})
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


def ollama_status(base_url: str = OLLAMA_DEFAULT):
    try:
        payload = _get_json(base_url.rstrip("/") + "/api/tags")
        models = [item.get("name", "") for item in payload.get("models", []) if item.get("name")]
        return {"connected": True, "models": models, "error": ""}
    except Exception as exc:
        return {"connected": False, "models": [], "error": str(exc)}


def ollama_generate(prompt: str, model: str, base_url: str = OLLAMA_DEFAULT,
                    system: str = "You are UNIVERSE AI, a helpful Hindi and English filmmaking assistant.",
                    timeout: int = 240):
    if not prompt.strip():
        raise ValueError("Prompt cannot be empty.")
    if not model.strip():
        raise ValueError("Select an installed local Ollama model.")
    payload = json.dumps({
        "model": model,
        "prompt": prompt,
        "system": system,
        "stream": False,
        "options": {"temperature": 0.75}
    }).encode("utf-8")
    request = urllib.request.Request(
        base_url.rstrip("/") + "/api/generate",
        data=payload,
        headers={"Content-Type": "application/json"}
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            result = json.loads(response.read().decode("utf-8"))
    except urllib.error.URLError as exc:
        raise RuntimeError(f"Local Ollama request failed: {exc}") from exc
    answer = (result.get("response") or "").strip()
    if not answer:
        raise RuntimeError("Local model returned an empty response.")
    return answer


def comfyui_status(base_url: str = COMFYUI_DEFAULT):
    try:
        payload = _get_json(base_url.rstrip("/") + "/system_stats")
        return {"connected": True, "stats": payload, "error": ""}
    except Exception as exc:
        return {"connected": False, "stats": {}, "error": str(exc)}


def offline_speak(text: str, output_path: str, rate: int = 165):
    """Create speech with locally installed OS voices via pyttsx3."""
    if not text.strip():
        raise ValueError("Dialogue cannot be empty.")
    try:
        import pyttsx3
    except ImportError as exc:
        raise RuntimeError("Offline voice package missing. Install pyttsx3 locally.") from exc
    engine = pyttsx3.init()
    engine.setProperty("rate", int(rate))
    engine.save_to_file(text, output_path)
    engine.runAndWait()
    engine.stop()
    if not os.path.exists(output_path) or os.path.getsize(output_path) < 100:
        raise RuntimeError("Speech file was not created. Check that an OS voice is installed.")
    return output_path


def ffmpeg_available():
    return shutil.which("ffmpeg") is not None


def render_image_slideshow(image_files, output_path: str, seconds_per_image: int = 4,
                           audio_path: str | None = None, width: int = 1920,
                           height: int = 1080):
    """Render a basic offline MP4 slideshow from local images, optionally with voice audio."""
    if not image_files:
        raise ValueError("Upload at least one image.")
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        raise RuntimeError("FFmpeg is not installed or is not on PATH.")
    if any(not Path(path).exists() for path in image_files):
        raise FileNotFoundError("One or more uploaded image files are missing.")

    with tempfile.TemporaryDirectory(prefix="universe_ai_") as tmp:
        concat_path = Path(tmp) / "images.txt"
        with concat_path.open("w", encoding="utf-8") as handle:
            for path in image_files:
                safe_path = str(Path(path).resolve()).replace("'", "'\\''")
                handle.write(f"file '{safe_path}'\n")
                handle.write(f"duration {max(1, int(seconds_per_image))}\n")
            safe_path = str(Path(image_files[-1]).resolve()).replace("'", "'\\''")
            handle.write(f"file '{safe_path}'\n")

        command = [
            ffmpeg, "-y", "-f", "concat", "-safe", "0", "-i", str(concat_path),
            "-vf", f"scale={width}:{height}:force_original_aspect_ratio=decrease,pad={width}:{height}:(ow-iw)/2:(oh-ih)/2,format=yuv420p",
            "-r", "30", "-c:v", "libx264"
        ]
        if audio_path and Path(audio_path).exists():
            command += ["-i", audio_path, "-c:a", "aac", "-shortest"]
        else:
            command += ["-an"]
        command += ["-movflags", "+faststart", output_path]
        result = subprocess.run(command, capture_output=True, text=True, timeout=900)
        if result.returncode != 0:
            raise RuntimeError((result.stderr or "FFmpeg render failed")[-2500:])
    return output_path
