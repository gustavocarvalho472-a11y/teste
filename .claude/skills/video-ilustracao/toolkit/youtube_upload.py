"""Publica no YouTube direto do kit `postar/`: vídeo, título, descrição, tags, thumb, legenda .srt e comentário.

Credenciais (variáveis de ambiente, nunca no código):
    YT_CLIENT_ID, YT_CLIENT_SECRET, YT_REFRESH_TOKEN
    (o refresh token precisa dos escopos youtube.upload + youtube.force-ssl e é por canal)

    python3 youtube_upload.py postar/publicar.json --dry-run          # confere tudo sem enviar
    python3 youtube_upload.py postar/publicar.json                    # envia como PRIVADO (pra revisar)
    python3 youtube_upload.py postar/publicar.json --publico          # publica na hora
    python3 youtube_upload.py postar/publicar.json --agendar 2026-10-03T21:00:00-03:00
        # agenda os longos nesse horário e os Shorts 3h depois
    python3 youtube_upload.py postar/publicar.json --so pt_longo,pt_short

O que já foi enviado fica em `postar/publicados.json`: rodar de novo não duplica vídeo.
A API do YouTube não permite fixar comentário nem preencher "vídeo relacionado" do Short:
o script posta o comentário e põe o link do vídeo longo na descrição do Short; fixar é 1 clique no app.
"""
import argparse
import datetime as dt
import json
import os
import sys
import time

import requests

API = "https://www.googleapis.com/youtube/v3"
UPLOAD = "https://www.googleapis.com/upload/youtube/v3"
CATEGORY = "22"  # Pessoas e blogs
SHORT_DELAY_H = 3


def token():
    need = ["YT_CLIENT_ID", "YT_CLIENT_SECRET", "YT_REFRESH_TOKEN"]
    missing = [k for k in need if not os.environ.get(k)]
    if missing:
        sys.exit("Faltam as variáveis de ambiente: " + ", ".join(missing))
    r = requests.post("https://oauth2.googleapis.com/token", data={
        "client_id": os.environ["YT_CLIENT_ID"], "client_secret": os.environ["YT_CLIENT_SECRET"],
        "refresh_token": os.environ["YT_REFRESH_TOKEN"], "grant_type": "refresh_token"}, timeout=30)
    if r.status_code != 200:
        sys.exit(f"Falha ao renovar o token ({r.status_code}): {r.text}")
    return r.json()["access_token"]


def check(r, what):
    if r.status_code >= 300:
        raise RuntimeError(f"{what}: HTTP {r.status_code} {r.text[:500]}")
    return r.json() if r.content else {}


def channel(h):
    js = check(requests.get(f"{API}/channels", params={"part": "snippet", "mine": "true"}, headers=h), "canal")
    return js["items"][0]["snippet"]["title"] if js.get("items") else "?"


def upload_video(h, path, body):
    size = os.path.getsize(path)
    r = requests.post(f"{UPLOAD}/videos", params={"uploadType": "resumable", "part": "snippet,status"},
                      headers={**h, "Content-Type": "application/json; charset=UTF-8",
                               "X-Upload-Content-Type": "video/mp4", "X-Upload-Content-Length": str(size)},
                      data=json.dumps(body))
    check(r, "iniciar upload")
    url, sent, chunk = r.headers["Location"], 0, 8 * 1024 * 1024
    with open(path, "rb") as f:
        while True:
            f.seek(sent)
            data = f.read(chunk)
            end = sent + len(data) - 1
            for attempt in range(5):
                try:
                    r = requests.put(url, data=data, headers={**h, "Content-Range": f"bytes {sent}-{end}/{size}"},
                                     timeout=300)
                    if r.status_code in (500, 502, 503, 504):
                        raise requests.ConnectionError(r.status_code)
                    break
                except requests.RequestException:
                    time.sleep(2 ** attempt)
                    q = requests.put(url, headers={**h, "Content-Range": f"bytes */{size}"})
                    if q.status_code == 308 and "Range" in q.headers:
                        sent = int(q.headers["Range"].split("-")[1]) + 1
                        break
            else:
                raise RuntimeError("upload falhou depois de 5 tentativas")
            if r.status_code in (200, 201):
                return r.json()["id"]
            if r.status_code != 308:
                check(r, "upload")
            sent = int(r.headers["Range"].split("-")[1]) + 1 if "Range" in r.headers else 0
            print(f"   {100 * sent / size:5.1f}%", flush=True)


