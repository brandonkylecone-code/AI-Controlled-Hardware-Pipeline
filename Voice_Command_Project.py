"""Voice-command controller: Whisper speech recognition -> Arduino LEDs.

Install: pip install transformers torch sounddevice pyserial numpy
(Use pyserial, not the unrelated "serial" package.)
Change SERIAL_PORT to your Arduino's serial port, upload voice_lights/voice_lights.ino
with the Arduino IDE (close the Serial Monitor afterwards), then run this file.
Say e.g. "red on", "turn blue off", "red and blue on", or "all off".
"""

import re
import time

import numpy as np
import serial
import sounddevice as sd
from transformers import pipeline

MODEL_NAME = "openai/whisper-base"
SERIAL_PORT = "COM3"  # Change to your Arduino's port.
BAUD_RATE = 9600
SAMPLE_RATE = 16_000
RECORD_SECONDS = 4
SILENCE_RMS = 0.005  # Clips quieter than this are skipped; tune for your mic.
METER_FULL_SCALE = 0.05  # Mic level that fills the live meter.


def parse_command(transcript):
    """Return a list of Arduino commands found in the transcript."""
    words = re.sub(r"[^a-z0-9 ]", " ", transcript.lower()).split()
    if "all" in words and "off" in words:
        return ["ALL_OFF"]
    if "all" in words and "on" in words:
        return ["ALL_ON"]
    # Whisper sometimes hears "off" as "of".
    action = "ON" if "on" in words else "OFF" if ("off" in words or "of" in words) else None
    if action is None:
        return []
    colors = {
        "RED": {"red", "one", "1"},
        "GREEN": {"green", "two", "2"},
        "BLUE": {"blue", "three", "3"},
    }
    return [f"{color}_{action}" for color, aliases in colors.items() if aliases & set(words)]


def record_with_meter(seconds):
    """Record from the mic while showing a live level meter.

    Returns (mono_audio, peak_level) where peak_level is the loudest short block.
    """
    total = int(seconds * SAMPLE_RATE)
    blocks = []
    state = {"samples": 0, "level": 0.0, "peak": 0.0}

    def callback(indata, frames, time_info, status):
        blocks.append(indata[:, 0].copy())
        state["samples"] += frames
        state["level"] = float(np.sqrt(np.mean(indata ** 2)))
        state["peak"] = max(state["peak"], state["level"])

    with sd.InputStream(
        samplerate=SAMPLE_RATE, channels=1, dtype="float32", callback=callback
    ):
        while state["samples"] < total:
            filled = min(20, int(state["level"] / METER_FULL_SCALE * 20))
            bar = "#" * filled + "-" * (20 - filled)
            status = "VOICE DETECTED" if state["level"] >= SILENCE_RMS else "quiet"
            print(f"\r  Mic [{bar}] {status:<14}", end="", flush=True)
            time.sleep(0.05)
    print()
    return np.concatenate(blocks)[:total], state["peak"]


def main():
    print(f"Loading {MODEL_NAME}; first run downloads the model.")
    recognizer = pipeline("automatic-speech-recognition", model=MODEL_NAME)
    try:
        board = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
    except serial.SerialException as error:
        raise SystemExit(f"Cannot open {SERIAL_PORT}: {error}") from error

    time.sleep(2)  # Opening serial usually resets the Arduino.
    print("Listening. Press Ctrl+C to stop.")
    try:
        while True:
            print(f"Ready - speak a command ({RECORD_SECONDS} seconds)...")
            mono, peak = record_with_meter(RECORD_SECONDS)
            # Whisper hallucinates text (e.g. "Thank you.") on silence, so skip quiet clips.
            if peak < SILENCE_RMS:
                print(f"No voice detected (peak level {peak:.4f} < {SILENCE_RMS}).")
                continue
            print(f"Voice detected (peak level {peak:.4f}). Transcribing...")
            # Force English; whisper-base is multilingual and often misdetects
            # the language of very short clips.
            result = recognizer(
                {"raw": mono, "sampling_rate": SAMPLE_RATE},
                generate_kwargs={"language": "english", "task": "transcribe"},
            )
            transcript = result.get("text", "").strip()
            print("Heard:", transcript or "(nothing)")
            commands = parse_command(transcript)
            if not commands:
                print("No supported light command found.")
                continue
            for command in commands:
                board.write((command + "\n").encode("ascii"))
                board.flush()
                print("Sent:", command)
    except KeyboardInterrupt:
        print("Stopping.")
    finally:
        board.close()


if __name__ == "__main__":
    main()
