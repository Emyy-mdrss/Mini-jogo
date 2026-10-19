
import os
import wave

import numpy as np
from scipy.signal import lfilter

SR = 22050
PASTA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sons")
os.makedirs(PASTA, exist_ok=True)

def hz(midi):
    return 440.0 * 2 ** ((midi - 69) / 12)


def tempo(dur):
    return np.arange(max(int(SR * dur), 1)) / SR


def fase(freq):
    return np.cumsum(freq) / SR


def quadrada(freq, duty=0.5):
    onda = np.where((fase(freq) % 1.0) < duty, 1.0, -1.0)
    return onda - (2 * duty - 1)         


def triangulo(freq):
    return 4 * np.abs((fase(freq) % 1.0) - 0.5) - 1


def serra(freq):
    return 2 * (fase(freq) % 1.0) - 1


def seno(freq):
    return np.sin(2 * np.pi * fase(freq))


def ruido(dur, semente=1):
    return np.random.RandomState(semente).uniform(-1, 1, max(int(SR * dur), 1))


def varrer(f0, f1, dur):
    t = tempo(dur)
    return f0 * (f1 / f0) ** (t / dur)


def passa_baixa(x, corte):
    a = 1 - np.exp(-2 * np.pi * corte / SR)
    return lfilter([a], [1, -(1 - a)], x)


def passa_alta(x, corte):
    return x - passa_baixa(x, corte)


def queda(n, rapidez=6.0, ataque=0.003):
    t = np.arange(n) / SR
    dur = n / SR
    return np.minimum(t / ataque, 1) * np.exp(-rapidez * t / dur)


def adsr(n, a, d, s, r):
    dur = n / SR
    a = min(a, dur * 0.25)
    r = min(r, dur * 0.45)
    d = min(d, max(dur - a - r, 0.001))
    pontos_t = [0, a, a + d, max(dur - r, a + d), dur]
    pontos_v = [0, 1, s, s, 0]
    return np.interp(np.arange(n) / SR, pontos_t, pontos_v)


def vibrato(freq, profundidade=0.01, taxa=6.0):
    t = np.arange(len(freq)) / SR
    return freq * (1 + profundidade * np.sin(2 * np.pi * taxa * t))


def misturar(*partes):
    n = max(len(p) for p in partes)
    saida = np.zeros(n)
    for p in partes:
        saida[:len(p)] += p
    return saida


def atrasar(x, segundos):
    return np.concatenate([np.zeros(int(SR * segundos)), x])


def emendar(*partes):
    return np.concatenate(partes)


def bip(f0, f1, dur, forma="q", duty=0.5, rapidez=6.0):
    f = varrer(f0, f1, dur) if f0 != f1 else np.full(max(int(SR * dur), 1), float(f0))
    onda = {"q": lambda: quadrada(f, duty), "t": lambda: triangulo(f),
            "s": lambda: seno(f), "w": lambda: serra(f)}[forma]()
    return onda * queda(len(f), rapidez)


def notas(lista, forma="q", duty=0.5, rapidez=3.0):
    return emendar(*[bip(f, f, d, forma, duty, rapidez) for f, d in lista])


def crush(x, niveis=8):
    return np.round(x * niveis) / niveis

def sfx_click():
    return bip(880, 1500, 0.07, "q", 0.5, 5)


def sfx_tecla():
    return bip(560, 430, 0.04, "t", rapidez=6)


def sfx_digita():
    return bip(720, 700, 0.022, "q", 0.25, 4)


def sfx_compra():
    return notas([(988, 0.07), (1319, 0.07), (1760, 0.18)], "q", 0.25)


def sfx_erro():
    return misturar(bip(170, 110, 0.2, "q", 0.5, 3), bip(120, 85, 0.2, "q", 0.25, 3) * 0.7)

def sfx_tiro_mimi():
    return misturar(bip(1800, 700, 0.12, "t", rapidez=6), bip(3600, 1500, 0.05, "s", rapidez=9) * 0.25)


def sfx_tiro_robo():
    estouro = passa_baixa(ruido(0.05, 3), 4000) * queda(int(SR * 0.05), 9)
    return misturar(bip(950, 170, 0.14, "q", 0.25, 5), estouro * 0.4)