def set_thumb(h, vid, path):
    with open(path, "rb") as f:
        check(requests.post(f"{UPLOAD}/thumbnails/set", params={"videoId": vid},
                            headers={**h, "Content-Type": "image/png"}, data=f.read()), "thumbnail")


def add_caption(h, vid, path, lang):
    meta = {"snippet": {"videoId": vid, "language": lang, "name": "", "isDraft": False}}
    with open(path, "rb") as f:
        files = {"meta": (None, json.dumps(meta), "application/json"),
                 "file": (os.path.basename(path), f.read(), "application/octet-stream")}
    check(requests.post(f"{UPLOAD}/captions", params={"part": "snippet", "uploadType": "multipart"},
                        headers=h, files=files), "legenda")


def comment(h, vid, text):
    body = {"snippet": {"videoId": vid, "topLevelComment": {"snippet": {"textOriginal": text}}}}
    check(requests.post(f"{API}/commentThreads", params={"part": "snippet"}, headers=h, json=body), "comentário")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("manifest")
    ap.add_argument("--so", help="ids separados por vírgula")
    ap.add_argument("--publico", action="store_true", help="publica na hora (padrão: privado)")
    ap.add_argument("--agendar", help="ISO 8601 com fuso, ex. 2026-10-03T21:00:00-03:00")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()

    base = os.path.dirname(os.path.abspath(a.manifest))
    man = json.load(open(a.manifest, encoding="utf-8"))
    state_path = os.path.join(base, "publicados.json")
    state = json.load(open(state_path)) if os.path.exists(state_path) else {}
    items = [v for v in man["videos"] if not a.so or v["id"] in a.so.split(",")]
    when = dt.datetime.fromisoformat(a.agendar) if a.agendar else None

    for v in items:   # validação antes de qualquer envio
        for k in ("arquivo", "thumb", "legenda"):
            if v.get(k) and not os.path.exists(os.path.join(base, v[k])):
                sys.exit(f"[{v['id']}] arquivo não encontrado: {v[k]}")
        if len(v["titulo"]) > 100 or len(v["descricao"]) > 5000 or len(",".join(v["tags"])) > 500:
            sys.exit(f"[{v['id']}] título/descrição/tags acima do limite do YouTube")

    h = None
    if not a.dry_run:
        h = {"Authorization": f"Bearer {token()}"}
        print("Canal:", channel(h))

    for v in items:
        if v["id"] in state:
            print(f"[{v['id']}] já publicado: https://youtu.be/{state[v['id']]}")
            continue
        desc = v["descricao"]
        for other, vid in state.items():
            desc = desc.replace("{link:" + other + "}", f"https://youtu.be/{vid}")
        if "{link:" in desc:
            sys.exit(f"[{v['id']}] o vídeo longo precisa ser publicado antes (link na descrição)")
        status = {"privacyStatus": "public" if a.publico else "private", "selfDeclaredMadeForKids": False}
        if when:
            t = when + dt.timedelta(hours=SHORT_DELAY_H if "short" in v["id"] else 0)
            status = {"privacyStatus": "private", "publishAt": t.astimezone(dt.timezone.utc).isoformat()
                      .replace("+00:00", "Z"), "selfDeclaredMadeForKids": False}
        body = {"snippet": {"title": v["titulo"], "description": desc, "tags": v["tags"], "categoryId": CATEGORY,
                            "defaultLanguage": v["idioma"], "defaultAudioLanguage": v["idioma"]},
                "status": status}
        print(f"[{v['id']}] {v['arquivo']} → {status.get('publishAt', status['privacyStatus'])}")
        if a.dry_run:
            print("   (dry-run) título:", v["titulo"])
            state.setdefault(v["id"], "DRYRUN")   # para os {link:...} resolverem no teste
            continue
        vid = upload_video(h, os.path.join(base, v["arquivo"]), body)
        state[v["id"]] = vid
        json.dump(state, open(state_path, "w"), indent=1)
        print(f"   enviado: https://youtu.be/{vid}")
        for step, fn in (("thumb", lambda: set_thumb(h, vid, os.path.join(base, v["thumb"]))),
                         ("legenda", lambda: add_caption(h, vid, os.path.join(base, v["legenda"]), v["idioma"])),
                         ("comentario", lambda: comment(h, vid, v["comentario"]))):
            if v.get(step):
                try:
                    fn()
                    print(f"   {step} ok")
                except RuntimeError as e:   # não perde o vídeo por causa de um extra
                    print(f"   {step} FALHOU: {e}")
    if not a.dry_run:
        print("\nFalta só: fixar o comentário e, no Short, escolher o vídeo longo em 'Vídeo relacionado'.")


if __name__ == "__main__":
    main()
