import numpy as np, wave, sys
SR = 44100
DUR = 40.0
BPM = 96
BEAT = 60 / BPM
N = int(SR * DUR)
rng = np.random.default_rng(7)
L = np.zeros(N); R = np.zeros(N)

def add(sig, t0, gain=1.0, pan=0.0):
    i = int(t0 * SR)
    if i >= N: return
    sig = sig[: N - i]
    L[i:i + len(sig)] += sig * gain * (1 - max(0, pan))
    R[i:i + len(sig)] += sig * gain * (1 + min(0, pan))

def tt(d): return np.arange(int(SR * d)) / SR
def midi(n): return 440 * 2 ** ((n - 69) / 12)

def lowpass(x, fc):
    a = np.exp(-2 * np.pi * fc / SR); y = np.zeros_like(x); s = 0.0
    for i in range(len(x)):
        s = (1 - a) * x[i] + a * s; y[i] = s
    return y
def highpass(x, fc): return x - lowpass(x, fc)

def keys(n, d=1.6, vel=1.0):
    t = tt(d); f = midi(n)
    env = np.exp(-t * 2.6) * (1 - np.exp(-t * 400))
    s = (np.sin(2 * np.pi * f * t) + .35 * np.sin(2 * np.pi * 2 * f * t) * np.exp(-t * 5) + .12 * np.sin(2 * np.pi * 3 * f * t) * np.exp(-t * 8))
    s *= 1 + .12 * np.sin(2 * np.pi * 4.5 * t)
    return s * env * .16 * vel
def pluck(n, d=1.2, vel=1.0):
    t = tt(d); f = midi(n)
    env = np.exp(-t * 4.5) * (1 - np.exp(-t * 600))
    s = np.sin(2 * np.pi * f * t) + .5 * np.sin(2 * np.pi * 2 * f * t) * np.exp(-t * 9) + .2 * np.sin(2 * np.pi * 4.01 * f * t) * np.exp(-t * 14)
    return s * env * .13 * vel
def bass(n, d=.9, vel=1.0):
    t = tt(d); f = midi(n)
    env = np.exp(-t * 3.2) * (1 - np.exp(-t * 300))
    return (np.sin(2 * np.pi * f * t) + .25 * np.sin(2 * np.pi * 2 * f * t)) * env * .34 * vel
def kick(vel=1.0):
    t = tt(.32); f = 45 + 95 * np.exp(-t * 28)
    ph = 2 * np.pi * np.cumsum(f) / SR
    return np.sin(ph) * np.exp(-t * 11) * .75 * vel
def snare(vel=1.0):
    t = tt(.28); n = highpass(rng.standard_normal(len(t)), 900)
    return (n * np.exp(-t * 22) * .22 + np.sin(2 * np.pi * 190 * t) * np.exp(-t * 28) * .18) * vel
def hat(vel=1.0, d=.06):
    t = tt(d); n = highpass(rng.standard_normal(len(t)), 6500)
    return n * np.exp(-t * 90) * .1 * vel
def tick(f=1900, vel=1.0):
    t = tt(.09); return np.sin(2 * np.pi * f * t) * np.exp(-t * 60) * .12 * vel
def tock(f=520, vel=1.0):
    t = tt(.3); return (np.sin(2 * np.pi * f * t) + .4 * np.sin(2 * np.pi * 2 * f * t)) * np.exp(-t * 14) * .16 * vel
def swish(d=.8, up=True):
    n = rng.standard_normal(int(SR * d)); t = tt(d)
    x = lowpass(n, 2600); x = highpass(x, 400)
    env = np.sin(np.pi * np.clip(t / d, 0, 1)) ** 2
    return x * env * .5
def sweep(d, f0=330, f1=990, vel=1.0):
    t = tt(d); f = f0 * (f1 / f0) ** (t / d)
    ph = 2 * np.pi * np.cumsum(f) / SR
    env = np.minimum(t / .1, 1) * np.minimum((d - t) / .25, 1)
    return np.sin(ph) * env * .05 * vel
def bell(n, d=1.8, vel=1.0):
    t = tt(d); f = midi(n)
    s = np.sin(2 * np.pi * f * t) + .4 * np.sin(2 * np.pi * 2.76 * f * t) * np.exp(-t * 3) + .25 * np.sin(2 * np.pi * 5.4 * f * t) * np.exp(-t * 6)
    return s * np.exp(-t * 2.4) * .13 * vel

