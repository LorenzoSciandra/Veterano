"""Colonna sonora sintetica sincronizzata con le scene di video.html (nessun campione esterno, nessun diritto).

Problema (0-9.6 s): tensione - bordone dissonante, battito, crescendo.
Come (9.6-15.6): scioglimento in maggiore, arpeggio leggero.  Cosa (15.6-17.8): apertura luminosa.
Demo (17.8-44.5): tappeto ottimista C-G-Am-F.  Finale (44.5-47.9): sospensione, poi colpo d'impatto.
Uso: python delivery/make_music.py delivery/out/music.wav
"""
import sys
import wave

import numpy as np

SR = 48000
DUR = 48.0
N = int(SR * DUR)
rng = np.random.default_rng(7)
L = np.zeros(N)
R = np.zeros(N)


def t_of(a, b):
    i0, i1 = int(a * SR), int(b * SR)
    return i0, i1, np.arange(i1 - i0) / SR


def env(n, a=0.5, r=0.8):
    e = np.ones(n)
    na, nr = int(a * SR), int(r * SR)
    if na:
        e[:na] = np.linspace(0, 1, na)
    if nr:
        e[-nr:] *= np.linspace(1, 0, nr)
    return e


def tone(f, t, harm=(1, .5, .25, .12)):
    return sum(h * np.sin(2 * np.pi * f * (k + 1) * t) for k, h in enumerate(harm)) / sum(harm)


def add(a, b, sig, pan=0.0, gain=1.0):
    i0 = int(a * SR)
    sig = sig[: max(0, min(len(sig), N - i0))]
    L[i0:i0 + len(sig)] += sig * gain * (1 - pan) / 2 * 2 ** 0.5
    R[i0:i0 + len(sig)] += sig * gain * (1 + pan) / 2 * 2 ** 0.5


def lowpass(x, alpha):
    y = np.empty_like(x)
    acc = 0.0
    for i in range(0, len(x), 1):
        acc += alpha * (x[i] - acc)
        y[i] = acc
    return y


NOTE = {"C3": 130.81, "E3": 164.81, "G3": 196.0, "A2": 110.0, "F2": 87.31, "G2": 98.0, "C4": 261.63, "E4": 329.63,
        "G4": 392.0, "A3": 220.0, "B3": 246.94, "D4": 293.66, "F3": 174.61, "A4": 440.0, "C5": 523.25, "F4": 349.23,
        "B4": 493.88, "D5": 587.33, "E5": 659.25, "G5": 783.99}

# --- 1. problema: tensione -------------------------------------------------
a, b = 0.0, 9.6
i0, i1, t = t_of(a, b)
grow = np.linspace(0.25, 1.0, len(t)) ** 1.6  # crescendo graduale
drone = tone(55, t, (1, .6, .4, .3, .2)) + 0.25 * tone(58.27, t, (1, .5, .3))  # La1 + Sib1 appena accennato
add(a, b, drone * env(len(t), 1.5, 0.15) * grow, gain=0.22)
# battito che accelera
beat_t, period = 0.6, 0.95
while beat_t < 9.2:
    _, _, bt = t_of(0, 0.35)
    thump = np.sin(2 * np.pi * (48 + 30 * np.exp(-bt * 25)) * bt) * np.exp(-bt * 11)
    add(beat_t, beat_t + 0.35, thump, gain=0.08 + 0.26 * (beat_t / 9.6) ** 1.5)
    beat_t += period
    period = max(0.7, period * 0.975)  # accelera appena
# crescendo di rumore filtrato verso il "Come"
i0, i1, t = t_of(5.8, 9.5)
noise = rng.standard_normal(len(t))
riser = lowpass(noise, 0.02) * np.linspace(0, 1, len(t)) ** 2.2
add(5.8, 9.5, riser, gain=0.45)
# nota acuta tesa che sale
i0, i1, t = t_of(6.5, 9.5)
f = 880 * (1 + 0.06 * (t / t[-1]))
add(6.5, 9.5, np.sin(2 * np.pi * np.cumsum(f) / SR) * np.linspace(0, 1, len(t)) ** 2, pan=0.3, gain=0.0)  # nota tesa tolta

