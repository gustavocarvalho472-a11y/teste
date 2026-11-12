#!/usr/bin/env python3
"""Builds build/timeline.json: every scene with exact frame timing synced to the voice-over."""
import json, re, subprocess, os

ROOT = os.path.dirname(os.path.abspath(__file__))
FPS = 25
VO = lambda i: f"{ROOT}/assets/vo/ch{i}.mp3"


def G(type_, **p):  # full-frame studio graphic
    return {"gfx": {"type": type_, **p}}


def S(bg, type_="none", **p):  # stock footage + transparent overlay
    return {"bg": bg, "gfx": {"type": type_, **p}}


CHAPTERS = [
    {"label": "THE 115 FILES", "music": "beat", "beats": [
        ("Between 2017 and 2023, Manchester City didn't just win English football. They owned it.",
         S("match1+crowd2", "stat", big="2017 – 2023", label="MANCHESTER CITY'S ERA OF DOMINANCE")),
        ("Five Premier League titles in six seasons.",
         G("icons", count=5, label="PREMIER LEAGUE TITLES", sub="IN SIX SEASONS")),
        ("A hundred points in a single campaign.",
         S("", "stat", big="100", label="POINTS · 2017/18 SEASON")),
        ("More than a billion euros spent building Pep Guardiola's dream squad.",
         G("counter", prefix="€", value=1000000000, suffix="+", label="SPENT BUILDING THE SQUAD")),
        ("While the traditional giants were cutting costs and struggling in the transfer market, City seemed to live in a different reality.",
         S("match2", "word", text="A DIFFERENT REALITY", late=0.45)),
        ("They won everything, and on top of that, they kept announcing record commercial revenues, outearning clubs with far bigger global fanbases.",
         G("trend", title="COMMERCIAL REVENUE", note="SOURCE: MANCHESTER CITY ANNUAL REPORTS · ROUNDED", data=[["2017/18", 232], ["2018/19", 227], ["2019/20", 246], ["2020/21", 272], ["2021/22", 310], ["2022/23", 341]])),
        ("It looked too good to be true.",
         S("stadium_night", "word", text="TOO GOOD TO BE TRUE?")),
        ("It was.", {**G("bigtext", lines=["IT WAS."], bare=True), "mute_music": True}),
        ("After years of investigation, Manchester City was found guilty of 114 financial breaches: inflated accounts, sponsorships that weren't what they claimed to be, and documents hidden from regulators.",
         G("list", tag="THE VERDICT", title="114 FINANCIAL BREACHES", t0=0.42,
           items=["Inflated accounts", "Sponsorships that weren't what they claimed to be", "Documents hidden from regulators"])),
        ("And none of it would have come out if it weren't for one man, sitting thousands of kilometers from Manchester, with a computer and 3.4 terabytes of leaked confidential files.",
         S("laptop_dark+keyboard", "stat", big="3.4 TB", label="OF LEAKED CONFIDENTIAL FILES", late=0.55)),
    ]},
    {"num": "01", "title": "THE FIRST DOMINO", "music": "beat", "beats": [
        ("November 2015. The phone of FC Twente's president won't stop ringing.",
         G("map", center=[5, 51], scale=2600, title="NOVEMBER 2015", zoom=0, k=1.9,
           pins=[{"n": "ENSCHEDE · FC TWENTE", "lon": 6.89, "lat": 52.22}])),
        ("Journalists want answers about confidential documents that have just appeared on a website hosted on a Russian server.",
         G("terminal", title="INCOMING", lines=["GET /documents/twente_contracts.pdf", "host .............. *.ru", "status ............ PUBLIC", "classification .... CONFIDENTIAL", "source ............ UNKNOWN"])),
        ("They're Twente's secret contracts with an investment fund called Doyen Sports.",
         S("contract", "lower", name="DOYEN SPORTS", role="Investment fund · secret contracts with FC Twente")),
        ("In exchange for five million euros to rescue its finances, the club had sold percentages of seven players' economic rights to the fund.",
         G("flow", title="THE DEAL", nodes=[{"l": "DOYEN SPORTS", "s": "INVESTMENT FUND"}, {"l": "FC TWENTE", "s": "CLUB"}],
           fwd="€5 MILLION", back="% OF 7 PLAYERS' ECONOMIC RIGHTS")),
        ("It's called third-party ownership, T.P.O., and it's banned.",
         G("define", term="TPO", full="THIRD-PARTY OWNERSHIP", body="An outside investor owns a share of a player's future transfer value.", stamp="BANNED")),
        ("But the worst part was a single clause. If Twente turned down a transfer offer that Doyen wanted to accept, the club owed a massive fine. In practice, Doyen was the one running the club.",
         G("doc", head="PARTICIPATION AGREEMENT · VETO CLAUSE", lines=["If the Club rejects a transfer offer", "that the Fund wishes to accept,", "*the Club shall pay the Fund a penalty.*"], foot="In practice: the fund decides.")),
        ("The Dutch federation banned Twente from European competition for three years, with penalties that nearly bankrupted it.",
         S("seats", "word", text="BANNED", sub="EUROPEAN COMPETITION · 3 YEARS", stamp=True)),
        ("In the months that followed, the same source leaked tax-avoidance schemes involving stars like Cristiano Ronaldo and José Mourinho, plus the files that would later bring down City's empire.",
         G("names", title="THE SAME SOURCE", t0=0.3, people=[{"n": "CRISTIANO RONALDO", "r": "TAX FILES"}, {"n": "JOSÉ MOURINHO", "r": "TAX FILES"}, {"n": "MANCHESTER CITY", "r": "THE SPONSORSHIP FILES", "hot": True}])),
    ]},
    {"num": "02", "title": 'WHO IS "JOHN"?', "music": "drone", "beats": [
        ("Behind that mountain of data, and the panic spreading through Europe's boardrooms, there was just one name.",
         S("boardroom", "word", text="ONE NAME", late=0.6)),
        ("Rui Pedro Gonçalves Pinto.", G("bigtext", kicker="THE SOURCE", lines=["RUI PEDRO", "GONÇALVES PINTO"])),
        ("Born in Portugal. A young FC Porto fan. A history student with no formal training in tech. He taught himself computing.",
         S("porto", "chips", title="RUI PINTO", items=["Born in Portugal", "FC Porto fan", "History student", "Self-taught in computing"])),
        ('In 2015, living in Budapest under the alias "John", he launched Football Leaks.',
         G("map", center=[6, 46.5], scale=1500, title="2015", route=[0, 1], foot='ALIAS: "JOHN"',
           pins=[{"n": "PORTO", "lon": -8.61, "lat": 41.15}, {"n": "BUDAPEST", "lon": 19.04, "lat": 47.5}])),
        ("His goal: expose how football had been taken over by shadowy investment funds, tax evasion and corruption.",
         G("terminal", title="FOOTBALL LEAKS", lines=["> football_leaks --publish", "target ........ investment funds", "target ........ tax evasion", "target ........ corruption", "status ........ ONLINE"])),
        ("By breaking into servers and running phishing attacks, Rui gathered more than 70 million confidential documents.",
         G("counter", value=70000000, suffix="+", label="CONFIDENTIAL DOCUMENTS", sub="3.4 TERABYTES OF DATA", t0=0.35)),
        ("Too much for one person to read. So he partnered with European Investigative Collaborations, the E.I.C., a journalism consortium led by Germany's Der Spiegel.",
         S("keyboard2+cables", "lower", name="EIC", role="European Investigative Collaborations · led by Der Spiegel", late=0.3)),
        ("As the stories exploded, Rui became a target, hunted by billion-dollar funds and threatened by the power networks inside football.",
         S("walk_night+corridor", "word", text="A TARGET", late=0.25)),
    ]},
    {"num": "03", "title": "THE LINE HE CROSSED", "music": "drone", "beats": [
        ("At home in Portugal, the leaks hit like an earthquake.",
         S("", "word", text="PORTUGAL", sub="THE LEAKS HIT HOME")),
        ("They exposed internal Benfica emails pointing to alleged influence over refereeing, favoritism inside the federation, and privileged access to confidential judicial reports.",
         G("list", tag="ALLEGED · THE BENFICA EMAILS", title="WHAT THE LEAKS POINTED TO", t0=0.3,
           items=["Influence over refereeing", "Favoritism inside the federation", "Access to confidential judicial reports"])),
        ("The scandal triggered corruption investigations into club officials.",
         S("lisbon", "lower", name="LISBON", role="Corruption investigations opened into club officials")),
        ("But the line between activism and crime got crossed.",
         S("handcuffs", "word", text="ACTIVISM", sub="OR CRIME?")),
        ("Rui tried to get one million euros from Doyen in exchange for not publishing the files, something he'd later call a childish mistake.",
         G("counter", prefix="€", value=1000000, label="DEMANDED FROM DOYEN SPORTS", sub="“A CHILDISH MISTAKE” — RUI PINTO", sublate=0.6)),
        ("In January 2019, he was arrested in Budapest, extradited to Portugal and charged with 147 crimes.",
         G("map", center=[6, 46.5], scale=1500, title="JANUARY 2019", route=[0, 1], foot="147 CRIMINAL CHARGES",
           pins=[{"n": "BUDAPEST · ARRESTED", "lon": 19.04, "lat": 47.5}, {"n": "LISBON · EXTRADITED", "lon": -9.14, "lat": 38.72}])),
        ("In court, he called himself a whistleblower, someone acting in the public interest.",
         S("courthouse", "word", text="WHISTLEBLOWER", sub="ACTING IN THE PUBLIC INTEREST", late=0.3)),
        ("And to reduce his sentence, he handed his encrypted hard drives to authorities in France, Belgium and Germany.",
         S("harddrive", "chips", title="ENCRYPTED DRIVES HANDED TO", items=["FRANCE", "BELGIUM", "GERMANY"], t0=0.5)),
        ("What was on them was a lot more than harmless chatter.",
         G("terminal", title="DECRYPTING", lines=["volume_01 ........ UNLOCKED", "volume_02 ........ UNLOCKED", "volume_03 ........ UNLOCKED", "files indexed .... 70,000,000+"])),
    ]},
    {"num": "04", "title": "EUROPE'S UNDERWORLD", "music": "beat", "beats": [
        ("The files showed Europe's biggest clubs operating in a world with no rules.",
         S("office_night", "word", text="NO RULES", late=0.5)),
        ("In 2018, Football Leaks published the emails that revealed the plans for a European Super League, a closed tournament designed by the continent's richest clubs to make billions.",
         G("define", term="SUPER LEAGUE", full="REVEALED BY FOOTBALL LEAKS · 2018", body="A closed tournament designed by the continent's richest clubs.", small=True)),
        ("At Paris Saint-Germain, after spending over 400 million euros on Neymar and Mbappé, the documents exposed crude accounting tricks to get around Financial Fair Play.",
         S("paris+match3", "stat", big="€400M+", label="PARIS SAINT-GERMAIN · NEYMAR AND MBAPPÉ", late=0.2)),
        ("PSG signed an inflated deal with the Qatar Tourism Authority: officially worth 200 million euros a year. UEFA's auditors valued it at around 3 million.",
         G("bars", title="QATAR TOURISM AUTHORITY DEAL · VALUE PER YEAR",
           items=[{"l": "OFFICIAL VALUE", "v": 200, "d": "€200M", "at": 0.42}, {"l": "UEFA AUDITORS' VALUATION", "v": 3, "d": "≈ €3M", "at": 0.78, "hot": True}])),
        ("In other words, state money was being pumped into the club and dressed up as commercial revenue.",
         G("flow3", title="HOW IT WORKED", nodes=["STATE MONEY", "“SPONSORSHIP”", "THE CLUB"], foot="BOOKED AS COMMERCIAL REVENUE")),
        ("Other files revealed a network of offshore companies used by Cristiano Ronaldo to shield more than 150 million euros in image rights, which led to his tax conviction in Spain.",
         S("", "chips", title="€150M+ IN IMAGE RIGHTS", items=["British Virgin Islands", "Jersey", "Luxembourg", "Tax conviction in Spain"], t0=0.2)),
        ("Der Spiegel also published documents on the rape allegation made by Kathryn Mayorga against Ronaldo in Las Vegas in 2009, including a 375,000 dollar confidentiality settlement. Ronaldo has always denied the allegation, and no criminal charges were filed.",
         G("list", tag="ALLEGATION · DENIED", title="LAS VEGAS, 2009", t0=0.12,
           items=["Der Spiegel publishes documents on the allegation", "$375,000 confidentiality settlement", "Ronaldo denies the allegation · no criminal charges filed"], lasthot=True, ats=[0.12, 0.5, 0.74])),
        ("But among all those scandals, one club kept showing up again and again.",
         S("cables", "word", text="ONE CLUB", sub="KEPT SHOWING UP", late=0.3)),
        ("Manchester City.", G("bigtext", lines=["MANCHESTER", "CITY"], sky=True)),
    ]},
    {"num": "05", "title": "THE CITIZENS", "music": "beat", "beats": [
        ("The man behind City's 2008 takeover is Sheikh Mansour, a member of Abu Dhabi's royal family, Deputy Prime Minister of the U.A.E., and head of ADUG, a state-linked investment vehicle backed by hundreds of billions of dollars.",
         S("skyline_night+money+skyline_day", "chips", title="SHEIKH MANSOUR", items=["Owner of Manchester City since 2008", "Abu Dhabi royal family", "Deputy Prime Minister of the UAE", "Head of ADUG"], t0=0.2)),
        ("He also owns City Football Group, today chaired by Khaldoon Al Mubarak.",
         G("org", nodes=["SHEIKH MANSOUR", "ADUG", "CITY FOOTBALL GROUP", "MANCHESTER CITY"], side="CHAIRMAN · KHALDOON AL MUBARAK")),
        ("In 2011, UEFA introduced Financial Fair Play: clubs couldn't spend more than they earned.",
         G("define", term="FFP", full="FINANCIAL FAIR PLAY · UEFA · 2011", body="Clubs cannot spend more than they earn.")),
        ("The Football Leaks emails showed that City's main sponsor, Etihad Airways, a company owned by the Abu Dhabi government, was officially paying 67.5 million pounds a year.",
         S("", "stat", big="£67.5M", label="ETIHAD AIRWAYS · OFFICIAL SPONSORSHIP PER YEAR", late=0.55)),
        ("But emails from City's own finance director admitted Etihad was only paying 8 million.",
         G("doc", head="INTERNAL EMAIL · FINANCE", lines=["Etihad's direct contribution", "remains at *£8 million.*", "The balance is covered by the shareholder."])),
        ("The other 59.5 million? It came straight from ADUG, the Sheikh's own fund.",
         G("bars", title="WHO REALLY PAID THE £67.5M", items=[{"l": "ETIHAD AIRWAYS", "v": 8, "d": "£8M", "at": 0.08}, {"l": "ADUG · THE OWNER'S FUND", "v": 59.5, "d": "£59.5M", "at": 0.42, "hot": True}])),
        ("In the Guardiola era, the scheme got more sophisticated. City Football Group bought Girona in Spain, in partnership with Pere Guardiola, Pep's brother.",
         S("", "chips", title="CITY FOOTBALL GROUP", items=["Buys Girona, in Spain", "Partner: Pere Guardiola"], t0=0.45)),
        ("Then the hunt for artificial revenue reached a whole new level with the Wega case. In 2015, City announced a 40 million pound sponsorship with this supposed tech and payment-card company.",
         G("counter", prefix="£", value=40000000, label="THE WEGA SPONSORSHIP · 2015", sub="A SUPPOSED TECH AND PAYMENT-CARD COMPANY", t0=0.5, sublate=0.75)),
        ("When journalists checked the company records, they found a sham. No products. No registered employees. No assets. Total equity: 1,200 pounds.",
         G("list", tag="COMPANY RECORDS", title="WEGA", t0=0.4, items=["No products", "No registered employees", "No assets", "Total equity: £1,200"], lasthot=True)),
        ("At the height of it, City sold its players' image rights to a third-party finance company, Fordham. From then on, Fordham paid those millions to the players, and the cost magically vanished from the reports City sent to UEFA.",
         G("flow3", title="IMAGE RIGHTS", nodes=["MANCHESTER CITY", "FORDHAM", "THE PLAYERS"], foot="THE COST VANISHES FROM THE REPORTS SENT TO UEFA", late=0.3)),
        ("February 2020: UEFA banned City from European competition for two years. Months later, the ban was overturned on appeal, and the club got away with a 10 million euro fine.",
         G("article", img="art_nyt.jpg", tag="PRESS · FEBRUARY 2020", marks=[[0.045, 0.07, 0.72, 0.235, 0.1], [0.045, 0.315, 0.775, 0.235, 0.19], [0.655, 0.615, 0.238, 0.13, 0.33]], stamp="OVERTURNED", stampat=0.6, foot="FINAL PENALTY: A €10 MILLION FINE", footat=0.8)),
        ("Then, in 2026, a new verdict, this time from the Premier League. City was found guilty of 114 of the 115 charges brought against it. The club denied every accusation and continues to insist it is innocent.",
         G("counter", value=114, suffix=" / 115", label="CHARGES PROVEN · PREMIER LEAGUE · 2026", sub="MANCHESTER CITY DENIES ALL CHARGES", t0=0.3, sublate=0.68)),
    ]},
    {"num": "06", "title": "THE POLITICAL CONNECTIONS", "music": "drone", "beats": [
        ("The 115 charges show something bigger: football has become hostage to diplomacy and state interests.",
         S("london", "word", text="DIPLOMACY", sub="AND STATE INTERESTS", late=0.4)),
        ("British government documents showed that the embassy in Abu Dhabi and the Foreign Office in London were following the City case step by step.",
         G("map", center=[27, 46.5], scale=740, title="UK GOVERNMENT DOCUMENTS", route=[0, 1], foot="FOLLOWING THE CASE STEP BY STEP",
           pins=[{"n": "LONDON · FOREIGN OFFICE", "lon": -0.12, "lat": 51.5}, {"n": "ABU DHABI · UK EMBASSY", "lon": 54.37, "lat": 24.45}])),
        ("The U.A.E. is a giant investor in the UK, with more than 10 billion pounds in energy, real estate and infrastructure.",
         G("counter", prefix="£", value=10, suffix=" BILLION+", label="UAE INVESTMENT IN THE UK", sub="ENERGY · REAL ESTATE · INFRASTRUCTURE", t0=0.3, sublate=0.6)),
        ("Truly punishing City could mean risking a diplomatic crisis, and that money.",
         S("manchester", "word", text="THE RISK", sub="A DIPLOMATIC CRISIS")),
    ]},
    {"num": "07", "title": "THE PRICE OF TELLING", "music": "finale", "beats": [
        ("One more powerful figure played a central role behind the scenes: Gianni Infantino.",
         G("bigtext", kicker="ALLEGATION", lines=["GIANNI", "INFANTINO"], sub="FIFA PRESIDENT", late=0.55)),
        ("According to Rui Pinto, the FIFA president knew about these backroom manipulations and even held secret meetings to soften the punishments for clubs. Infantino has denied any wrongdoing.",
         S("handshake+boardroom", "lower", name="ACCORDING TO RUI PINTO", role="Infantino has denied any wrongdoing")),
        ("Poking that hornet's nest came at a very high price. Rui Pinto spent years in Portugal's witness protection program, but lost that status in October of this year, leaving him exposed to real danger.",
         S("corridor+walk_night", "chips", title="RUI PINTO", items=["Years in witness protection", "Protection lost this October"], t0=0.35)),
        ("What actually decides the leagues and titles that generate billions of euros are deals far more political than sporting. Deals that feel distant, or even like conspiracy theories, made by powerful people who put themselves above the rules and the law.",
         S("trophy+match1+seats", "word", text="ABOVE THE RULES", late=0.72)),
        ("But in the end, all it took was one guy with an internet connection, and journalists free to do their jobs, to prove that when a project looks too good to be true...",
         S("hacker+laptop_dark", "none")),
        ("maybe it really is.", G("bigtext", lines=["MAYBE IT", "REALLY IS."], bare=True)),
    ]},
]