def sfx_dash():
    n = int(SR * 0.28)
    t = np.arange(n) / SR
    env = np.sin(np.pi * np.clip(t / 0.28, 0, 1)) ** 1.5
    vento = passa_alta(ruido(0.28, 5), 700) * env
    return misturar(vento * 0.8, bip(300, 1400, 0.28, "s", rapidez=2) * 0.35)


def sfx_espuma():
    rng = np.random.RandomState(11)
    saida = np.zeros(int(SR * 0.6))
    for i in range(14):
        inicio = int(rng.uniform(0, 0.4) * SR)
        f = rng.uniform(450, 1500)
        bolha = bip(f, f * 1.6, 0.07, "s", rapidez=5)
        saida[inicio:inicio + len(bolha)] += bolha * rng.uniform(0.4, 1.0)
    chiado = passa_alta(ruido(0.55, 8), 2500) * queda(int(SR * 0.55), 3) * 0.25
    return misturar(saida, chiado)


def sfx_moeda():
    return notas([(1319, 0.06), (1760, 0.2)], "q", 0.25, 4)


def sfx_vida():
    return notas([(1047, 0.07), (1319, 0.07), (1568, 0.07), (2093, 0.26)], "t", rapidez=3)


def sfx_powerup():
    sobe = [440 * 2 ** (i / 6) for i in range(9)]
    return notas([(f, 0.045) for f in sobe] + [(1760, 0.2)], "q", 0.25, 3)


def sfx_dano():
    estalo = passa_baixa(ruido(0.16, 4), 1800) * queda(int(SR * 0.16), 8)
    return misturar(bip(430, 90, 0.26, "q", 0.5, 4), estalo * 0.6)


def sfx_escudo():
    return misturar(bip(1900, 1880, 0.28, "s", rapidez=7), bip(2850, 2800, 0.2, "s", rapidez=9) * 0.5)


def sfx_teia_presa():
    n = int(SR * 0.34)
    return passa_baixa(ruido(0.34, 6), 1200) * queda(n, 4) * (0.6 + 0.4 * np.sin(2 * np.pi * 14 * np.arange(n) / SR))

def sfx_tiro_inimigo():
    return bip(540, 250, 0.1, "q", 0.125, 6)


def sfx_teia_tiro():
    chiado = passa_alta(ruido(0.18, 9), 3000) * queda(int(SR * 0.18), 5) * 0.3
    return misturar(bip(1500, 480, 0.16, "s", rapidez=5), chiado)


def sfx_armadura():
    estalo = passa_alta(ruido(0.012, 12), 2000)
    return misturar(bip(1250, 1240, 0.16, "s", rapidez=9), bip(1870, 1850, 0.12, "s", rapidez=10) * 0.6,
                    bip(3100, 3100, 0.07, "s", rapidez=12) * 0.3, estalo)


def sfx_gosma():
    n = int(SR * 0.22)
    t = np.arange(n) / SR
    f = varrer(330, 110, 0.22) * (1 + 0.12 * np.sin(2 * np.pi * 22 * t))
    return misturar(seno(f) * queda(n, 5), passa_baixa(ruido(0.22, 13), 700) * queda(n, 6) * 0.5)


def sfx_invoca():
    n = int(SR * 0.6)
    t = np.arange(n) / SR
    f = varrer(110, 230, 0.6)
    return serra(f) * (0.6 + 0.4 * np.sin(2 * np.pi * 16 * t)) * adsr(n, 0.05, 0.1, 0.8, 0.2)

def sfx_inseto():
    estalo = passa_baixa(ruido(0.12, 14), 2500) * queda(int(SR * 0.12), 8)
    return misturar(estalo, bip(320, 80, 0.2, "q", 0.5, 6) * 0.6)


def sfx_inseto_zigzag():
    n = int(SR * 0.3)
    t = np.arange(n) / SR
    f = varrer(900, 260, 0.3) * (1 + 0.18 * np.sin(2 * np.pi * 18 * t))
    return quadrada(f, 0.125) * queda(n, 4)


def sfx_barata_voadora():
    n = int(SR * 0.32)
    t = np.arange(n) / SR
    zumbido = serra(np.full(n, 150.0)) * (0.55 + 0.45 * np.sin(2 * np.pi * 40 * t)) * queda(n, 3)
    estouro = atrasar(bip(650, 110, 0.07, "q", 0.5, 6), 0.22)
    return misturar(zumbido * 0.7, passa_alta(ruido(0.32, 15), 1500) * queda(n, 5) * 0.3, estouro)


