from __future__ import annotations

import asyncio
import os
import subprocess
from pathlib import Path

import edge_tts


async def _save_tts(text: str, output_path: Path, voice: str, rate: str) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    communicate = edge_tts.Communicate(text=text, voice=voice, rate=rate)
    await communicate.save(str(output_path))


def text_to_speech(
    text: str,
    output_path: Path,
    voice: str = "pl-PL-ZofiaNeural",
    rate: str = "+0%",
) -> Path:
    # Edge TTS nie wymaga płatnego API, ale korzysta z usługi online Microsoftu.
    try:
        asyncio.run(_save_tts(text, output_path, voice, rate))
        return output_path
    except Exception:
        if os.name != "nt":
            raise
        return _windows_sapi_fallback(text, output_path.with_suffix(".wav"))


def _windows_sapi_fallback(text: str, output_path: Path) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    text_path = output_path.with_suffix(".txt")
    script_path = output_path.with_suffix(".ps1")
    text_path.write_text(text, encoding="utf-8")
    script_path.write_text(
        """
param(
  [Parameter(Mandatory=$true)][string]$TextPath,
  [Parameter(Mandatory=$true)][string]$OutputPath
)
$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Speech
$text = [IO.File]::ReadAllText($TextPath, [Text.Encoding]::UTF8)
$speaker = New-Object System.Speech.Synthesis.SpeechSynthesizer
$speaker.Rate = 0
$speaker.Volume = 100
$speaker.SetOutputToWaveFile($OutputPath)
$speaker.Speak($text)
$speaker.Dispose()
""".strip(),
        encoding="utf-8",
    )
    subprocess.run(
        ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(script_path), str(text_path), str(output_path)],
        check=True,
    )
    return output_path
