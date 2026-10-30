"""Roteiro decupado do vídeo "Mbappé ofendeu a China", em formato que o montar.py entende.

Cada bloco é um dict:
  id     cena do handoff (S01…)
  ato    capítulo (só no primeiro bloco do ato)
  fala   narração (legenda = este texto; a voz usa FALA_TTS para corrigir pronúncia)
  shots  visuais em sequência, dividindo a duração do bloco. Cada shot é um id de asset
         (MEME_01, PRT_04, FOT_01, IA_02, LOG_01, CLP_01) ou "gfx:<nome>", "black", "title:<texto>".
         Um shot pode ser uma tupla (asset, {opções}): bw=True (P&B), small=True, split=[a, b], grid=[…],
         logos=[…], kb="in"|"out"|"pan".
  txt    texto na tela: (texto, estilo) com estilo "big" | "stamp" | "yellow" | "small"
  hl     frase-chave que ganha a caixa amarela nos prints
  fonte  crédito "Fonte: X" nos prints
  sfx    efeito no início do bloco (nome de audio/sfx/<nome>.wav ou sintetizado)
  dur    duração fixa (blocos sem fala)
  pun    contador "PUNIÇÃO n/5"
  respiro  segundos extras de B-roll depois da fala (ATOS 3 e 6, para chegar a 8:30)
  mus    marca de trilha: "off" (música para), "in" (entra), "up" (sobe), "resolve" (resolve)
"""