def sfx_formiga():
    batida = misturar(bip(780, 770, 0.1, "s", rapidez=9), bip(1190, 1180, 0.08, "s", rapidez=10) * 0.6)
    surdo = bip(160, 60, 0.15, "t", rapidez=6)
    return misturar(batida, atrasar(batida * 0.8, 0.09), surdo * 0.8)


def sfx_traca():
    n = int(SR * 0.28)
    t = np.arange(n) / SR
    asas = passa_baixa(ruido(0.28, 16), 3000) * (0.45 + 0.55 * np.sin(2 * np.pi * 26 * t) ** 2)
    return misturar(asas * queda(n, 3.5), bip(1100, 700, 0.1, "t", rapidez=7) * 0.25)


def sfx_aranha():
    n = int(SR * 0.34)
    chiado = passa_alta(ruido(0.34, 17), 3500) * queda(n, 3.5)
    return misturar(chiado * 0.7, bip(2300, 900, 0.3, "s", rapidez=4) * 0.5)


def sfx_mosquito():
    n = int(SR * 0.32)
    t = np.arange(n) / SR
    f = varrer(3300, 1700, 0.32) + 220 * np.sin(2 * np.pi * 32 * t)
    return misturar(seno(f) * queda(n, 3.5), atrasar(bip(900, 150, 0.06, "q", 0.5, 7), 0.26))


def sfx_mosca():
    n = int(SR * 0.36)
    t = np.arange(n) / SR
    f = 175 * (1 + 0.08 * np.sin(2 * np.pi * 45 * t))
    zumbido = serra(f) * (0.6 + 0.4 * np.sin(2 * np.pi * 38 * t)) * queda(n, 3)
    return misturar(zumbido * 0.7, atrasar(passa_baixa(ruido(0.12, 18), 900) * queda(int(SR * 0.12), 6), 0.24) * 0.7)


def sfx_pulga():
    return misturar(bip(2700, 2300, 0.03, "q", 0.25, 6), atrasar(bip(2400, 2000, 0.03, "q", 0.25, 6), 0.06),
                    atrasar(bip(900, 300, 0.05, "q", 0.5, 8), 0.12) * 0.6)


def sfx_lesma():
    n = int(SR * 0.42)
    t = np.arange(n) / SR
    f = varrer(240, 55, 0.42) * (1 + 0.1 * np.sin(2 * np.pi * 14 * t))
    molhado = passa_baixa(ruido(0.42, 19), 800) * (0.5 + 0.5 * np.sin(2 * np.pi * 9 * t) ** 2)
    return misturar(seno(f) * queda(n, 3), molhado * queda(n, 3.5) * 0.7)


def sfx_rainha_hit():
    n = int(SR * 0.17)
    return misturar(serra(varrer(100, 70, 0.17)) * queda(n, 5), passa_baixa(ruido(0.17, 20), 1500) * queda(n, 6) * 0.4)


def sfx_rainha_entrada():
    dur = 1.5
    n = int(SR * dur)
    t = np.arange(n) / SR
    contorno = np.interp(t, [0, 0.5, 1.1, dur], [70, 118, 100, 55])
    f = contorno * (1 + 0.04 * np.sin(2 * np.pi * 9 * t))
    corpo = serra(f) * (0.65 + 0.35 * np.sin(2 * np.pi * 20 * t))
    rosnado = passa_baixa(ruido(dur, 21), 900) * 0.5
    return (corpo * 0.8 + rosnado) * adsr(n, 0.08, 0.2, 0.85, 0.5)


def sfx_rainha_morte():
    dur = 2.0
    n = int(SR * dur)
    t = np.arange(n) / SR
    f = np.interp(t, [0, 0.4, dur], [140, 120, 35]) * (1 + 0.05 * np.sin(2 * np.pi * 11 * t))
    corpo = serra(f) * (0.6 + 0.4 * np.sin(2 * np.pi * 24 * t))
    estalos = passa_alta(ruido(dur, 22), 1500) * (np.random.RandomState(23).uniform(0, 1, n) > 0.985) * 1.2
    gemido = triangulo(np.interp(t, [0, dur], [700, 150])) * 0.25 * np.exp(-t * 1.2)
    return (corpo * 0.7 + estalos + gemido) * adsr(n, 0.01, 0.2, 0.8, 0.9)


