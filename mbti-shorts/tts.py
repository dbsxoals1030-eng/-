import sys, asyncio, certifi
certifi.where = lambda *a, **k: '/root/.ccr/ca-bundle.crt'   # trust the egress proxy CA (verification stays on)
import edge_tts
async def main(voice, rate, pitch, text, out):
    await edge_tts.Communicate(text, voice, rate=rate, pitch=pitch).save(out)
voice, rate, pitch, text, out = sys.argv[1:6]
asyncio.run(main(voice, rate, pitch, text, out))
