# Prompts para o Google Flow: Seis frases que Jesus nunca disse

## Passo 1: a foto padrão (referência de personagens e estilo)
Gere esta imagem primeiro, em 16:9, e escolha a melhor das variações.

```
Character reference sheet, three characters standing side by side on a plain deep black background, full body, front view, evenly spaced, each with a small head-and-shoulders close-up above them.
LEFT: Jesus, a man in his thirties, long dark wavy hair, full beard, simple woven robe and mantle, calm kind eyes.
CENTER: the apostle Peter, a burly fisherman in his forties, short curly grey-streaked hair and thick beard, rough tunic with a rope belt.
RIGHT: a young man in his twenties in modern clothes, hooded jacket, jeans, sneakers, short dark hair, gaunt face.
Style: 19th-century wood engraving in the style of Gustave Doré, black and white only, fine cross-hatching, dramatic chiaroscuro, strong rim light, consistent line work across all three figures, no text, no labels, no frame, 16:9
```

**Melhor ainda (opcional):** gere os três personagens separados, trocando a linha de personagem e mantendo a de estilo. O Flow mantém o rosto com mais fidelidade quando cada "ingrediente" tem uma pessoa só.

## Passo 2: o prompt único para todas as cenas
1. No Flow, adicione a foto padrão como **ingrediente**.
2. Cole o prompt-mestre abaixo uma vez.
3. Troque **só a última linha** (CENA) para cada imagem.

O Flow gera de 1 a 4 variações por vez, e todas são da mesma cena. Por isso não existe um prompt que gere as 23 cenas diferentes de uma vez. Com o prompt-mestre fixo, as cenas saem todas no mesmo estilo e com os mesmos rostos.

```
Use the attached reference image for the characters' faces, hair, clothing and for the drawing style. Keep every character exactly as in the reference.
Style: 19th-century wood engraving in the style of Gustave Doré, black and white only, fine cross-hatching, dramatic chiaroscuro, strong rim light, subject isolated against a deep black background, cinematic composition, 16:9, no text, no frame, no color.
SCENE: [cole aqui a cena]
```

## As 23 cenas (cole uma de cada vez no lugar de [cole aqui a cena])
Salve com o nome indicado em `motor/img/nunca_disse/`.

| Nome | Cena |
|---|---|
| 01_encruzilhada | The young man stands alone at a crossroads at night, many dark paths splitting in every direction, one hand pressed against his chest, a single signpost with no words. |
| 02_reflexo | The young man kneels over a still pool, staring at his own idealized glowing reflection, the world around him dark and withered. |
| 05_labirinto | An anatomical human heart engraved as an intricate stone labyrinth seen from above, a tiny lost figure inside the maze, centered, glowing edges. No characters from the reference. |
| 06_cenaculo | Jesus speaks to eleven disciples at night in a stone upper room, a single oil lamp, solemn faces, long shadows. Peter sits closest to him. |
| 07_barco | A small wooden fishing boat tossed by enormous waves in a night storm, terrified men holding the mast, lightning splitting the sky. |
| 08_aguas | Jesus stands calm on the stormy sea, one hand extended, clouds breaking open above him with beams of light, waves around his feet. |
| 10_maos | The young man on his knees, open empty hands raised toward a beam of light falling from above, peaceful face, darkness around. |
| 11_monte | Jesus seated on a rocky hillside teaching, a vast crowd spread across the slopes below, the Sea of Galilee in the distance, wide epic shot, low sun behind clouds. |
| 12_fariseus | Jesus points calmly to his own chest while stern Pharisees in long robes point accusingly at disciples eating bread with unwashed hands, a stone water basin in the foreground. |
| 13_janela | The young man leans on a window ledge looking down at a crowded modern city street, arms crossed, cold expression, people below small and distant. |
| 14_sermao | Jesus stands among ordinary villagers, one hand raised mid-speech, a Roman soldier and a tax collector listening at the edge of the crowd. |
| 15_cruz | Jesus crucified, face lifted to the sky in prayer, Roman soldiers below casting lots for his garment, dark sky, a single shaft of light on the cross, seen from below. |
| 16_metro | The young man stands in a packed subway car, headphones on, staring at a glowing phone full of lists and alarms, tense jaw, faces blurred around him. |
| 17_aves | Jesus stands in a wheat field among listeners, pointing up to a flock of birds flying across a bright sky, children looking up. |
| 18_lirios | Close view of wild lilies in a hillside meadow, a hand gently touching one flower, soft morning light, dew drops. No characters from the reference. |
| 19_banco | The young man sits on a park bench with headphones, writing in a notebook, satisfied smile, his long shadow on the ground shaped like chains. |
| 20_adultera | Jesus crouches and writes in the dust with his finger, a frightened woman kneeling beside him, men with stones in their hands walking away one by one, temple courtyard. |
| 21_cruz_nas_costas | A man in a simple tunic seen from behind carries a rough wooden cross up a narrow mountain path toward the light, footprints of another person ahead of him on the path. |
| 22_cafe | The young man sits alone at a table by a sunlit window, a single coffee cup, an empty chair across, proud upright posture, dust in the light beams. |
| 23_videira | Jesus walks at night among old grapevines with his disciples, holding a living vine branch heavy with grapes, a cut dry branch on the ground at his feet, full moon. |
| 24_pedro_galo | Peter stands by a charcoal fire in a courtyard at night, hands over his face in anguish, a servant girl pointing at him, a rooster crowing on a wall against the dawn sky. |
| 25_pedro_praia | Jesus and Peter on a shore at dawn beside a small charcoal fire with fish and bread, Peter kneeling in tears, Jesus' hand on his shoulder, boats and nets behind. |
| 26_casa_rocha | A small stone house on a massive rock by the sea, enormous storm waves and wind crashing against it, lightning, a second house on the sand collapsing into the water. No characters from the reference. |

**Dica:** se uma cena começar a sair colorida ou realista, acrescente no fim da linha da cena: `black and white engraving, no color, no photorealism`.
