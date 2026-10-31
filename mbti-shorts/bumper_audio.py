"""5s bumper audio: soft jingle + sfx + '잇팁인데요' voice. usage: python3 -I bumper_audio.py out.wav voice.mp3"""
import numpy as np, wave, sys, subprocess
SR = 44100; DUR = 5.0; N = int(SR * DUR); rng = np.random.default_rng(3)
L = np.zeros(N); R = np.zeros(N)
def add(sig, t0, g=1.0, pan=0.0):
    i = int(t0 * SR)
    if i >= N: return
    sig = sig[: N - i]; L[i:i + len(sig)] += sig * g * (1 - max(0, pan)); R[i:i + len(sig)] += sig * g * (1 + min(0, pan))
def tt(d): return np.arange(int(SR * d)) / SR
def midi(n): return 440 * 2 ** ((n - 69) / 12)
def lowpass(x, fc):
    a = np.exp(-2 * np.pi * fc / SR); y = np.empty_like(x); s = 0.0
    for i in range(len(x)): s = (1 - a) * x[i] + a * s; y[i] = s
    return y
def highpass(x, fc): return x - lowpass(x, fc)
def keys(n, d=2.2, v=1.0):
    t = tt(d); f = midi(n); e = np.exp(-t * 2.4) * (1 - np.exp(-t * 400))
    return (np.sin(2*np.pi*f*t) + .35*np.sin(2*np.pi*2*f*t)*np.exp(-t*5) + .12*np.sin(2*np.pi*3*f*t)*np.exp(-t*8)) * (1 + .1*np.sin(2*np.pi*4.5*t)) * e * .17 * v
def bell(n, d=2.2, v=1.0):
    t = tt(d); f = midi(n)
    return (np.sin(2*np.pi*f*t) + .4*np.sin(2*np.pi*2.76*f*t)*np.exp(-t*3) + .25*np.sin(2*np.pi*5.4*f*t)*np.exp(-t*6)) * np.exp(-t*2.2) * .15 * v
def kick(v=1.0):
    t = tt(.3); f = 45 + 90*np.exp(-t*28); return np.sin(2*np.pi*np.cumsum(f)/SR) * np.exp(-t*11) * .8 * v
def tick(f=1900, v=1.0):
    t = tt(.09); return np.sin(2*np.pi*f*t) * np.exp(-t*60) * .13 * v
def pop(v=1.0):
    t = tt(.22); f = 180 + 520*np.exp(-t*30); return np.sin(2*np.pi*np.cumsum(f)/SR) * np.exp(-t*16) * .35 * v
def swish(d=.7):
    n = rng.standard_normal(int(SR*d)); t = tt(d); x = highpass(lowpass(n, 2600), 400)
    return x * np.sin(np.pi*np.clip(t/d, 0, 1))**2 * .45
def bass(n, d=1.2, v=1.0):
    t = tt(d); f = midi(n); return (np.sin(2*np.pi*f*t) + .25*np.sin(2*np.pi*2*f*t)) * np.exp(-t*2.6) * (1 - np.exp(-t*300)) * .34 * v
add(swish(.7), 0.0, 1.0)
add(pop(1.0), .3, 1.0); add(kick(.8), .25, .9)               # cat pops in
add(tick(1500), .9, .9); add(tick(1800), 1.1, .9)            # text reveal
add(bass(45, 2.4), 1.15, 1.0)
for k, n in enumerate([57, 60, 64, 67]): add(keys(n, 2.6), 1.15 + k*.014, 1.0, pan=(k-1.5)*.15)   # Am9 when cat wakes
for k, n in enumerate([88, 91, 95]): add(bell(n, 1.8), 1.2 + k*.1, .8, pan=.2)                     # sparkle
add(tick(2000), 1.75, .8); add(tick(2300), 2.15, .7)
add(keys(64 + 12, 2.0, .6), 2.9, .8, pan=.2); add(keys(67 + 12, 2.0, .5), 3.3, .7, pan=.2)         # soft tail
# voice
v = np.frombuffer(subprocess.run(['ffmpeg','-v','error','-i',sys.argv[2],'-af','silenceremove=start_periods=1:start_threshold=-42dB:start_silence=0.02,areverse,silenceremove=start_periods=1:start_threshold=-42dB:start_silence=0.02,areverse','-ac','1','-ar',str(SR),'-f','f32le','-'],capture_output=True,check=True).stdout, dtype=np.float32).astype(np.float64)
v = v / (np.abs(v).max() + 1e-9) * .9
vs = v + .25 * (v - lowpass(v, 2500))
vo = np.zeros(N); k = int(1.0 * SR); seg = vs[: N - k]; vo[k:k+len(seg)] += seg
# music ducks under voice
env = np.abs(vo); e = 0.0; es = np.empty(N); aa = np.exp(-1/(.03*SR)); ar = np.exp(-1/(.3*SR))
for i in range(N):
    x = env[i]; e = x + aa*(e - x) if x > e else x + ar*(e - x); es[i] = e
duck = 1 - .55 * np.clip(es / .25, 0, 1)
def echo(x, d, fb, mix):
    d = int(d*SR); y = x.copy()
    for k in range(1, 4): y[k*d:] += x[:N-k*d] * (fb**k) * mix
    return y
L = lowpass(echo(L, .45, .45, .3), 9000) * duck; R = lowpass(echo(R, .3, .45, .3), 9000) * duck
mix = np.stack([L + vo*1.15, R + vo*1.15], 1)
fade = np.ones(N); fi = int(.03*SR); fo = int(.5*SR); fade[:fi] = np.linspace(0,1,fi); fade[-fo:] = np.linspace(1,0,fo)
mix *= fade[:, None]; mix = np.tanh(mix) * .95
with wave.open(sys.argv[1], 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((mix*32767).astype('<i2').tobytes())
print('ok')
