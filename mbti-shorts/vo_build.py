"""Build the fast-tempo Korean voice-over track, fit each line to its scene window, duck the BGM under it.
usage: python3 -I vo_build.py <music.wav> <workdir> <out.wav> <episode.json>
Lines are (start_sec, max_end_sec, text). Spell MBTI types the way Koreans say them (잇티제, 인팁...).
"""
import sys, os, subprocess, json, wave
import numpy as np

SR = 44100
VOICE, RATE, PITCH = 'ko-KR-SunHiNeural', '+24%', '+1Hz'
INTRO, RANK, OUTRO = 0.0, 3.75, 35.0
def rk(i): return RANK_START + i * 6.25
RANK_START = 3.75

def build_lines(ep):
    mode = ep.get('mode', 'ranking')
    items = ep['items'] if mode == 'list' else ep['ranks']
    n = len(items)
    item = int((40 - 3.75 - 5) / .625 / n + 1e-9) * .625
    out0 = 3.75 + n * item
    iv = ep['intro_voice']
    L = [(0.10, 3.0 if len(iv) > 1 else 3.6, iv[0])]
    if len(iv) > 1 and iv[1]: L.append((3.05 if True else 2.85, 3.72, iv[1]))
    for i, r in enumerate(items):
        s = 3.75 + i * item; v = r['voice']
        if mode == 'list':
            e1 = s + min(2.3, item * .45)
            L += [(s + .1, e1, v[0]), (e1 + .1, s + item - .25, v[1])]
        else:
            L += [(s + .15, s + 1.75, v[0]), (s + 1.85, s + 4.15, v[1]), (s + 4.25, s + 5.95, v[2])]
    o = ep['outro']['voice']
    L += [(out0 + .2, out0 + 2.2, o[0]), (out0 + 2.3, out0 + 3.7, o[1]), (out0 + 3.75, out0 + 4.95, o[2])]
    return L

music_wav, work, out, episode = sys.argv[1:5]
LINES = build_lines(json.load(open(episode, encoding='utf-8')))
os.makedirs(work, exist_ok=True)
here = os.path.dirname(os.path.abspath(__file__))

def decode(path, af):
    cmd = ['ffmpeg', '-v', 'error', '-i', path, '-af', af, '-ac', '1', '-ar', str(SR), '-f', 'f32le', '-']
    return np.frombuffer(subprocess.run(cmd, capture_output=True, check=True).stdout, dtype=np.float32)

TRIM = 'silenceremove=start_periods=1:start_threshold=-42dB:start_silence=0.02,areverse,silenceremove=start_periods=1:start_threshold=-42dB:start_silence=0.02,areverse'
N = int(SR * 40)
vo = np.zeros(N)
report = []
for i, (t0, tmax, text) in enumerate(LINES):
    mp3 = f'{work}/l{i:02d}.mp3'
    if not os.path.exists(mp3) or os.path.getsize(mp3) == 0:
        subprocess.run(['python3', '-I', f'{here}/tts.py', VOICE, RATE, PITCH, text, mp3], check=True, timeout=90)
    x = decode(mp3, TRIM)
    dur = len(x) / SR; win = tmax - t0
    if dur > win:
        tempo = dur / win
        if tempo > 1.3: print('WARN too long', i, text, round(dur, 2), round(win, 2))
        x = decode(mp3, TRIM + f',atempo={min(tempo, 2.0):.3f}')
    x = x / (np.abs(x).max() + 1e-9) * .9
    k = int(t0 * SR)
    seg = x[: N - k]
    fi = int(.004 * SR); seg[:fi] *= np.linspace(0, 1, fi); fo = int(.02 * SR); seg[-fo:] *= np.linspace(1, 0, fo)
    vo[k:k + len(seg)] += seg
    report.append((i, round(t0, 2), 'nat', round(dur, 2), 'win', round(win, 2), 'x%.2f' % max(1, dur / win), text))
for r in report: print(r)

# light presence EQ / warmth: gentle high-shelf-ish via difference
def lp(x, fc):
    a = np.exp(-2 * np.pi * fc / SR); y = np.empty_like(x); s = 0.0
    for n in range(len(x)):
        s = (1 - a) * x[n] + a * s; y[n] = s
    return y
vo = vo + .25 * (vo - lp(vo, 2500))

with wave.open(music_wav) as w:
    m = np.frombuffer(w.readframes(w.getnframes()), dtype='<i2').reshape(-1, 2).astype(np.float64) / 32768
# duck music under voice
env = np.abs(vo); a_att = np.exp(-1 / (.03 * SR)); a_rel = np.exp(-1 / (.35 * SR)); e = 0.0; env_s = np.empty(N)
for n in range(N):
    v = env[n]; e = v + a_att * (e - v) if v > e else v + a_rel * (e - v); env_s[n] = e
env_s = np.clip(env_s / .25, 0, 1)
duck = 1 - .6 * env_s
m *= duck[:, None]
mix = m + np.stack([vo, vo], 1) * 1.15
mix = np.tanh(mix * 1.0) * .95
pcm = (mix * 32767).astype('<i2')
with wave.open(out, 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())
print('done', out)
