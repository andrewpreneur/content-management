#!/usr/bin/env python3
"""Transcribe a video/audio file with faster-whisper.

Writes <out>/transcript.json (segments + word timings), transcript.txt and captions.srt.

Usage:
  python3 tools/transcribe.py SOURCE.mp4 OUT_DIR [--model small.en] [--lang en]
Install once: pip install faster-whisper
"""
import argparse, json, os, subprocess, tempfile


def srt_time(t):
    h, rem = divmod(t, 3600)
    m, s = divmod(rem, 60)
    return f"{int(h):02d}:{int(m):02d}:{int(s):02d},{int(round((s % 1) * 1000)):03d}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("source")
    ap.add_argument("out")
    ap.add_argument("--model", default="small.en")
    ap.add_argument("--lang", default="en")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)

    from faster_whisper import WhisperModel

    with tempfile.TemporaryDirectory() as td:
        wav = os.path.join(td, "a.wav")
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", a.source, "-vn", "-ac", "1", "-ar", "16000", wav], check=True)
        import numpy as np, wave
        with wave.open(wav) as w:
            audio = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768.0
        model = WhisperModel(a.model, device="cpu", compute_type="int8")
        segs, info = model.transcribe(audio, language=a.lang, word_timestamps=True, vad_filter=True)
        out = []
        for s in segs:
            out.append({
                "start": round(s.start, 2), "end": round(s.end, 2), "text": s.text.strip(),
                "words": [{"w": w.word.strip(), "s": round(w.start, 2), "e": round(w.end, 2)} for w in (s.words or [])],
            })

    json.dump({"source": a.source, "language": a.lang, "segments": out}, open(os.path.join(a.out, "transcript.json"), "w"), indent=1)
    with open(os.path.join(a.out, "transcript.txt"), "w") as f:
        for s in out:
            f.write(f"[{s['start']:7.2f}] {s['text']}\n")
    with open(os.path.join(a.out, "captions.srt"), "w") as f:
        for i, s in enumerate(out, 1):
            f.write(f"{i}\n{srt_time(s['start'])} --> {srt_time(s['end'])}\n{s['text']}\n\n")
    print(f"{len(out)} segments → {a.out}")


if __name__ == "__main__":
    main()
