"""Narração Kokoro (am_michael) por frase, com pausas desenhadas + tempos por palavra (faster-whisper).
Uso: python3 tts.py linhas.json saida_dir [lead_in_s]
Gera saida_dir/NN.wav, saida_dir/narracao.wav (24 kHz) e saida_dir/timing.json"""
import json, os, re, sys
import numpy as np, soundfile as sf
from kokoro_onnx import Kokoro

FIX = {  # fonemas espeak -> pronúncia desejada
    "hˈɔːɹheɪ dʒˈiːzəs": "ʒˈɔːɹʒ ʒəzˈuːʃ",       # Jorge Jesus (pt)
    "ɹɑːnˈældoʊ": "ɹoʊnˈɑːldoʊ",                  # Ronaldo
}
VOICE = os.environ.get("VOICE", "am_michael")

def main(lines_path, out, lead=0.6):
    lines = json.load(open(lines_path))
    os.makedirs(out, exist_ok=True)
    tts = Kokoro(os.path.expanduser("~/tts/kokoro-v1.0.onnx"), os.path.expanduser("~/tts/voices-v1.0.bin"))
    sr = 24000
    track, t, timing = [np.zeros(int(lead * sr), np.float32)], lead, []
    for lid, text, speed, pause in lines:
        ph = tts.tokenizer.phonemize(text, "en-us")
        for a, b in FIX.items():
            ph = ph.replace(a, b)
        wp = f"{out}/{lid}.wav"
        if os.path.exists(wp) and not os.environ.get("REDO"):
            audio, sr = sf.read(wp, dtype="float32")
        else:
            audio, sr = tts.create(ph, voice=VOICE, speed=speed, is_phonemes=True)
            # apara silêncio das pontas
            nz = np.where(np.abs(audio) > 0.01)[0]
            audio = audio[max(0, nz[0] - 240): nz[-1] + 1200] if len(nz) else audio
            sf.write(wp, audio, sr)
        d = len(audio) / sr
        timing.append({"id": lid, "text": text, "start": round(t, 3), "end": round(t + d, 3)})
        track += [audio.astype(np.float32), np.zeros(int(pause * sr), np.float32)]
        t += d + pause
    full = np.concatenate(track)
    sf.write(f"{out}/narracao.wav", full, sr)
    # tempos por palavra
    from faster_whisper import WhisperModel
    m = WhisperModel("small.en", compute_type="int8")
    for it in timing:
        a, r = sf.read(f"{out}/{it['id']}.wav", dtype="float32")
        from scipy.signal import resample_poly
        a16 = resample_poly(a, 2, 3).astype(np.float32)  # 24k -> 16k
        segs, _ = m.transcribe(a16, language="en", word_timestamps=True)
        words = [(w.word.strip(), round(it["start"] + w.start, 3), round(it["start"] + w.end, 3)) for s in segs for w in s.words]
        it["words"] = words
        it["heard"] = " ".join(w[0] for w in words)
    json.dump({"total": round(t, 3), "lines": timing}, open(f"{out}/timing.json", "w"), indent=1, ensure_ascii=False)
    for it in timing:
        print(f'{it["id"]} {it["start"]:7.2f}-{it["end"]:7.2f}  {it["heard"]}')
    print("TOTAL", round(t, 2))

if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], float(sys.argv[3]) if len(sys.argv) > 3 else 0.6)