B, R, P, I = "city_bbc_long", "rui_trial_reuters", "city_pep_official", "city_ban_itv"
def sh(src, *idx): return [("shot", src, i) for i in idx]
def win(src, a, b): return [("win", src, a, b)]
NDR = "rui_ndr"; NC = "crop=iw*0.78:ih*0.76:iw*0.11:ih*0.02,"
def shc(src, crop, *idx): return [("shot", src, i, crop) for i in idx]
def st(*keys): return [("stock", k) for k in keys]
POOLS = {
 "celeb": sh(B, 2, 4, 5, 6, 8, 3, 27, 26, 37) + sh("city_stage23", 9, 1, 3, 5, 0, 7, 4, 8, 2) + sh("city_parade23", 0, 1, 2, 3, 4) + sh("city_parade18", 1, 4, 5) + sh("city_parade22", 0, 1) + sh(I, 8, 9) + sh(P, 32, 36, 40, 31),
 "ucl": sh("city_stage23", 9) + sh(P, 31, 29) + sh(B, 2) + sh(P, 30),
 "goals": sh(I, 0) + sh(P, 22, 19) + sh(I, 2) + sh(P, 29, 30),
 "etihad": sh(B, 43, 7, 21, 11) + win(B, 352.74, 357.34) + sh(B, 34) + sh(R, 9, 8),
 "store": sh(R, 10, 11),
 "pep": sh(P, 28, 37, 39, 27, 23, 34, 26, 38, 40) + sh(B, 23) + sh(I, 7) + sh("city_parade22", 2) + sh("city_stage23", 6),
 "match": sh(I, 0, 5, 2, 1) + sh(P, 29, 19, 30, 22) + st("match1"),
 "rui": shc(NDR, NC, 64, 68, 76, 77, 73) + sh(NDR, 51, 57, 66, 52, 75, 78, 60),
 "ruiroom": sh(NDR, 13, 54, 58),
 "leakdocs": sh(B, 33),
 "court": sh(R, 3, 2, 6, 5, 4, 7, 13, 12, 14),
 "arrest": sh(B, 45, 46, 47, 61, 62, 63, 70, 71, 72),
 "photo": sh(R, 16, 15),
 "police": sh(R, 0, 1) + sh(B, 64),
 "porto": sh(B, 49, 48, 50) + st("porto"),
 "spiegel": sh(B, 56, 31, 59, 60, 32),
 "uefa": sh(B, 28, 29, 30),
 "mansour": sh("mansour_goal", 0, 4, 2, 6, 1) + sh(B, 24, 25),
 "abudhabi": sh("abudhabi_drone", 0, 10, 16) + st("skyline_night"),
 "psg": sh("neymar_present", 1, 7) + sh(NDR, 10, 9) + sh("neymar_present", 2, 4, 9, 5, 6, 8, 3) + st("paris"),
 "ronaldo": win("ronaldo_court_ap", 2, 34),
 "mourinho": win("mourinho_court", 7, 28) + sh("mourinho_court", 3, 4),
 "infantino": sh(NDR, 11) + win("infantino_afp", 47, 52) + win("infantino_afp", 21, 46),
 "twente": win("twente_fans", 6, 66),
 "lisbon": st("lisbon") + sh(B, 67),
 "budapest": sh(B, 54) + sh(NDR, 28, 25, 20, 45) + st("budapest"),
 "london": st("london"), "manchester": st("manchester"),
 "tech": st("laptop_dark", "keyboard2", "hacker", "cables", "keyboard", "harddrive"),
 "docs": st("contract", "boardroom", "sign", "handshake", "office_night", "spreadsheet"),
 "money": st("money"), "plane": st("plane"),
}
SCENE_POOLS = [
 ["ucl+goals+celeb", "celeb", "goals+celeb", "pep+match", "match+etihad", "etihad+celeb", "etihad", "etihad", "etihad+pep", "rui+arrest+ruiroom"],
 [None, "tech", "docs", "twente", "docs+twente", "docs", "twente", "ronaldo+mourinho+etihad"],
 ["spiegel+ruiroom", "rui", "porto+rui", None, "ruiroom+tech", "ruiroom+tech+spiegel", "spiegel+rui", "rui+court+arrest"],
 ["lisbon", "lisbon+docs", "police+lisbon", "arrest+rui", "money+rui", None, "court+rui", "tech+court", "tech"],
 ["docs", "uefa+match", "psg", "psg", "psg+docs", "ronaldo", "ronaldo+docs", "etihad", "celeb"],
 ["mansour+abudhabi", "mansour+etihad", "uefa", "etihad+plane", "leakdocs+etihad", "mansour+abudhabi", "pep", "store+docs", "docs", "celeb+match", "uefa+match", "etihad+pep+celeb"],
 ["london", None, "abudhabi+london", "manchester+etihad"],
 ["infantino", "infantino", "rui+court+arrest", "pep+mansour+celeb+etihad", "rui+tech+rui", "etihad"],
]
SCENE_CUT = {(1, 0): 1.8, (1, 1): 1.6, (1, 2): 1.3}
SHOTS = json.load(open(f"{ROOT}/build/shots.json"))
_items = {}; _cur = {}; _len = {}
def pool_items(name):
    if name not in _items:
        out = []
        for it in POOLS[name]:
            if it[0] == "stock":
                p = f"{ROOT}/assets/stock/{it[1]}.mp4"; L = _len.setdefault(p, dur(p)); spans = [(0.3, L - 0.3)]
            elif it[0] == "win":
                p = f"{ROOT}/assets/real/{it[1]}.mp4"; spans = [(it[2], it[3])]
            else:
                p = f"{ROOT}/assets/real/{it[1]}.mp4"; a, b = SHOTS[it[1]][it[2]]; spans = [(a + 0.12, b - 0.12)]
            crop = it[3] if it[0] == "shot" and len(it) > 3 else ""
            for a, b in spans:
                if b - a > 9.5:
                    k = int((b - a) // 4.7); out += [(p, a + i * (b - a) / k, a + (i + 1) * (b - a) / k, crop) for i in range(k)]
                else:
                    out.append((p, a, b, crop))
        _items[name] = out; _cur[name] = 0
    return _items[name]
def allocate(pools, nf, cut=4.0):
    D = nf / FPS; n = max(1, round(D / cut)); names = pools.split("+"); takes = []; base = nf // n
    for i in range(n):
        frames = base if i < n - 1 else nf - base * (n - 1); d = frames / FPS; name = names[i % len(names)]; items = pool_items(name)
        for _ in range(len(items)):
            p, a, b, crop = items[_cur[name] % len(items)]; _cur[name] += 1; L = b - a
            if L >= d or d / L <= 1.75: break
        slow = max(1.0, d / L); ss = a + (min(1.2, (L - d) / 2) if L > d else 0)
        takes.append({"src": p, "ss": round(ss, 2), "slow": round(slow, 3), "frames": frames, "crop": crop})
    return takes


def dur(path):
    return float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path]))