def sfx_morte_mimi():
    dur = 0.95
    n = int(SR * dur)
    t = np.arange(n) / SR
    contorno = np.interp(t, [0, 0.18, 0.45, 0.75, dur], [520, 980, 780, 460, 260])
    f = contorno * (1 + 0.025 * np.sin(2 * np.pi * 7 * t))
    voz = 0.7 * triangulo(f) + 0.2 * quadrada(f * 2, 0.3) + 0.2 * seno(f * 3)
    return voz * adsr(n, 0.03, 0.15, 0.8, 0.35)


def sfx_morte_robo():
    dur = 1.15
    n = int(SR * dur)
    t = np.arange(n) / SR
    f = varrer(900, 45, dur)
    corpo = crush(quadrada(f, 0.25), 6) * np.exp(-1.2 * t / dur)
    estalos = (np.random.RandomState(24).uniform(0, 1, n) > 0.994) * np.random.RandomState(25).uniform(-1, 1, n)
    final = atrasar(bip(110, 40, 0.18, "s", rapidez=5), dur - 0.15)
    return misturar(corpo * 0.8, estalos * 0.5 * np.exp(-1.5 * t / dur), final)


def sfx_fase_inicio():
    return notas([(392, 0.11), (523, 0.11), (659, 0.34)], "q", 0.25, 2.5)


def sfx_fase_concluida():
    return notas([(523, 0.09), (659, 0.09), (784, 0.09), (1047, 0.09), (1319, 0.4)], "q", 0.25, 2.0)


def sfx_gameover():
    queda_triste = notas([(330, 0.4), (294, 0.4), (262, 0.4), (247, 0.9)], "t", rapidez=2.2)
    return misturar(queda_triste, atrasar(bip(82, 55, 0.9, "t", rapidez=2.5), 1.0) * 0.4)


def sfx_vitoria():
    subida = notas([(392, 0.1), (523, 0.1), (659, 0.1), (784, 0.1), (1047, 0.1), (784, 0.1), (1047, 0.34)], "q", 0.25, 2.0)
    n = int(SR * 1.6)
    t = np.arange(n) / SR
    acorde = sum(triangulo(np.full(n, hz(m))) for m in (72, 76, 79, 84)) * 0.28
    acorde = acorde * (0.8 + 0.2 * np.sin(2 * np.pi * 8 * t)) * adsr(n, 0.02, 0.2, 0.8, 0.5)
    baixo = quadrada(np.full(n, hz(48)), 0.5) * 0.25 * adsr(n, 0.02, 0.2, 0.8, 0.5)
    final = misturar(acorde, baixo)
    return emendar(subida, final)

def sfx_cena_fedor():
    dur = 2.6
    n = int(SR * dur)
    t = np.arange(n) / SR
    ronco = (seno(np.full(n, 52.0)) * 0.6 + passa_baixa(ruido(dur, 30), 220) * 0.9) * (0.6 + 0.4 * np.sin(2 * np.pi * 3 * t))
    rng = np.random.RandomState(31)
    bolhas = np.zeros(n)
    for i in range(16):
        ini = int(rng.uniform(0.2, 2.2) * SR)
        f = rng.uniform(180, 520)
        b = bip(f, f * 2.0, 0.09, "s", rapidez=5)
        bolhas[ini:ini + len(b)] += b * 0.7
    arroto = atrasar(serra(varrer(125, 55, 0.4)) * queda(int(SR * 0.4), 3), 1.2)
    return misturar(ronco * adsr(n, 0.2, 0.3, 0.8, 0.6) * 0.8, bolhas, arroto * 0.6)


def sfx_cena_pragas():
    dur = 2.6
    n = int(SR * dur)
    t = np.arange(n) / SR
    rng = np.random.RandomState(32)
    saida = np.zeros(n)
    for i in range(70):
        ini = int((rng.uniform(0, 1) ** 0.7) * (dur - 0.1) * SR)
        passo = passa_alta(ruido(0.025, 40 + i), 2500) * queda(int(SR * 0.025), 6)
        saida[ini:ini + len(passo)] += passo * rng.uniform(0.3, 1.0)
    zumbido = serra(np.full(n, 185.0) * (1 + 0.03 * np.sin(2 * np.pi * 5 * t))) * (0.6 + 0.4 * np.sin(2 * np.pi * 36 * t))
    zumbido *= np.clip(t / 1.5, 0, 1) * 0.35
    guinchos = misturar(*[atrasar(bip(2400, 3100, 0.07, "s", rapidez=6), s) for s in (0.5, 1.1, 1.8)]) * 0.3
    return misturar(saida * 1.2, zumbido, guinchos) * adsr(n, 0.05, 0.2, 0.9, 0.5)


