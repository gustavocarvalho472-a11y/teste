# Entrega do vídeo

## Pelo chat
O envio de arquivos aceitou 18–25 MB e falhou com 61 MB e 94 MB (erro 502).
Use para prévias (`--preview` já gera ≤ 25 MB). Dividir o vídeo final em 20+
partes é o último recurso.

## Git LFS (vídeo final inteiro, recomendado)
GitHub recusa arquivos > 100 MB em commit normal; com LFS aceita até 2 GB.
Use uma branch órfã só com o vídeo, para não misturar com o código:

```bash
W=<pasta temporária>
git worktree add --detach $W && cd $W
git checkout --orphan video-final && git rm -rqf .
git lfs install --local && git lfs track "*.mp4"
cp <caminho>/video.mp4 . && git add .gitattributes video.mp4
git commit -m "Add final video (Git LFS)" && git push -u origin video-final
cd - && git worktree remove --force $W
```

Confirme que subiu (o tamanho tem que bater com o arquivo local):
```bash
curl -sSIL https://media.githubusercontent.com/media/<dono>/<repo>/video-final/video.mp4 | grep -i content-length
```

Link de download direto para o usuário:
`https://media.githubusercontent.com/media/<dono>/<repo>/video-final/video.mp4`

Avisos para passar ao usuário:
- plano gratuito do LFS: 1 GB de armazenamento e 1 GB de banda/mês (um vídeo
  de ~900 MB = um download por mês); apagar a branch depois libera espaço;
- se o link funciona sem login, o repositório é público — o vídeo (e a música)
  fica acessível a quem tiver o link.

Peça permissão antes de criar uma branch nova se as instruções da sessão
restringirem para qual branch dá para enviar.