B = [
    # ── ATO 1 — GANCHO ──────────────────────────────────────────────────────────────────────────────
    dict(id="S01", ato="O gancho", fala="Esse é o Kylian Mbappé. Um dos jogadores mais caros do planeta.",
         shots=["CLP_01"], mus="off"),
    dict(id="S02", fala="E semana passada, ele chamou o fundador da China de ditador.",
         shots=["MEME_01"], txt=("DITADOR", "stamp"), sfx="boom"),
    dict(id="S03", fala="Rindo.", shots=[("CLP_01", {"bw": True, "frame": 0.6})], sfx="scratch"),
    dict(id="S04", fala="Esse homem está no dinheiro da China. Está na porta da Cidade Proibida.",
         shots=["FOT_02", "FOT_01"], mus="in"),
    dict(id="S05", fala="Pra 1,4 bilhão de pessoas, o Mbappé não fez uma piada. Ele ofendeu o pai do país.",
         shots=["IA_02"], txt=("1,4 BILHÃO", "big")),
    dict(id="S06", fala="E a China não perdoou.", shots=["black"], sfx="boom", pausa=0.5),
    dict(id="S07a", fala="Em 48 horas, a TV estatal tirou ele do ar.", shots=["PRT_01"],
         hl="SUSPENDS La Liga coverage", fonte="X / @MadridZone", sfx="whoosh"),
    dict(id="S07b", fala="Três marcas rasgaram os contratos.", shots=["IA_04"], sfx="paper_rip"),
    dict(id="S07c", fala="As contas dele foram silenciadas.", shots=["PRT_02"], fonte="Weibo", sfx="whoosh"),
    dict(id="S07d", fala="Os games começaram a apagar ele.", shots=["PRT_03"], fonte="X / Polymarket Español",
         sfx="whoosh"),
    dict(id="S07e", fala="A La Liga saiu da TV estatal chinesa.", shots=["PRT_04"], fonte="X / @KalshiFC",
         sfx="whoosh"),
    dict(id="S07f", fala="E o presidente da liga correu até a embaixada pra pedir desculpas.", shots=["PRT_05"],
         fonte="X / @Tebasjavier", sfx="whoosh"),
    dict(id="S08", fala="O Mbappé também pediu desculpas. Em chinês.", shots=["PRT_06"],
         hl="bloco em chinês", fonte="X / @KMbappe"),
    dict(id="S09", fala="A resposta da China? Palavras não bastam.", shots=["PRT_07"],
         txt=("PALAVRAS NÃO BASTAM", "stamp"), fonte="X / Madrid Sports", sfx="impact"),
    dict(id="S10a", fala="Como um meme de dez segundos colocou quase meio bilhão de dólares em risco?",
         shots=[("MEME_01", {"kb": "in", "dark": True})]),
    dict(id="S10b", fala="E por que pedir desculpas não salvou ele?", shots=[("MEME_01", {"kb": "in", "dark": True})]),
    dict(id="S10c", fala="Fica até o final — porque o maior prejuízo dessa história não é do Mbappé.",
         shots=[("MEME_01", {"kb": "in", "dark": True})]),
    dict(id="TITULO", fala="", shots=["title:O MEME QUE A CHINA NÃO PERDOOU"], dur=1.6, sfx="glitch"),

    # ── ATO 2 — O APELIDO ───────────────────────────────────────────────────────────────────────────
    dict(id="S11", ato="O apelido", fala="Tudo começa com um apelido. No futebol, o Mbappé é chamado de 'o ditador'.",
         shots=["FOT_03"], txt=("O DITADOR", "big")),
    dict(id="S12", fala="Não por política. Por poder. Dizem que ele manda no vestiário, escolhe técnico, "
                        "dita o próprio contrato.", shots=["IA_03"]),
    dict(id="S13", fala="A internet adorou. E começou a colocar a cara dele em fotos de generais, imperadores "
                        "e líderes da história.",
         shots=[("grid", {"grid": ["MEME_03", "MEME_04", "MEME_05", "MEME_06"]})], sfx="shutter"),
    dict(id="S14", fala="Até que alguém fez esse aqui.", shots=["MEME_02"], sfx="impact"),
    dict(id="S15", fala="E o problema é que, na China, esse homem não é personagem de meme.", shots=["FOT_04"]),
    dict(id="S16a", fala="Pro Ocidente, Mao Tsé-Tung é lembrado pela Revolução Cultural e por um governo de "
                         "mão de ferro.", shots=["FOT_05"]),
    dict(id="S16b", fala="Mas pro Estado chinês, ele é o fundador da República Popular — o homem que governou "
                         "de 1949 a 1976.", shots=["gfx:linha_tempo"]),
    dict(id="S16c", fala="Na China, zoar o Mao não é opinião. É ofensa.", shots=["FOT_01"],
         txt=("É OFENSA", "stamp"), sfx="impact"),
    dict(id="S17", fala="E o Mbappé estava prestes a descobrir isso do pior jeito. Porque ele tinha muito a perder lá.",
         shots=[("MEME_01", {"small": True})], sfx="whoosh_low"),

    # ── ATO 3 — O MBAPPÉ QUE A CHINA AMAVA ──────────────────────────────────────────────────────────
    dict(id="S18", respiro=2.5, ato="O Mbappé que a China amava",
         fala="Os chineses amavam ele. Tinham até um apelido carinhoso: Guigui, por causa de uma suposta "
              "semelhança com uma Tartaruga Ninja.", shots=["PRT_08"], txt=("GUIGUI 龟龟", "big"),
         fonte="TIME"),
    dict(id="S19", respiro=2.5, fala="Cerca de 1 milhão de seguidores no Weibo. Mais 1 milhão no Xiaohongshu.",
         shots=["gfx:contadores"]),
    dict(id="S20", respiro=2.5, fala="Ele tinha uma água com o próprio rosto na garrafa.", shots=["FOT_06", "FOT_07"]),
    dict(id="S21a", respiro=2.5, fala="Contrato com a Mengniu, o maior laticínio da China. Com a Milkground, de queijos.",
         shots=[("logos", {"logos": ["LOG_01", "LOG_02", "LOG_03"]})]),
    dict(id="S21b", respiro=2.5, fala="E a camisa dele era a mais vendida do Real Madrid no país.", shots=["IA_08"]),
    dict(id="S22", respiro=2.5, fala="O Mbappé não era só famoso na China. Ele era um produto.",
         shots=[("FOT_07", {"bw": True})], txt=("UM PRODUTO", "big")),
    dict(id="S23", fala="E aí ele sentou nesse sofá.", shots=["CLP_01"], mus="off"),

    # ── ATO 4 — A FRASE ─────────────────────────────────────────────────────────────────────────────
    dict(id="S24", ato="A frase", fala="Programa francês The Bridge. Quadro leve. Pergunta: 'qual meme seu te "
                                       "fez rir mais?'", shots=["CLP_01"]),
    dict(id="S25", fala="Ele escolheu esse. E descreveu como 'um cara… acho que é um ditador chinês'.",
         shots=[("split", {"split": ["FOT_08", "MEME_01"]})], txt=("“um cara… acho que é um ditador chinês”", "type"),
         mus="in"),
    dict(id="S26", fala="Repara: ele nem sabia quem era. E pra China, isso foi pior. O maior símbolo do país era, "
                        "pra ele, 'um cara qualquer'.", shots=["FOT_01"], txt=("“UM CARA QUALQUER”", "stamp")),
    dict(id="S27", fala="O clipe vazou pras redes chinesas. Em horas, virou um dos assuntos mais falados do Weibo.",
         shots=["IA_05"], sfx="notifs"),

    # ── ATO 5 — A VINGANÇA ──────────────────────────────────────────────────────────────────────────
    dict(id="S28a", ato="A vingança", pun=1, fala="Punição número um. 26 de outubro, à noite.",
         shots=["IA_01"], sfx="tv_off"),
    dict(id="S28b", pun=1, fala="O China Media Group, dono da TV estatal CCTV, corta a La Liga e qualquer jogo "
                                "com o Mbappé.", shots=["IA_12", "PRT_04"], fonte="X / @KalshiFC"),
    dict(id="S28c", pun=1, fala="Tira os anúncios dele do ar. Apaga os posts sobre ele.", shots=["IA_01"],
         sfx="tv_off"),
    dict(id="S29a", pun=2, fala="Punição dois. Dia 27. A Dongpeng, a da água, rompe. A Mengniu rompe. "
                                "A Milkground rompe.",
         shots=[("logos", {"logos": ["LOG_01", "LOG_02", "LOG_03"], "fall": True})], sfx="paper_rip3"),
    dict(id="S29b", pun=2, fala="Segundo o Le Monde, parte desses contratos valia uns 50 milhões de yuans — "
                                "quase 7 milhões de euros.", shots=["PRT_09"], txt=("≈ €7 MILHÕES", "big"),
         fonte="CNBC"),
    dict(id="S30", pun=2, fala="E as ações das próprias marcas despencaram na bolsa.", shots=["IA_07"],
         sfx="cash_drop"),
    dict(id="S31", pun=3, fala="Punição três. As contas dele no Weibo e no Xiaohongshu são silenciadas por "
                               "'violar regras'.", shots=["PRT_02"], txt=("SILENCIADO", "stamp"), sfx="impact"),
    dict(id="S32a", pun=4, fala="Punição quatro. O FC Online, da Tencent, começa a tirar o Mbappé. A versão "
                                "chinesa do eFootball faz o mesmo.", shots=["PRT_03"], fonte="X / Polymarket Español",
         sfx="glitch"),
    dict(id="S32b", pun=4, fala="Na China, o Real Madrid entra em campo no videogame — sem o Mbappé.",
         shots=["IA_06"], sfx="glitch"),
    dict(id="S33a", pun=5, fala="Punição cinco. E essa atravessa o oceano. Um mês antes, a On — a marca suíça "
                                "pela qual ele trocou a Nike — tinha feito dele embaixador global.",
         shots=["FOT_08", "PRT_10"], fonte="X / Kalshi", hl="DROPPED"),
    dict(id="S33b", pun=5, fala="Na terça, as ações da On chegaram a cair quase 6% em Wall Street. E a marca "
                                "apagou tudo do Mbappé nas redes chinesas.", shots=["IA_07", "PRT_10"],
         txt=("−6% NO DIA", "big"), fonte="X / Kalshi", sfx="cash_drop"),
    dict(id="S34", fala="Mas guarda isso: nenhuma dessas punições é a mais cara. A mais cara caiu em cima de "
                        "vinte clubes que não tinham nada a ver com a piada.",
         shots=[("LOG_04", {"bw": True, "crack": True})], sfx="crack"),

    # ── ATO 6 — O DINHEIRO DE VERDADE ───────────────────────────────────────────────────────────────
    dict(id="S35", respiro=2.5, ato="O dinheiro de verdade",
         fala="Agosto deste ano. Javier Tebas, presidente da La Liga, vai a Pequim e assina com a Migu, da "
              "estatal China Mobile. Exclusividade digital na China até 2030. Os 380 jogos de cada temporada.",
         shots=["IA_09", "FOT_09", "IA_09"]),
    dict(id="S36", respiro=2.5, fala="O valor nunca foi divulgado. Mas o mercado fala em algo entre 400 e 465 milhões de dólares.",
         shots=["gfx:valor_migu"], sfx="impact"),
    dict(id="S37", respiro=2.5, fala="E a La Liga tem trauma. Em 2021/22, uma parceira chinesa simplesmente não pagou. "
                        "Buraco de 45 milhões de euros.", shots=["IA_10"], txt=("−€45 MI", "big")),
    dict(id="S38", respiro=2.5, fala="Então, quando a TV estatal corta o sinal, o recado não é pra TV. É pro contrato de "
                        "quase meio bilhão.", shots=["IA_12", "gfx:valor_migu"], sfx="tv_off"),
    dict(id="S39a", respiro=2.5, fala="E o Real Madrid? Entre 10% e 15% da venda internacional de camisas e produtos do "
                         "clube vem da China.", shots=["PRT_11", "gfx:pizza"], fonte="X / Kalshi"),
    dict(id="S39b", respiro=2.5, fala="E o clube fica com uma fatia dos direitos de imagem do Mbappé. Cada marca que rasga "
                         "contrato com ele tira dinheiro de Madri também.", shots=["IA_08", "IA_04"],
         sfx="paper_rip"),
    dict(id="S40", respiro=2.5, fala="Você talvez tenha visto por aí que a La Liga perdeu 900 milhões só na China. Não é "
                        "verdade. Isso é o que ela ganha com direitos internacionais no mundo inteiro. E o "
                        "contrato com a Migu, até agora, continua de pé.", shots=["gfx:mito"]),
    dict(id="S41", fala="O que é pior. Porque significa que a China ainda não usou a arma grande. Só mostrou que tem.",
         shots=[("IA_02", {"kb": "in"})], mus="up"),

    # ── ATO 7 — AS DESCULPAS ────────────────────────────────────────────────────────────────────────
    dict(id="S42", ato="As desculpas que não funcionaram",
         fala="O Mbappé publicou um pedido de desculpas em três línguas. Disse que o comentário foi infeliz.",
         shots=["PRT_06"], hl="ill-judged", fonte="X / @KMbappe"),
    dict(id="S43", fala="O Real Madrid pediu desculpas. E o Tebas fez algo raro: se reuniu com o embaixador "
                        "chinês e mandou uma carta à TV estatal chamando a atitude do próprio jogador da liga "
                        "de inaceitável.", shots=["PRT_05", "PRT_12"], txt=("INACEITÁVEL", "stamp"),
         fonte="X / @Tebasjavier · Kalshi"),
    dict(id="S44", fala="A resposta? A TV estatal disse que vai julgar pelas ações. E exigiu desculpas públicas "
                        "e por escrito da La Liga, do Real e do Mbappé.", shots=["PRT_07"],
         fonte="X / Madrid Sports"),
    dict(id="S45", fala="Nas redes chinesas, o comentário que viralizou foi: não aceito, não perdoado.",
         shots=["gfx:nao_perdoado"], sfx="boom"),
    dict(id="S46", fala="E pra piorar: um comitê do Congresso americano dedicado à China disse publicamente que "
                        "ele nem devia ter pedido desculpas.", shots=["PRT_13"], fonte="X / @committeeonccp"),
    dict(id="S47", fala="O Mbappé ficou no meio de duas superpotências. Por causa de um meme.", shots=["IA_11"]),

    # ── ATO 8 — A LIÇÃO ─────────────────────────────────────────────────────────────────────────────
    dict(id="S48", ato="A lição", fala="E ele não é o primeiro. Em 2019, o Özil criticou a China, e a TV estatal "
                                       "tirou um jogo do Arsenal do ar.", shots=["PRT_14"]),
    dict(id="S49", fala="No mesmo ano, um único tuíte de um dirigente do Houston Rockets fez a NBA sumir da TV "
                        "chinesa.", shots=["PRT_15"]),
    dict(id="S50", fala="O padrão é sempre o mesmo. A China não multa. Ela tira o acesso. E acesso a 1,4 bilhão "
                        "de pessoas é o ativo mais caro do esporte.", shots=["IA_02", "IA_12"],
         txt=("ELA TIRA O ACESSO", "big")),
    dict(id="S51", fala="Quando você chega no nível do Mbappé, você não é mais uma pessoa. É uma empresa. E toda "
                        "frase sua vira cláusula de contrato.", shots=[("FOT_03", {"bw": True}), "IA_04"]),
    dict(id="S52", fala="Então: como um meme de dez segundos coloca quase meio bilhão em risco? Porque quando você "
                        "é um produto global, não existe piada local.", shots=[("MEME_01", {"kb": "shrink"})],
         mus="resolve"),
    dict(id="S53", ato="Comenta aí", fala="Comenta aí: ele devia ter pedido desculpas, ou o Congresso americano tem "
                                          "razão? E se você quer saber por que o Mbappé largou a Nike pela On, o "
                                          "vídeo tá aqui na tela.", shots=["gfx:endscreen"]),
    dict(id="END", fala="", shots=["gfx:endscreen"], dur=10.0),
]