def sfx_cena_herois():
    arpejo = notas([(523, 0.1), (659, 0.1), (784, 0.1), (1047, 0.5)], "q", 0.25, 2.0)
    miau = atrasar(miau_alegre(), 0.35)
    bipes = atrasar(notas([(1200, 0.07), (1600, 0.1)], "q", 0.5, 4), 0.85)
    brilho = atrasar(passa_alta(ruido(0.5, 33), 5000) * queda(int(SR * 0.5), 4) * 0.12, 0.1)
    return misturar(arpejo, miau * 0.8, bipes * 0.6, brilho)


def miau_alegre():
    dur = 0.5
    n = int(SR * dur)
    t = np.arange(n) / SR
    contorno = np.interp(t, [0, 0.12, 0.3, dur], [600, 1100, 900, 700])
    f = contorno * (1 + 0.015 * np.sin(2 * np.pi * 7 * t))
    return (0.7 * triangulo(f) + 0.2 * quadrada(f * 2, 0.3)) * adsr(n, 0.02, 0.1, 0.8, 0.15)


EFEITOS = {
    "click": sfx_click, "tecla": sfx_tecla, "digita": sfx_digita, "compra": sfx_compra, "erro": sfx_erro,
    "tiro_mimi": sfx_tiro_mimi, "tiro_robo": sfx_tiro_robo, "dash": sfx_dash, "espuma": sfx_espuma,
    "moeda": sfx_moeda, "vida": sfx_vida, "powerup": sfx_powerup, "dano": sfx_dano, "escudo": sfx_escudo,
    "teia_presa": sfx_teia_presa,
    "tiro_inimigo": sfx_tiro_inimigo, "teia_tiro": sfx_teia_tiro, "armadura": sfx_armadura, "gosma": sfx_gosma,
    "invoca": sfx_invoca,
    "inseto": sfx_inseto, "inseto_reto": sfx_inseto, "inseto_zigzag": sfx_inseto_zigzag,
    "barata_voadora": sfx_barata_voadora, "formiga": sfx_formiga, "traca": sfx_traca, "aranha": sfx_aranha,
    "mosquito": sfx_mosquito, "mosca": sfx_mosca, "pulga": sfx_pulga, "lesma": sfx_lesma,
    "rainha_hit": sfx_rainha_hit, "rainha_entrada": sfx_rainha_entrada, "rainha_morte": sfx_rainha_morte,
    "morte_mimi": sfx_morte_mimi, "morte_robo": sfx_morte_robo,
    "fase_inicio": sfx_fase_inicio, "fase_concluida": sfx_fase_concluida, "gameover": sfx_gameover,
    "vitoria": sfx_vitoria,
    "cena_fedor": sfx_cena_fedor, "cena_pragas": sfx_cena_pragas, "cena_herois": sfx_cena_herois,
}

# volume final de cada efeito (1.0 = pico de 0.9). Os sons que tocam o tempo todo ficam mais baixinhos.
GANHO = {
    "tecla": 0.3, "digita": 0.28, "click": 0.7, "tiro_mimi": 0.55, "tiro_robo": 0.55, "tiro_inimigo": 0.45,
    "teia_tiro": 0.5, "dash": 0.7, "inseto": 0.7, "inseto_reto": 0.7, "inseto_zigzag": 0.7,
    "barata_voadora": 0.7, "formiga": 0.75, "traca": 0.65, "aranha": 0.65, "mosquito": 0.6, "mosca": 0.65,
    "pulga": 0.55, "lesma": 0.75, "armadura": 0.6, "gosma": 0.6, "moeda": 0.6, "dano": 0.85,
    "rainha_hit": 0.7,
}

