#!/usr/bin/env python3
"""Narração -> MP3. Padrão: edge-tts (grátis, sem chave). ElevenLabs se ELEVENLABS_API_KEY existir.
Uso: tts.py narration.txt out.mp3 [--voice en-US-GuyNeural] [--rate -5%] [--elevenlabs VOICE_ID]
Vozes: `edge-tts --list-voices`. Para PT-BR: pt-BR-AntonioNeural."""
import argparse, asyncio, os, sys

ap = argparse.ArgumentParser()
ap.add_argument("text"); ap.add_argument("out")
ap.add_argument("--voice", default="en-US-GuyNeural")
ap.add_argument("--rate", default="+0%")
ap.add_argument("--elevenlabs", metavar="VOICE_ID")
a = ap.parse_args()
text = open(a.text, encoding="utf-8").read()
os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)

if a.elevenlabs:
    import requests
    key = os.environ.get("ELEVENLABS_API_KEY") or sys.exit("Defina ELEVENLABS_API_KEY")
    r = requests.post(f"https://api.elevenlabs.io/v1/text-to-speech/{a.elevenlabs}",
                      headers={"xi-api-key": key}, json={"text": text, "model_id": "eleven_multilingual_v2"})
    r.raise_for_status(); open(a.out, "wb").write(r.content)
else:
    import edge_tts
    asyncio.run(edge_tts.Communicate(text, a.voice, rate=a.rate).save(a.out))
print("ok:", a.out)