# ---- chord progression: Am9 | Fmaj7 | Cmaj7 | G6 (4 beats each) ----
chords = [([57, 60, 64, 67], 45), ([53, 57, 60, 64], 41), ([60, 64, 67, 71], 48), ([55, 59, 62, 64], 43)]
nbeats = int(DUR / BEAT) + 1
for b in range(nbeats):
    bar, pos = divmod(b, 4); ch, root = chords[bar % 4]; t0 = b * BEAT
    sec_gain = .55 if t0 < 3.75 else 1.0
    if pos == 0:
        for k, n in enumerate(ch): add(keys(n, 2.4, .85), t0 + k * .012, sec_gain, pan=(k - 1.5) * .12)
        add(bass(root, 1.2), t0, sec_gain)
    if pos == 1:  # syncopated stab on "and of 2"
        for k, n in enumerate(ch[1:]): add(keys(n + 12 if k == 2 else n, 1.1, .5), t0 + BEAT * .5 + k * .01, sec_gain, pan=(k - 1) * .15)
    if pos == 2:
        add(bass(root + (7 if bar % 2 else 0), .8, .8), t0 + BEAT * .5, sec_gain)
    if pos == 3 and bar % 2:
        add(bass(root + 12, .6, .6), t0 + BEAT * .5, sec_gain)
    # drums
    if t0 >= 3.75 - 1e-6 or b >= 2:
        d = 1.0 if t0 >= 3.75 else .5
        if pos in (0, 2): add(kick(.9 if pos == 0 else .7), t0, d)
        if pos in (1, 3): add(snare(.8), t0, d)
        add(hat(.5 if pos % 2 == 0 else .7), t0, d, pan=.2)
        add(hat(.4), t0 + BEAT * .5 + .02, d, pan=-.2)

# ---- sparse pentatonic melody (from first rank) ----
mel = [(0, 76), (1.5, 79), (2.5, 76), (3.5, 74), (4, 72), (5.5, 74), (6.5, 69), (8, 76), (9.5, 79), (10.5, 81), (11.5, 79), (12, 76), (13.5, 74), (15, 72)]
for cyc in range(0, 10):
    for bt, n in mel:
        t0 = 3.75 + (cyc * 16 + bt) * BEAT
        if t0 < DUR - 1.5 and t0 > 3.75: add(pluck(n, 1.2, .8), t0, 1.0, pan=.25)

# ---- sfx ----
starts = [3.75 + i * 6.25 for i in range(5)] + [35.0]
for st in starts:
    add(swish(.85), st - .05, 1.0); add(tock(110, 1.2), st + .1, .8)
for i in range(5):
    r = 3.75 + i * 6.25
    add(tick(1500), r + .35, .9); add(tick(1800), r + .5, .8); add(tick(2100), r + .85, .7)
    add(sweep(1.5, 300, 900), r + 1.3, .9)
    add(tick(1700), r + 1.975, 1.0); add(tick(1900), r + 2.6, 1.0)
    add(tock(660, .9), r + 3.2, 1.0)
    add(tock(440, 1.0), r + 2.8, .0)
add(bell(88, 2.2), 3.75 + 4 * 6.25 + 3.2, 1.0); add(bell(95, 2.2), 3.75 + 4 * 6.25 + 3.32, .8); add(bell(100, 2.4), 3.75 + 4 * 6.25 + 3.44, .7)
# intro
for t0, f in [(.15, 1400), (.4, 1700), (.85, 1900)]: add(tick(f), t0, 1.0)
for i in range(5): add(tick(1300 + i * 120), 1.55 + i * .16, .8)
add(tock(600), 2.75, .9)
# outro
for i in range(5): add(tick(1400 + i * 130), 35 + .7 + i * .2, .8)
add(tock(520), 35 + 2.35, 1.0); add(bell(84, 2.5), 35 + 2.4, .9)

# ---- space: light echo, warmth, limiter, fades ----
def echo(x, delay, fb, mix):
    d = int(delay * SR); y = x.copy()
    for k in range(1, 5):
        y[k * d:] += x[:N - k * d] * (fb ** k) * mix
    return y
L = echo(L, BEAT * .75, .45, .35); R = echo(R, BEAT * .5, .45, .35)
L = lowpass(L, 9000); R = lowpass(R, 9000)
fade = np.ones(N); fi = int(.04 * SR); fo = int(1.5 * SR)
fade[:fi] = np.linspace(0, 1, fi); fade[-fo:] = np.linspace(1, 0, fo) ** 1.5
L *= fade; R *= fade
peak = max(np.abs(L).max(), np.abs(R).max())
g = .85 / peak
L = np.tanh(L * g * 1.1) * .92; R = np.tanh(R * g * 1.1) * .92
out = np.stack([L, R], 1)
pcm = (out * 32767).astype('<i2')
with wave.open(sys.argv[1], 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())
print('ok', peak)
