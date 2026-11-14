"""Registra delivery/video.html con un browser automatico e lo codifica in MP4 (H.264 + AAC muto), ≤50 s.

Uso: <venv con playwright>/bin/python delivery/render_video.py
Output: delivery/out/idea.mp4
"""
from __future__ import annotations

import subprocess
import time
from pathlib import Path

from playwright.sync_api import sync_playwright

HERE = Path(__file__).resolve().parent
OUT = HERE / "out"
SIZE = {"width": 1280, "height": 720}

with sync_playwright() as p:
    browser = p.chromium.launch(args=["--autoplay-policy=no-user-gesture-required"])
    ctx = browser.new_context(viewport=SIZE, record_video_dir=str(OUT / "raw"), record_video_size=SIZE)
    page = ctx.new_page()
    t0 = time.monotonic()
    page.goto((HERE / "video.html").as_uri())
    page.wait_for_function("() => window.__started", timeout=60000)
    offset = time.monotonic() - t0
    page.wait_for_function("() => window.__done", timeout=120000)
    raw = page.video.path()
    ctx.close()
    browser.close()

print(f"raw={raw} offset={offset:.2f}s")
mp4 = OUT / "idea.mp4"
subprocess.run(
    [
        "ffmpeg", "-v", "error", "-y", "-ss", f"{offset:.2f}", "-i", str(raw),
        "-i", str(OUT / "music.m4a"),
        "-map", "0:v:0", "-map", "1:a:0", "-t", "47.9",
        "-vf", "scale=-2:720,fps=30,format=yuv420p",
        "-c:v", "libx264", "-preset", "medium", "-crf", "22", "-maxrate", "3M", "-bufsize", "6M",
        "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart", "-shortest", str(mp4),
    ],
    check=True,
)
print(mp4)