def instrumento(inst, midi, dur):
    n = max(int(SR * dur), 1)
    f = np.full(n, hz(midi))
    t = np.arange(n) / SR
    if inst == "lead":
        onda = quadrada(f * (1 + 0.006 * np.sin(2 * np.pi * 5.5 * t) * np.clip(t / 0.2, 0, 1)), 0.25)
        env = adsr(n, 0.005, 0.08, 0.6, 0.06)
    elif inst == "doce":
        onda = triangulo(f * (1 + 0.004 * np.sin(2 * np.pi * 5 * t)))
        env = adsr(n, 0.01, 0.1, 0.75, 0.08)
    elif inst == "baixo":
        onda = 0.6 * quadrada(f, 0.5) + 0.5 * triangulo(f)
        env = adsr(n, 0.003, 0.05, 0.7, 0.03)
    elif inst == "arp":
        onda = triangulo(f)
        env = adsr(n, 0.003, 0.1, 0.3, 0.05)
    elif inst == "pad":
        onda = 0.5 * triangulo(f) + 0.3 * quadrada(f * 1.004, 0.5)
        env = adsr(n, 0.06, 0.1, 0.7, 0.2)
    elif inst == "stab":
        onda = serra(f)
        env = adsr(n, 0.003, 0.06, 0.45, 0.05)
    else:
        raise ValueError(inst)
    return onda * env


def bumbo():
    n = int(SR * 0.16)
    return seno(varrer(160, 42, 0.16)) * queda(n, 5, 0.001) * 1.1


def caixa():
    n = int(SR * 0.13)
    return (passa_alta(ruido(0.13, 50), 900) * 0.8 + seno(np.full(n, 190.0)) * 0.5) * queda(n, 7, 0.001)


def chimbal(aberto=False):
    n = int(SR * (0.12 if aberto else 0.04))
    return passa_alta(ruido(n / SR, 51), 6000) * queda(n, 5 if aberto else 9, 0.001) * 0.5


class Faixa:
    def __init__(self, bpm, compassos):
        self.spb = 60.0 / bpm
        self.n = int(round(compassos * 4 * self.spb * SR))
        self.buf = np.zeros(self.n + SR * 2)

    def poe(self, x, beat, vol):
        i = int(round(beat * self.spb * SR))
        self.buf[i:i + len(x)] += x[:len(self.buf) - i] * vol

    def nota(self, inst, midi, beat, dur_beats, vol=1.0):
        self.poe(instrumento(inst, midi, dur_beats * self.spb), beat, vol)

    def batida(self, tipo, beat, vol=1.0):
        som = {"bumbo": bumbo, "caixa": caixa, "chimbal": chimbal, "chimbal_a": lambda: chimbal(True)}[tipo]()
        self.poe(som, beat, vol)

    def renderizar(self):
        saida = self.buf[:self.n].copy()
        resto = self.buf[self.n:]
        saida[:len(resto)] += resto          # a "cauda" volta pro começo: loop sem emenda
        return saida


def tema_menu():
    f = Faixa(96, 12)
    acordes = [(48, (60, 64, 67)), (45, (57, 60, 64)), (41, (53, 57, 60)), (43, (55, 59, 62))]
    melodia = [
        [(76, 1), (74, .5), (72, .5), (67, 1), (69, 1)], [(72, 1.5), (69, .5), (67, 2)],
        [(69, 1), (72, 1), (76, 1), (72, 1)], [(74, 1.5), (72, .5), (67, 2)],
        [(76, 1), (79, .5), (76, .5), (74, 1), (72, 1)], [(74, 1.5), (72, .5), (69, 2)],
        [(72, 1), (74, 1), (76, 1), (79, 1)], [(76, 3), (0, 1)],
        [(79, 1), (76, .5), (74, .5), (72, 1), (74, 1)], [(76, 1.5), (74, .5), (69, 2)],
        [(72, 1), (69, 1), (67, 1), (69, 1)], [(72, 3), (0, 1)],
    ]
    for c in range(12):
        raiz, acorde = acordes[c % 4]
        b = c * 4
        f.nota("baixo", raiz, b, 1.8, 0.8)
        f.nota("baixo", raiz + 7, b + 2, 1.8, 0.7)
        for i in range(8):
            f.nota("arp", acorde[i % 3] + (12 if i % 3 == 2 else 0), b + i * 0.5, 0.45, 0.32)
        pos = b
        for nota, dur in melodia[c]:
            if nota:
                f.nota("doce", nota, pos, dur * 0.95, 0.75)
            pos += dur
    return f.renderizar()