# Pronúncia: a voz lê FALA_TTS em vez do texto da legenda (Kokoro/espeak não conhece estes nomes).
PRON = {
    "Mbappé": "Embapê", "Kylian": "Quilian", "Weibo": "Uêibô", "Xiaohongshu": "Chiaorrôngchu",
    "Mengniu": "Mêngniú", "Milkground": "Milk-gráund", "Dongpeng": "Dôngpêng", "Tencent": "Ténçent",
    "Guigui": "Guêiguêi", "Migu": "Mígu", "Özil": "Ózil", "Tebas": "Tébas", "eFootball": "i-futból",
    "FC Online": "éfe cê ônlaine", "The Bridge": "dâ bridge", "Wall Street": "uól estrit",
    "Houston Rockets": "Ríuston Róquets", "CCTV": "cê cê tê vê", "China Media Group": "Tchaina Mídia Grup",
    "China Mobile": "Tchaina Môbail", "Le Monde": "Lê Mônde", "La Liga": "Lá Liga", "NBA": "ene bê á",
    "2021/22": "2021 e 22", "Tsé-Tung": "Tsé-Tung", "On ": "Ón ", "On,": "Ón,", "On —": "Ón —",
    "pela On": "pela Ón", "da On": "da Ón", "TV": "tê vê", "1,4": "um vírgula quatro", "380": "trezentos e oitenta",
    "6%": "6 por cento", "10%": "10", "15%": "15 por cento", "Pra ": "Pra ", "€": "",
}


def fala_tts(txt):
    for k, v in PRON.items():
        txt = txt.replace(k, v)
    return txt.replace("'", "").replace("—", ",").replace("…", ",")