# --- 2. come: scioglimento in maggiore -----------------------------------------
def pad(a, b, notes, gain=0.12, att=0.8, rel=1.0):
    i0, i1, t = t_of(a, b)
    s = sum(tone(NOTE[n], t, (1, .35, .12)) for n in notes) / len(notes)
    vib = 1 + 0.08 * np.sin(2 * np.pi * 0.3 * t)
    add(a, b, s * env(len(t), att, rel) * vib, gain=gain)


def arp(a, b, notes, step=0.3, gain=0.10):
    x, k = a, 0
    while x < b - 0.05:
        n = notes[k % len(notes)]
        _, _, t = t_of(0, 0.9)
        pl = tone(NOTE[n], t, (1, .3, .1)) * np.exp(-t * 5.5)
        add(x, x + 0.9, pl, pan=(-0.35 if k % 2 else 0.35), gain=gain)
        x += step
        k += 1


pad(9.6, 12.6, ["C3", "E3", "G3", "C4"], gain=0.16, att=0.25)
pad(12.6, 15.8, ["F2", "A3", "C4", "F3"], gain=0.15)
arp(10.2, 15.6, ["C4", "E4", "G4", "C5"], step=0.3, gain=0.09)

# --- 3. cosa: apertura luminosa --------------------------------------------
pad(15.6, 18.2, ["C3", "G3", "C4", "E4", "G4"], gain=0.17, att=0.3)
for k, n in enumerate(["C5", "E5", "G5"]):
    _, _, t = t_of(0, 1.6)
    add(15.65 + k * 0.12, 17.25 + k * 0.12, tone(NOTE[n], t, (1, .2)) * np.exp(-t * 2.2), pan=0.2 * (k - 1), gain=0.07)

# --- 4. demo: tappeto ottimista -------------------------------------------------
prog = [["C3", "E3", "G3"], ["G2", "B3", "D4"], ["A2", "C4", "E4"], ["F2", "A3", "C4"]]
arps = [["C4", "E4", "G4", "E4"], ["B3", "D4", "G4", "D4"], ["A3", "C4", "E4", "C4"], ["A3", "C4", "F4", "C4"]]
x, k = 17.8, 0
while x < 44.4:
    y = min(x + 3.34, 44.5)
    pad(x, y + 0.4, prog[k % 4], gain=0.11, att=0.6, rel=0.7)
    arp(x, y, arps[k % 4], step=0.42, gain=0.06 if x < 34.1 else 0.08)  # piccolo slancio dal passo 4
    x, k = y, k + 1

# --- 5. finale: sospensione e impatto ---------------------------------------
_, _, t = t_of(0, 0.8)
add(44.5, 45.3, lowpass(rng.standard_normal(len(t)), 0.05) * np.linspace(0, 1, len(t)) ** 3, gain=0.6)  # risucchio
_, _, t = t_of(0, 2.6)
boom = np.sin(2 * np.pi * np.cumsum(80 * np.exp(-t * 2.2) + 32) / SR) * np.exp(-t * 1.6)
add(45.3, 47.9, boom, gain=0.9)
pad(45.3, 48.0, ["C3", "G3", "C4", "E4", "G4", "C5"], gain=0.2, att=0.02, rel=2.0)

# equilibrio: soluzione e demo un po' più presenti
L[int(9.6 * SR):int(44.5 * SR)] *= 1.6
R[int(9.6 * SR):int(44.5 * SR)] *= 1.6

# --- riverbero semplice e mix ----------------------------------------------
ir_t = np.arange(int(1.6 * SR)) / SR
ir = rng.standard_normal(len(ir_t)) * np.exp(-ir_t * 3.2)
ir[0] = 6.0
ir /= np.abs(ir).sum() / 8


def conv(x):
    n = len(x) + len(ir)
    y = np.fft.irfft(np.fft.rfft(x, n) * np.fft.rfft(ir, n), n)[: len(x)]
    return 0.6 * x + 0.4 * y


L, R = conv(L), conv(R)
fade = np.ones(N)
fade[-int(0.9 * SR):] = np.linspace(1, 0, int(0.9 * SR))
fade[: int(0.05 * SR)] = np.linspace(0, 1, int(0.05 * SR))
st = np.stack([L * fade, R * fade], 1)
st /= np.abs(st).max() / 0.85
with wave.open(sys.argv[1], "wb") as w:
    w.setnchannels(2)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes((st * 32767).astype("<i2").tobytes())
print("ok", sys.argv[1])