def tema_jogo():
    f = Faixa(138, 16)
    prog = [(45, 57, 60, 64), (41, 53, 57, 60), (48, 60, 64, 67), (43, 55, 59, 62)]
    riffs = [
        [(81, .5), (0, .5), (81, .5), (79, .5), (76, 1), (72, 1)],
        [(74, .5), (76, .5), (72, 1), (69, 1), (72, 1)],
        [(79, .5), (0, .5), (79, .5), (76, .5), (72, 1), (76, 1)],
        [(74, 1), (76, .5), (74, .5), (71, 1), (67, 1)],
    ]
    for c in range(16):
        raiz, a, b_, c_ = prog[c % 4]
        b = c * 4
        for i in range(8):
            f.nota("baixo", raiz if i % 4 != 3 else raiz + 12, b + i * 0.5, 0.4, 0.75)
        f.batida("bumbo", b, 1.0)
        f.batida("bumbo", b + 2, 1.0)
        f.batida("caixa", b + 1, 0.8)
        f.batida("caixa", b + 3, 0.8)
        for i in range(8):
            f.batida("chimbal", b + i * 0.5, 0.6)
        if c >= 4:
            pos = b
            for nota, dur in riffs[c % 4]:
                if nota:
                    f.nota("lead", nota + (12 if c >= 12 and c % 2 == 0 else 0), pos, dur * 0.9, 0.55)
                pos += dur
        if c % 4 == 0 or c % 4 == 2:
            for k, m in enumerate((a, b_, c_)):
                f.nota("pad", m, b, 3.8, 0.17)
    return f.renderizar()


def tema_chefe():
    f = Faixa(156, 16)
    raiz = 38
    motivos = [
        [(74, 1), (75, .5), (74, .5), (69, 1), (0, 1)],
        [(74, .5), (75, .5), (77, 1), (75, 1), (74, 1)],
        [(81, 1), (80, .5), (77, .5), (75, 1), (74, 1)],
        [(74, 1.5), (75, .5), (69, 2)],
    ]
    for c in range(16):
        b = c * 4
        grave = raiz if (c % 4) != 3 else raiz + 1
        for i in range(8):
            f.nota("baixo", grave if i % 2 == 0 else grave + 12, b + i * 0.5, 0.42, 0.85)
        for i in range(4):
            f.batida("bumbo", b + i, 1.0)
        f.batida("caixa", b + 1, 0.85)
        f.batida("caixa", b + 3, 0.85)
        for i in range(16):
            f.batida("chimbal", b + i * 0.25, 0.4)
        if c % 2 == 1:
            f.nota("stab", raiz + 24, b + 2.5, 0.4, 0.28)
            f.nota("stab", raiz + 30, b + 2.5, 0.4, 0.22)
        if c >= 2:
            pos = b
            for nota, dur in motivos[c % 4]:
                if nota:
                    f.nota("lead", nota, pos, dur * 0.9, 0.5)
                pos += dur
    return f.renderizar()


MUSICAS = {"tema_menu": tema_menu, "tema_jogo": tema_jogo, "tema_chefe": tema_chefe}

def salvar_wav(nome, x, pico=0.9, ganho=1.0):
    x = np.nan_to_num(x)
    maior = np.max(np.abs(x))
    if maior > 0:
        x = x * (pico / maior)
    x = x * ganho
    fade = min(int(SR * 0.004), len(x) // 4)
    if fade > 0:
        x[:fade] *= np.linspace(0, 1, fade)
        x[-fade:] *= np.linspace(1, 0, fade)
    dados = (np.clip(x, -1, 1) * 32767).astype("<i2")
    with wave.open(os.path.join(PASTA, nome + ".wav"), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(dados.tobytes())
    return len(x) / SR


if __name__ == "__main__":
    for nome, funcao in EFEITOS.items():
        dur = salvar_wav(nome, funcao(), 0.9, GANHO.get(nome, 1.0))
        print(f"efeito  {nome:16s} {dur:5.2f}s")
    for nome, funcao in MUSICAS.items():
        dur = salvar_wav(nome, funcao(), 0.85)
        print(f"musica  {nome:16s} {dur:5.2f}s")
    print(f"\n{len(EFEITOS)} efeitos e {len(MUSICAS)} musicas em {PASTA}/")