def silences(path):
    out = subprocess.run(["ffmpeg", "-i", path, "-af", "silencedetect=noise=-34dB:d=0.2", "-f", "null", "-"], capture_output=True, text=True).stderr
    st = [float(x) for x in re.findall(r"silence_start: ([\d.]+)", out)]
    en = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", out)]
    return list(zip(st, en))


def weight(t):
    return sum(3.2 if c.isdigit() else 1 for c in t) + 6 * t.count(".") + 3 * t.count(",")


def beat_times(i, beats):
    d = dur(VO(i)); sil = silences(VO(i))
    ws = [weight(b[0]) for b in beats]; tot = sum(ws)
    cuts = [0.0]; acc = 0; last = 0.0
    for w in ws[:-1]:
        acc += w; exp = acc / tot * d
        cand = [(abs((s + e) / 2 - exp) - min(e - s, 0.8), s, e) for s, e in sil if s > last + 0.6 and abs((s + e) / 2 - exp) < 2.5]
        if cand:
            _, s, e = min(cand); t = max(s + 0.05, e - 0.18)
        else:
            t = exp
        cuts.append(t); last = t
    return cuts, d


def main():
    scenes = []; t = 0.0; vo = []; music = []; auto = [2]
    def add(d, **k):
        nonlocal t
        sid = k.pop("sid", None)
        if not sid: sid = f"s{auto[0]:03d}"; auto[0] += 1
        scenes.append({"id": sid, "start": t, "dur": d, **k}); t += d
    music.append({"track": "drone", "start": 0})
    BBC = f"{ROOT}/assets/real/city_bbc_long.mp4"; SKY = f"{ROOT}/assets/real/soriano_sky.mp4"; NDRF = f"{ROOT}/assets/real/rui_ndr.mp4"
    add(5.2, sid="b000", gfx={"type": "caps", "name": "", "role": "", "phrases": [{"t0": 0.15, "t1": 1.7, "text": "*Champions* of Europe.", "q": 0}, {"t0": 1.8, "t1": 3.4, "text": "5 league titles in 6 years.", "q": 0}, {"t0": 3.5, "t1": 5.1, "text": "*Too good* to be true?", "q": 0}]},
        label="", pools="ucl+goals+celeb+goals", cut=1.3)
    COLD = [
        (BBC, 245.2, 6.0, "PEP GUARDIOLA", "Manchester City manager · 2023", "", [(0.15, 2.45, "How confident are you that you have *been told everything?*", 1), (3.1, 5.7, "We are *already being condemned.*", 0)]),
        (SKY, 0.0, 6.6, "FERRAN SORIANO", "Manchester City chief executive · 2026", "", [(2.1, 3.75, "Do you *apologise* to football fans?", 1), (4.0, 6.4, "I have nothing to say.", 0)]),
        (SKY, 11.3, 6.0, "FERRAN SORIANO", "Manchester City chief executive · 2026", "", [(0.2, 2.6, "Is all this success *sham contracts?*", 1), (2.65, 4.4, "Is this a *sham club?*", 1), (4.6, 5.9, "Thank you.", 0)]),
        (NDRF, 426.9, 4.0, "RUI PINTO", "Football Leaks · the source", "crop=iw*0.60:ih*0.70:iw*0.10:ih*0.03,", [(0.1, 1.9, "I'm not a hacker.", 0), (2.0, 3.85, "I'm a *whistleblower.*", 0)]),
        (BBC, 92.6, 6.4, "", "BBC News report · 2026", "", [(0.1, 2.7, "Seismic news.", 0), (3.5, 6.25, "City found *guilty* of the majority of *115 charges.*", 0)]),
    ]
    for k, (src, ss, d, name, role, crop, ph) in enumerate(COLD):
        add(d, sid=f"c{k:03d}", gfx={"type": "caps", "name": name, "role": role, "phrases": [{"t0": a, "t1": b, "text": x, "q": q} for a, b, x, q in ph]}, label="",
            takes=[{"src": src, "ss": ss, "slow": 1.0, "frames": round(d * FPS), "crop": crop}], nat={"src": src, "ss": ss})
    add(5.0, sid="s001", gfx={"type": "sting", "title": "THE 115 CHARGES", "sub": "THE HACKER WHO PULLED THE THREAD"}, label="")
    for ci, ch in enumerate(CHAPTERS, 1):
        if "num" in ch:
            music.append({"track": ch["music"], "start": t})
            add(3.4, gfx={"type": "bumper", "num": ch["num"], "title": ch["title"]}, label="")
        else:
            music.append({"track": ch["music"], "start": t - 5.0})
        label = (ch.get("num", "") + " · " + ch["title"]) if "num" in ch else ch["label"]
        lead = 0.35; t += 0  # scene starts slightly before the voice
        cuts, d = beat_times(ci, ch["beats"])
        vo_start = t + lead
        vo.append({"file": f"ch{ci}.mp3", "start": vo_start, "dur": d})
        n = len(ch["beats"])
        for bi, (text, vis) in enumerate(ch["beats"]):
            s0 = vo_start + cuts[bi] if bi else t
            s1 = vo_start + (cuts[bi + 1] if bi + 1 < n else d + 0.9)
            t = s0
            vis = dict(vis); vis.pop("bg", None)
            add(s1 - s0, text=text, label=label, vo0=vo_start + cuts[bi], pools=SCENE_POOLS[ci - 1][bi], cut=SCENE_CUT.get((ci, bi), 4.0), **vis)
    music.append({"track": "finale", "start": t, "keep": True})
    add(14.0, gfx={"type": "end"}, label="")
    # frame-quantise
    for s in scenes:
        s["f0"] = round(s["start"] * FPS)
    for a, b in zip(scenes, scenes[1:]):
        a["nf"] = b["f0"] - a["f0"]
    scenes[-1]["nf"] = round(scenes[-1]["dur"] * FPS)
    for s in scenes:
        s["start"] = s["f0"] / FPS; s["dur"] = s["nf"] / FPS
    for s in scenes:
        if s.get("pools"): s["takes"] = allocate(s["pools"], s["nf"], s.get("cut", 4.0))
        if s["gfx"]["type"] in ("article", "map"): s.pop("takes", None)
        s["framed"] = "takes" in s and s["gfx"]["type"] in ("none", "stat", "word", "lower", "chips", "caps")
    total = (scenes[-1]["f0"] + scenes[-1]["nf"]) / FPS
    os.makedirs(f"{ROOT}/build", exist_ok=True)
    json.dump({"fps": FPS, "total": total, "scenes": scenes, "vo": vo, "music": music}, open(f"{ROOT}/build/timeline.json", "w"), indent=1, ensure_ascii=False)
    print(f"{len(scenes)} scenes, total {total/60:.2f} min")
    for s in scenes:
        print(f'{s["id"]} {s["start"]:7.2f} {s["dur"]:6.2f} {(s.get("pools") or "-")[:22]:22s} {len(s.get("takes",[]))} {s["gfx"]["type"]:9s} {s.get("text","")[:60]}')


if __name__ == "__main__":
    main()
