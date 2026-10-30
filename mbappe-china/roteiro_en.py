"""English version of the script (the published video is in English; PT is audio-only for review).

EN[id] overrides the block's fields: fala (narration + captions), txt (on-screen text), hl (print highlight),
ato (chapter). Adapted, not literal. PRON_EN fixes how the English TTS voice reads names.
"""

TITLE = "THE MEME CHINA WOULDN'T FORGIVE"

EN = {
    "S01": dict(ato="The hook", fala="This is Kylian Mbappé. One of the most expensive players on the planet."),
    "S02": dict(fala="And last week, he called the founder of China a dictator.", txt=("DICTATOR", "stamp")),
    "S03": dict(fala="Laughing."),
    "S04": dict(fala="This man is on China's money. He hangs over the gate of the Forbidden City."),
    "S05": dict(fala="To 1.4 billion people, Mbappé didn't make a joke. He insulted the father of the nation.",
                txt=("1.4 BILLION", "big")),
    "S06": dict(fala="And China did not forgive."),
    "S07a": dict(fala="Within 48 hours, state TV pulled him off the air."),
    "S07b": dict(fala="Three brands tore up their contracts."),
    "S07c": dict(fala="His accounts were silenced.", hl="his account blocked"),
    "S07d": dict(fala="Video games started erasing him."),
    "S07e": dict(fala="La Liga vanished from Chinese state TV."),
    "S07f": dict(fala="And the league's president rushed to the embassy to apologize."),
    "S08": dict(fala="Mbappé apologized too. In Chinese."),
    "S09": dict(fala="China's answer? Words are not enough.", txt=("WORDS ARE NOT ENOUGH", "stamp")),
    "S10a": dict(fala="How did a ten-second meme put almost half a billion dollars at risk?"),
    "S10b": dict(fala="And why didn't an apology save him?"),
    "S10c": dict(fala="Stay to the end, because the biggest loser in this story isn't Mbappé."),
    "S11": dict(ato="The nickname", fala="It all starts with a nickname. In football, Mbappé is called 'the dictator'.",
                txt=("THE DICTATOR", "big")),
    "S12": dict(fala="Not because of politics. Because of power. They say he runs the dressing room, picks the coach, "
                     "and writes his own contract."),
    "S13": dict(fala="The internet loved it. People started putting his face on generals, emperors and leaders "
                     "from history."),
    "S14": dict(fala="Until someone made this one."),
    "S15": dict(fala="And the problem is, in China, this man is not meme material."),
    "S16a": dict(fala="In the West, Mao Zedong is remembered for the Cultural Revolution and an iron-fisted rule."),
    "S16b": dict(fala="But to the Chinese state, he is the founder of the People's Republic, the man who ruled "
                      "from 1949 to 1976."),
    "S16c": dict(fala="In China, mocking Mao isn't an opinion. It's an insult.", txt=("IT'S AN INSULT", "stamp")),
    "S17": dict(fala="And Mbappé was about to learn that the hard way. Because he had a lot to lose there."),
    "S18": dict(ato="The Mbappé China loved",
                fala="Chinese fans loved him. They even had a cute nickname for him: Guigui, little turtle, "
                     "for his supposed resemblance to a Ninja Turtle.", txt=("GUIGUI 龟龟", "big")),
    "S19": dict(fala="About a million followers on Weibo. Another million on Xiaohongshu."),
    "S20": dict(fala="He had a bottled water with his own face on it."),
    "S21a": dict(fala="A deal with Mengniu, China's biggest dairy company. Another with Milkground, the cheese maker."),
    "S21b": dict(fala="And his shirt was Real Madrid's best seller in the country."),
    "S22": dict(fala="Mbappé wasn't just famous in China. He was a product.", txt=("A PRODUCT", "big")),
    "S23": dict(fala="And then he sat on this couch."),
    "S24": dict(ato="The sentence", fala="French show, The Bridge. A light segment. The question: 'which meme of "
                                         "yourself makes you laugh the most?'"),
    "S25": dict(fala="He picked this one. And described it as 'some guy… I think he's a Chinese dictator'.",
                txt=("“some guy… I think he's a Chinese dictator”", "type")),
    "S26": dict(fala="Notice: he didn't even know who it was. And to China, that was worse. The country's greatest "
                     "symbol was, to him, 'some guy'.", txt=("“SOME GUY”", "stamp")),
    "S27": dict(fala="The clip leaked onto Chinese social media. Within hours, it was one of the top trending "
                     "topics on Weibo."),
    "S28a": dict(ato="The revenge", fala="Punishment number one. October 26th, at night."),
    "S28b": dict(fala="China Media Group, owner of state broadcaster CCTV, cuts La Liga and every match "
                      "featuring Mbappé."),
    "S28c": dict(fala="Pulls his commercials off the air. Deletes the posts about him."),
    "S29a": dict(fala="Punishment two. The 27th. Dongpeng, the water brand, walks away. Mengniu walks away. "
                      "Milkground walks away."),
    "S29b": dict(fala="According to Le Monde, part of those deals was worth around 50 million yuan. Almost "
                      "7 million euros.", txt=("≈ €7 MILLION", "big")),
    "S30": dict(fala="And the brands' own shares tumbled on the stock market."),
    "S31": dict(fala="Punishment three. His Weibo and Xiaohongshu accounts are silenced for 'violating the rules'.",
                txt=("SILENCED", "stamp")),
    "S32a": dict(fala="Punishment four. Tencent's FC Online starts pulling Mbappé. The Chinese version of "
                      "eFootball does the same."),
    "S32b": dict(fala="In China, Real Madrid takes the virtual pitch without Mbappé."),
    "S33a": dict(fala="Punishment five. And this one crosses the ocean. A month earlier, On, the Swiss brand he "
                      "left Nike for, had made him a global ambassador."),
    "S33b": dict(fala="On Tuesday, On's shares fell almost 6% on Wall Street. And the brand wiped everything "
                      "Mbappé from its Chinese social media.", txt=("−6% IN ONE DAY", "big")),
    "S34": dict(fala="But remember this: none of these punishments is the most expensive one. The most expensive "
                     "one landed on twenty clubs that had nothing to do with the joke."),
    "S35": dict(ato="The real money",
                fala="August this year. La Liga president Javier Tebas flies to Beijing and signs with Migu, from "
                     "state-owned China Mobile. Exclusive digital rights in China until 2030. All 380 matches "
                     "every season."),
    "S36": dict(fala="The figure was never disclosed. But the market talks about something between 400 and 465 "
                     "million dollars."),
    "S37": dict(fala="And La Liga has been burned before. In 2021/22, a Chinese partner simply didn't pay. "
                     "A 45 million euro hole.", txt=("−€45M", "big")),
    "S38": dict(fala="So when state TV cuts the signal, the message isn't for TV. It's for a contract worth "
                     "almost half a billion."),
    "S39a": dict(fala="And Real Madrid? Between 10 and 15% of the club's international shirt and merchandise "
                      "sales come from China."),
    "S39b": dict(fala="And the club takes a cut of Mbappé's image rights. Every brand that tears up his contract "
                      "takes money out of Madrid too."),
    "S40": dict(fala="You may have seen that La Liga lost 900 million in China alone. That's not true. That's "
                     "what it earns from international rights worldwide. And the Migu deal, so far, still stands."),
    "S41": dict(fala="Which is worse. Because it means China hasn't used the big weapon yet. It just showed it has one."),
    "S42": dict(ato="The apologies that didn't work",
                fala="Mbappé posted an apology in three languages. He said his comment was ill-judged."),
    "S43": dict(fala="Real Madrid apologized. And Tebas did something rare: he met the Chinese ambassador and sent "
                     "a letter to state TV calling his own league's player's behavior unacceptable.",
                txt=("UNACCEPTABLE", "stamp")),
    "S44": dict(fala="The response? State TV said it will judge by actions. And demanded public, written apologies "
                     "from La Liga, Real Madrid and Mbappé."),
    "S45": dict(fala="On Chinese social media, the comment that went viral was: not accepted, not forgiven."),
    "S46": dict(fala="And to make it worse, a US congressional committee on China said publicly that he never "
                     "should have apologized."),
    "S47": dict(fala="Mbappé ended up caught between two superpowers. Because of a meme."),
    "S48": dict(ato="The lesson", fala="And he's not the first. In 2019, Özil criticized China, and state TV "
                                       "pulled an Arsenal match off the air."),
    "S49": dict(fala="That same year, a single tweet from a Houston Rockets executive made the NBA disappear from "
                     "Chinese TV."),
    "S50": dict(fala="The pattern is always the same. China doesn't fine you. It takes away access. And access to "
                     "1.4 billion people is the most valuable asset in sports.", txt=("IT TAKES AWAY ACCESS", "big")),
    "S51": dict(fala="When you reach Mbappé's level, you're no longer a person. You're a company. And every "
                     "sentence you say becomes a contract clause."),
    "S52": dict(fala="So: how does a ten-second meme put almost half a billion at risk? Because when you're a "
                     "global product, there's no such thing as a local joke."),
    "S53": dict(ato="Your turn", fala="Tell me in the comments: should he have apologized, or is the US Congress "
                                      "right? And if you want to know why Mbappé left Nike for On, that video is "
                                      "right here on screen."),
}

# word said when each logo drops in S29a (montar.py / timeline.py use it for the falls and paper rips)
FALL_WORD = "walks"

PRON_EN = {
    "Mbappé": "Em-bah-pay", "Kylian": "Kill-yan", "Weibo": "Way-bo", "Xiaohongshu": "Shao-hong-shoo",
    "Mengniu": "Mung-nyo", "Dongpeng": "Dong-pung", "Milkground": "Milk-ground", "Guigui": "Gway-gway",
    "Migu": "Mee-goo", "Tebas": "Teh-bass", "Özil": "Oh-zil", "Zedong": "Dzuh-dong", "CCTV": "C C T V",
    "2021/22": "2021-22", "1.4": "one point four", "6%": "6 percent", "15%": "15 percent", "Le Monde": "Luh Mond",
    "eFootball": "e-Football", "La Liga": "La Leega", "On,": "On,", "yuan": "yoo-an",
}
