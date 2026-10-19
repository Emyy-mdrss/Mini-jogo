
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import math
import random

import pygame

pygame.init()
pygame.display.set_mode((1, 1))

PASTA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sprites")
os.makedirs(PASTA, exist_ok=True)

CONTORNO = (28, 18, 16)


class Grade:

    def __init__(self, largura, altura=None):
        self.w = largura
        self.h = altura or largura
        self.px = {}

    def _poe(self, x, y, cor):
        if 0 <= x < self.w and 0 <= y < self.h:
            self.px[(x, y)] = cor

    def set(self, x, y, cor, espelho=True):
        self._poe(x, y, cor)
        if espelho:
            self._poe(self.w - 1 - x, y, cor)

    def rect(self, x0, y0, x1, y1, cor, espelho=True):
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                self.set(x, y, cor, espelho)

    def linha(self, x0, y0, x1, y1, cor, espelho=True):
        dx, dy = abs(x1 - x0), abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        erro = dx - dy
        while True:
            self.set(x0, y0, cor, espelho)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * erro
            if e2 > -dy:
                erro -= dy
                x0 += sx
            if e2 < dx:
                erro += dx
                y0 += sy

    def caminho(self, pontos, cor, espelho=True):
        for (a, b) in zip(pontos, pontos[1:]):
            self.linha(a[0], a[1], b[0], b[1], cor, espelho)

    def ascii(self, linhas, paleta, x0=0, y0=0):
        for j, linha in enumerate(linhas):
            for i, ch in enumerate(linha):
                if ch in paleta:
                    self._poe(x0 + i, y0 + j, paleta[ch])

    def contorno(self, cor=CONTORNO):
        novos = {}
        for (x, y) in self.px:
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                p = (x + dx, y + dy)
                if p not in self.px and 0 <= p[0] < self.w and 0 <= p[1] < self.h:
                    novos[p] = cor
        self.px.update(novos)
        return self

    def inverter_v(self):
        self.px = {(x, self.h - 1 - y): c for (x, y), c in self.px.items()}
        return self

    def render(self, unidade):
        s = pygame.Surface((self.w * unidade, self.h * unidade), pygame.SRCALPHA)
        for (x, y), cor in self.px.items():
            pygame.draw.rect(s, cor, (x * unidade, y * unidade, unidade, unidade))
        return s


def salvar(superficie, nome):
    pygame.image.save(superficie, os.path.join(PASTA, nome))
    print(f"gerado: {nome} {superficie.get_size()}")

def gerar_mimi():
    g = Grade(24)
    dk, br, lt = (74, 58, 50), (130, 104, 88), (104, 82, 70)
    cr, pk, olho = (216, 198, 180), (226, 150, 186), (30, 24, 26)
    rox, rox_e, ouro = (176, 66, 210), (118, 36, 150), (250, 205, 70)

    # orelhas
    for y, xs in ((1, [6]), (2, [6, 7]), (3, [6, 7, 8]), (4, [6, 7, 8, 9])):
        for x in xs:
            g.set(x, y, br)
    g.set(7, 3, cr)
    g.set(7, 4, cr)
    g.set(8, 4, lt)
    # cabeça
    g.rect(5, 5, 11, 13, br)
    g.rect(5, 5, 5, 8, lt)
    g.rect(8, 5, 8, 6, dk)        
    g.rect(10, 5, 10, 7, dk)
    g.rect(6, 7, 7, 7, lt)
    g.rect(11, 5, 11, 10, cr, True)  
    g.rect(9, 10, 11, 13, cr)
    g.rect(7, 8, 7, 10, olho)     
    g.set(11, 11, pk)               
    g.set(11, 12, lt)
    g.linha(4, 10, 1, 9, dk)
    g.linha(4, 12, 1, 13, dk)
    g.rect(7, 14, 11, 15, rox)
    g.rect(7, 15, 11, 15, rox_e)
    g.set(11, 16, ouro)
    # corpo e patas
    g.rect(7, 16, 11, 21, br)
    g.rect(10, 17, 11, 20, cr)
    g.rect(7, 17, 7, 20, lt)
    g.rect(7, 21, 9, 22, br)
    g.rect(7, 22, 9, 22, cr)
    # rabo (só do lado direito)
    g.rect(17, 15, 18, 20, br, espelho=False)
    g.rect(18, 13, 19, 15, br, espelho=False)
    g.set(19, 13, dk, espelho=False)
    return g.contorno().render(2)


def gerar_robo():
    g = Grade(24)
    br, sh = (224, 236, 240), (160, 182, 196)
    esc, tela = (44, 52, 70), (152, 202, 228)
    tela_e, olho = (96, 148, 184), (40, 58, 96)
    rosa, verm, lar = (238, 146, 156), (226, 70, 70), (252, 190, 130)

    g.rect(9, 2, 9, 4, esc, espelho=False)
    g.set(9, 1, lar, espelho=False)
    g.rect(14, 3, 14, 4, esc, espelho=False)
    g.set(14, 2, verm, espelho=False)
    g.rect(4, 5, 11, 13, br)
    g.rect(4, 5, 5, 13, sh, espelho=False)
    g.rect(4, 13, 11, 13, sh)
    g.rect(6, 6, 11, 12, tela)
    g.rect(6, 12, 11, 12, tela_e)
    g.rect(8, 8, 8, 10, olho)
    g.set(7, 11, rosa)
    g.set(11, 10, olho)
  
    g.rect(10, 14, 11, 14, esc)
    g.rect(7, 15, 11, 20, br)
    g.rect(7, 15, 7, 20, sh, espelho=False)
    g.rect(8, 19, 11, 19, sh)
    g.set(14, 17, verm, espelho=False)
    g.rect(4, 16, 5, 18, br)
    g.rect(3, 18, 5, 19, sh)
    g.rect(8, 21, 9, 22, br)
    g.rect(7, 22, 9, 22, sh)
    return g.contorno().render(2)

def barata(pal, asas=None):
    g = Grade(24)
    # pernas
    g.caminho([(6, 12), (3, 11), (2, 8)], pal["perna"])
    g.caminho([(6, 15), (2, 15), (1, 17)], pal["perna"])
    g.caminho([(6, 18), (3, 19), (2, 22)], pal["perna"])
    if asas:
        g.rect(3, 11, 5, 19, asas[0])
        g.rect(4, 10, 5, 10, asas[0])
        g.rect(3, 13, 3, 17, asas[1])
        g.rect(4, 12, 4, 12, asas[2])
    # corpo
    g.rect(8, 9, 11, 11, pal["corpo"])
    g.rect(6, 12, 11, 19, pal["corpo"])
    g.rect(7, 20, 11, 21, pal["corpo"])
    g.rect(9, 22, 11, 22, pal["corpo"])
    g.rect(6, 12, 6, 19, pal["sombra"])
    for y in (14, 16, 18):
        g.rect(7, y, 11, y, pal["sombra"])
    g.rect(9, 10, 10, 10, pal["brilho"])
    g.rect(9, 13, 10, 13, pal["brilho"])
    g.rect(9, 15, 10, 15, pal["brilho"])
    # cabeça
    g.rect(9, 5, 11, 8, pal["cabeca"])
    g.rect(9, 6, 10, 6, (122, 116, 124))
    g.rect(9, 7, 10, 7, (24, 22, 26))
    # antenas
    g.caminho([(10, 5), (6, 1), (4, 3)], pal["antena"])
    return g


def finalizar_inseto(g, unidade=2):
    return g.inverter_v().contorno().render(unidade)


PAL_RETO = dict(corpo=(184, 60, 44), sombra=(122, 34, 28), brilho=(230, 118, 92),
                perna=(214, 112, 60), cabeca=(112, 36, 30), antena=(64, 26, 20))
PAL_ZIGZAG = dict(corpo=(142, 64, 184), sombra=(90, 34, 128), brilho=(196, 134, 230),
                  perna=(200, 124, 220), cabeca=(78, 32, 108), antena=(52, 22, 72))
PAL_VOADORA = dict(corpo=(128, 68, 18), sombra=(86, 42, 10), brilho=(176, 104, 38),
                   perna=(192, 108, 20), cabeca=(72, 36, 10), antena=(56, 30, 12))


def gerar_inseto_reto():
    return finalizar_inseto(barata(PAL_RETO))


def gerar_inseto_zigzag():
    # roxa e com um risquinho claro nas asas fechadas, pra lembrar que ela zigue-zagueia
    g = barata(PAL_ZIGZAG)
    g.rect(8, 13, 8, 19, (210, 160, 240))
    return finalizar_inseto(g)


def gerar_barata_voadora():
    asas = ((150, 226, 246), (86, 178, 218), (214, 248, 255))
    return finalizar_inseto(barata(PAL_VOADORA, asas=asas))


def gerar_formiga():
    g = Grade(24)
    corpo, sombra, brilho = (122, 56, 38), (76, 30, 22), (176, 100, 74)
    aco, aco_b, perna, cabeca = (142, 152, 168), (196, 206, 220), (62, 28, 20), (104, 46, 32)

    # pernas finas e angulosas, como na referência
    g.caminho([(10, 9), (6, 7), (4, 4)], perna)
    g.caminho([(10, 10), (5, 11), (3, 15)], perna)
    g.caminho([(10, 11), (6, 15), (4, 21)], perna)
    # corpo em 3 partes
    g.rect(10, 8, 11, 11, corpo)
    g.rect(8, 12, 11, 20, corpo)
    g.rect(9, 21, 11, 22, corpo)
    g.rect(8, 12, 8, 20, sombra)
    g.rect(9, 13, 10, 13, brilho)
    # armadura de aço (a "blindada")
    for y in (15, 18):
        g.rect(8, y, 11, y, aco)
        g.rect(9, y, 10, y, aco_b)
    g.rect(9, 21, 11, 21, aco)
    # cabeça com capacete
    g.rect(9, 4, 11, 7, cabeca)
    g.rect(9, 4, 11, 4, aco)
    g.rect(10, 4, 10, 4, aco_b)
    g.set(9, 6, (230, 210, 120))
    g.set(8, 8, perna)
    # antenas com cotovelo
    g.caminho([(10, 3), (7, 1), (4, 2)], perna)
    return finalizar_inseto(g)


def gerar_traca():
    g = Grade(24)
    asa, padrao, borda = (216, 192, 142), (168, 134, 90), (116, 88, 56)
    claro, corpo, corpo_s = (240, 222, 180), (172, 146, 104), (122, 98, 68)
    olho_e, olho_i = (96, 60, 44), (246, 226, 150)

    # asas de cima (grandes) e de baixo (menores), com um recorte no meio
    g.rect(4, 5, 10, 5, borda)
    g.rect(3, 6, 10, 12, asa)
    g.rect(2, 7, 2, 11, borda)
    g.rect(3, 6, 3, 12, borda)
    g.rect(4, 5, 10, 5, borda)
    g.rect(5, 13, 10, 18, asa)
    g.rect(5, 18, 10, 18, borda)
    g.rect(4, 14, 4, 17, borda)
    g.rect(5, 19, 9, 19, borda)
    g.rect(9, 6, 9, 17, claro)
    # desenhos nas asas (olhinhos de mariposa)
    g.rect(5, 8, 7, 10, olho_e)
    g.rect(6, 9, 6, 9, olho_i)
    g.rect(6, 15, 7, 16, padrao)
    g.rect(4, 6, 4, 6, padrao)
    # corpinho peludo
    g.rect(10, 5, 11, 18, corpo)
    g.rect(10, 8, 10, 9, corpo_s)
    g.rect(10, 12, 10, 14, corpo_s)
    g.rect(10, 19, 11, 20, corpo_s)
    # cabeça e antenas penadas
    g.rect(10, 2, 11, 4, corpo_s)
    g.set(10, 3, (30, 24, 20))
    g.caminho([(10, 2), (7, 0)], borda)
    g.set(8, 1, borda)
    g.set(7, 2, borda)
    g.set(9, 0, borda)
    return finalizar_inseto(g)


def gerar_aranha():
    # a aranha fica pendurada no fio, então não inverte
    g = Grade(24)
    corpo, brilho = (34, 34, 42), (74, 74, 90)
    perna, fio, verm = (20, 20, 26), (206, 206, 216), (220, 40, 44)

    g.rect(11, 0, 11, 6, fio)
    g.caminho([(9, 9), (6, 5), (3, 8), (3, 13)], perna)
    g.caminho([(9, 10), (5, 7), (2, 11), (2, 16)], perna)
    g.caminho([(9, 12), (6, 14), (4, 17), (4, 21)], perna)
    g.caminho([(10, 14), (7, 17), (7, 22)], perna)
    g.rect(9, 7, 11, 13, corpo)
    g.rect(10, 14, 11, 17, corpo)
    g.rect(9, 8, 9, 9, brilho)
    g.rect(11, 9, 11, 10, verm)       # ampulheta vermelha
    g.set(11, 12, verm)
    g.set(10, 16, verm)               # olhinhos
    return g.contorno().render(2)


def gerar_mosquito():
    g = Grade(24)
    corpo, sombra, claro = (178, 90, 32), (124, 58, 16), (244, 170, 60)
    asa, asa_c, asa_e = (96, 218, 238), (196, 246, 255), (62, 164, 204)
    perna, ferrao = (110, 54, 16), (60, 32, 14)

    # asas grandes em ângulo, no estilo da referência azul
    g.rect(2, 7, 9, 9, asa)
    g.rect(1, 8, 2, 9, asa)
    g.rect(3, 10, 9, 11, asa_e)
    g.rect(4, 7, 7, 7, asa_c)
    g.rect(3, 8, 5, 8, asa_c)
    # pernas compridas
    g.caminho([(10, 11), (6, 13), (5, 19)], perna)
    g.caminho([(10, 13), (5, 15), (3, 21)], perna)
    g.caminho([(10, 15), (7, 18), (7, 22)], perna)
    # corpo fino
    g.rect(10, 5, 11, 6, corpo)
    g.rect(10, 7, 11, 11, corpo)
    g.rect(11, 12, 11, 20, corpo)
    for y in (13, 15, 17, 19):
        g.set(11, y, sombra)
    g.set(10, 8, claro)
    g.set(10, 10, claro)
    g.set(10, 6, (126, 214, 72))      # olho verde
    # ferrão comprido na frente
    g.rect(11, 0, 11, 4, ferrao)
    g.caminho([(10, 5), (8, 2)], perna)
    return finalizar_inseto(g)


def gerar_mosca():
    g = Grade(24)
    corpo, sombra, brilho = (46, 116, 98), (26, 78, 72), (130, 214, 176)
    asa, asa_c, olho = (210, 232, 244), (244, 252, 255), (210, 52, 56)
    perna = (30, 52, 46)

    g.rect(2, 8, 8, 16, asa)
    for (x, y) in ((2, 8), (2, 16)):
        g.px.pop((x, y), None)
        g.px.pop((g.w - 1 - x, y), None)
    g.rect(4, 9, 6, 10, asa_c)
    g.rect(3, 12, 3, 14, (160, 190, 210))
    g.caminho([(8, 11), (5, 13), (4, 16)], perna)
    g.caminho([(8, 13), (4, 16), (3, 19)], perna)
    # corpo redondo e brilhante
    g.rect(8, 8, 11, 13, corpo)
    g.rect(8, 14, 11, 19, sombra)
    g.rect(9, 20, 11, 21, sombra)
    g.rect(9, 9, 10, 10, brilho)
    g.rect(9, 15, 10, 16, corpo)
    # cabeça com olhos enormes
    g.rect(9, 4, 11, 7, (30, 40, 38))
    g.rect(7, 4, 8, 7, olho)
    g.set(7, 5, (255, 170, 170))
    g.rect(11, 2, 11, 3, perna)
    return finalizar_inseto(g)


def gerar_pulga():
    g = Grade(12)
    corpo, sombra, brilho, perna = (136, 56, 36), (84, 32, 22), (200, 110, 78), (48, 20, 14)
    # três pares de perninhas, as de trás mais longas (é a perna de pular)
    g.caminho([(4, 4), (2, 3), (1, 5)], perna)
    g.caminho([(4, 6), (1, 7), (1, 10)], perna)
    g.caminho([(4, 8), (2, 10), (2, 11)], perna)
    # corpinho em gota
    g.rect(4, 3, 5, 9, corpo)
    g.rect(5, 2, 5, 2, corpo)
    g.rect(4, 8, 4, 9, sombra, espelho=False)
    g.rect(5, 4, 5, 5, brilho)
    g.rect(4, 7, 5, 7, sombra)
    # cabeça e antenas
    g.rect(4, 0, 5, 1, sombra)
    g.set(4, 1, (250, 236, 220))
    g.caminho([(4, 0), (3, 0)], perna)
    return finalizar_inseto(g, 2)


def gerar_lesma():
    g = Grade(24)
    corpo, sombra, brilho = (142, 186, 76), (86, 128, 46), (214, 240, 150)
    barriga, haste = (192, 218, 124), (108, 148, 56)
    branco, pupila = (240, 244, 222), (24, 22, 20)

    g.rect(8, 7, 11, 12, corpo)          # cabeça
    g.rect(6, 13, 11, 19, corpo)         # corpo gordinho
    g.rect(7, 20, 11, 21, corpo)         # cauda afinando
    g.rect(9, 22, 11, 22, corpo)
    g.rect(6, 13, 6, 19, sombra)
    g.rect(7, 20, 7, 21, sombra)
    g.rect(9, 14, 11, 19, barriga)
    g.rect(8, 9, 8, 11, brilho)
    g.rect(7, 15, 7, 17, brilho)
    # hastes com olhos grandes
    g.caminho([(8, 7), (6, 4), (5, 2)], haste)
    g.rect(3, 0, 5, 2, branco)
    g.rect(4, 1, 4, 1, pupila)
    g.set(9, 9, pupila)
    # lodinho no fim do corpo
    g.set(8, 22, brilho)
    return finalizar_inseto(g)


def gerar_rainha_barata():
    pal = dict(corpo=(172, 36, 38), sombra=(112, 22, 26), brilho=(228, 100, 84),
               perna=(218, 150, 60), cabeca=(104, 18, 22), antena=(72, 14, 16))
    asas = ((232, 150, 160), (186, 96, 112), (252, 206, 210))
    ouro, ouro_s, joia = (250, 208, 62), (196, 144, 24), (110, 220, 240)

    g = barata(pal, asas=asas)
    g.inverter_v()
    # coroa dourada em cima da cabeça (a cabeça agora está embaixo)
    g.rect(8, 13, 11, 13, ouro)
    g.rect(8, 14, 11, 14, ouro_s)
    for (x, y) in ((8, 12), (8, 11), (10, 12), (10, 11), (11, 12), (11, 11), (11, 10), (11, 9)):
        g.set(x, y, ouro)
    g.set(11, 13, joia)
    g.set(8, 13, (232, 70, 80))
    return g.contorno().render(5)


# ---------------------------------------------------------------------------
# projéteis e perigos
# ---------------------------------------------------------------------------

def gerar_tiro():
    g = Grade(4, 10)
    g.ascii([".yy.", "yhhy", "yhhy", "yhhy", "yhhy", "yhhy", "yhhy", "yhhy", "yyyy", ".yy."],
            {"y": (255, 214, 44), "h": (255, 250, 196)})
    return g.render(2)


def gerar_tiro_teleguiado():
    g = Grade(4, 10)
    g.ascii([".pp.", "phhp", "phhp", "phhp", "phhp", "phhp", "phhp", "phhp", "pppp", ".pp."],
            {"p": (176, 78, 230), "h": (240, 204, 255)})
    return g.render(2)


def gerar_tiro_inimigo():
    g = Grade(5)
    g.ascii(["..r..", ".rwr.", "rwwwr", ".rwr.", "..r.."],
            {"r": (214, 40, 44), "w": (255, 170, 150)})
    return g.render(2)


def gerar_teia():
    g = Grade(5)
    g.ascii(["a.a.a", ".aba.", "abbba", ".aba.", "a.a.a"], {"a": (96, 138, 190), "b": (240, 250, 255)})
    return g.render(2)


def gerar_lodo():
    g = Grade(15, 8)
    cor, borda, brilho = (124, 160, 62), (84, 116, 40), (184, 214, 116)
    faixas = [(5, 9), (2, 12), (1, 13), (0, 14), (0, 14), (1, 13), (2, 12), (5, 9)]
    for y, (a, b) in enumerate(faixas):
        for x in range(a, b + 1):
            g.set(x, y, borda if x in (a, b) or y in (0, 7) else cor, espelho=False)
    g.set(4, 2, brilho, espelho=False)
    g.set(5, 2, brilho, espelho=False)
    g.set(10, 5, brilho, espelho=False)
    return g.render(2)


# ---------------------------------------------------------------------------
# itens (grade 14x14 -> 28px)
# ---------------------------------------------------------------------------

def gerar_item_tiro_triplo():
    g = Grade(14)
    az, az_c = (40, 156, 232), (150, 214, 255)
    for cx, topo in ((6, 1), (2, 3)):
        g.set(cx, topo, az_c)
        g.rect(cx - 1, topo + 1, cx, topo + 1, az)
        g.rect(cx - 2, topo + 2, cx, topo + 2, az)
        g.rect(cx, topo + 3, cx, topo + 8, az)
    return g.contorno().render(2)


def gerar_item_escudo():
    g = Grade(14)
    br, sh, rim = (232, 238, 248), (150, 164, 196), (92, 108, 148)
    g.rect(3, 2, 6, 7, br)
    g.rect(4, 8, 6, 9, br)
    g.rect(5, 10, 6, 10, br)
    g.rect(6, 11, 6, 11, br)
    g.rect(3, 2, 3, 7, sh)
    g.rect(6, 3, 6, 9, rim)
    g.rect(4, 4, 5, 4, rim)
    return g.contorno().render(2)


def gerar_item_vida_extra():
    g = Grade(14)
    verm, claro = (226, 48, 62), (255, 150, 160)
    g.rect(3, 2, 5, 2, verm)
    g.rect(2, 3, 6, 3, verm)
    g.rect(2, 4, 6, 5, verm)
    g.rect(3, 6, 6, 6, verm)
    g.rect(4, 7, 6, 7, verm)
    g.rect(5, 8, 6, 8, verm)
    g.rect(6, 9, 6, 9, verm)
    g.set(3, 3, claro)
    g.set(2, 4, claro)
    return g.contorno().render(2)


def gerar_item_tiro_rapido():
    g = Grade(14)
    g.ascii([
        "......xxxx....",
        ".....xxxx.....",
        "....xxxx......",
        "...xxxxxxx....",
        "......xxx.....",
        ".....xxx......",
        "....xxx.......",
        "...xx.........",
    ], {"x": (255, 166, 28)}, x0=0, y0=2)
    g.set(7, 2, (255, 236, 120), espelho=False)
    g.set(6, 3, (255, 236, 120), espelho=False)
    return g.contorno().render(2)


def gerar_item_pimenta():
    g = Grade(14)
    g.ascii([
        "......gg......",
        ".....gg.......",
        "....rrrrr.....",
        "...rrrrrrr....",
        "...rhrrrrr....",
        "...rhrrrrr....",
        "...rrrrrrr....",
        "....rrrrr.....",
        "....rrrrr.....",
        ".....rrrr.....",
        "......rrr.....",
        ".......rr.....",
    ], {"g": (86, 168, 52), "r": (212, 38, 30), "h": (255, 136, 120)}, y0=1)
    return g.contorno().render(2)


def gerar_item_detergente():
    g = Grade(14)
    ci, ci_e, br = (44, 204, 214), (22, 140, 156), (240, 246, 248)
    g.rect(5, 1, 6, 2, br)
    g.rect(6, 3, 6, 4, ci)
    g.rect(3, 5, 6, 12, ci)
    g.rect(3, 5, 3, 12, ci_e, espelho=False)
    g.rect(4, 7, 6, 10, br)
    g.rect(5, 8, 6, 9, ci_e)
    g.set(11, 3, (180, 240, 250), espelho=False)
    return g.contorno().render(2)


def gerar_item_migalha():
    g = Grade(14)
    ouro, sombra, brilho = (255, 206, 40), (206, 150, 18), (255, 244, 160)
    g.rect(5, 2, 6, 2, ouro)
    g.rect(4, 3, 6, 3, ouro)
    g.rect(3, 4, 6, 9, ouro)
    g.rect(4, 10, 6, 10, ouro)
    g.rect(5, 11, 6, 11, ouro)
    g.rect(3, 8, 6, 9, sombra, espelho=False)
    g.rect(10, 4, 10, 9, sombra, espelho=False)
    g.set(4, 4, brilho, espelho=False)
    g.set(5, 3, brilho, espelho=False)
    g.set(4, 5, brilho, espelho=False)
    return g.contorno().render(2)


# ---------------------------------------------------------------------------
# fundos: todos são a MESMA cozinha (armários, fogão com coifa, pia com janela,
# geladeira, bancada com utensílios, piso de azulejo), montada em módulos numa
# tela de 200x150 e ampliada 4x pra ficar em blocos. O que muda de fase pra fase
# é a ordem dos módulos, a hora do dia e a situação (bagunça, teias, lodo...).
# ---------------------------------------------------------------------------

def tela_baixa():
    return pygame.Surface((200, 150))


def ampliar(s):
    return pygame.transform.scale(s, (800, 600))


def R(c, cor, x, y, w, h):
    pygame.draw.rect(c, cor, (x, y, w, h))


K = dict(
    parede=(224, 198, 152), parede_s=(210, 182, 136),
    az_a=(238, 234, 220), az_b=(226, 220, 202), rejunte=(198, 192, 174),
    arm=(178, 120, 68), arm_c=(136, 88, 46), arm_s=(92, 60, 32), arm_l=(204, 148, 92),
    base=(166, 110, 62), puxador=(206, 206, 214),
    banc=(240, 230, 210), banc_f=(150, 116, 78), rodape=(98, 66, 38),
    metal=(170, 172, 182), metal_s=(112, 114, 126), metal_c=(218, 220, 230), vidro=(40, 38, 46),
    gel=(192, 196, 206), gel_s=(140, 146, 160),
    piso_a=(238, 220, 186), piso_b=(224, 202, 166), piso_r=(204, 182, 146),
)


def graduar(c, mult, soma=(0, 0, 0)):
    """Escurece/tinge a cena inteira (noite, tempestade, bagunça...)."""
    c.fill(tuple(int(m) for m in mult), special_flags=pygame.BLEND_RGB_MULT)
    if any(soma):
        c.fill(soma, special_flags=pygame.BLEND_RGB_ADD)


def luz(c, pontos, cor, alpha):
    s = pygame.Surface((200, 150), pygame.SRCALPHA)
    pygame.draw.polygon(s, (*cor, alpha), pontos)
    c.blit(s, (0, 0))


def brilho_redondo(c, centro, raio, cor, alpha):
    s = pygame.Surface((200, 150), pygame.SRCALPHA)
    pygame.draw.circle(s, (*cor, alpha), centro, raio)
    c.blit(s, (0, 0))


# --- itens de bancada (todos "sentam" em y=38) ---------------------------

def p_torradeira(c, x):
    R(c, K["metal"], x, 32, 11, 6)
    R(c, K["metal_c"], x, 32, 11, 1)
    R(c, K["vidro"], x + 2, 31, 7, 1)
    R(c, (200, 70, 60), x + 8, 35, 2, 1)


def p_chaleira(c, x):
    R(c, (196, 60, 52), x + 1, 31, 8, 7)
    R(c, (150, 40, 36), x + 1, 36, 8, 2)
    R(c, K["metal_c"], x + 3, 30, 4, 1)
    R(c, K["metal_s"], x + 9, 32, 2, 1)
    R(c, K["metal_s"], x - 1, 32, 2, 4)


def p_potes(c, x):
    for k, (h, cor) in enumerate(((9, (236, 226, 200)), (12, (214, 150, 90)), (7, (190, 210, 226)))):
        R(c, cor, x + k * 5, 38 - h, 4, h)
        R(c, K["arm_s"], x + k * 5, 38 - h, 4, 1)


def p_fruteira(c, x):
    R(c, (150, 98, 56), x, 35, 13, 3)
    R(c, (120, 76, 40), x + 1, 37, 11, 1)
    R(c, (214, 52, 48), x + 2, 32, 3, 3)
    R(c, (240, 200, 60), x + 5, 31, 3, 4)
    R(c, (110, 170, 60), x + 8, 32, 3, 3)
    R(c, (240, 140, 50), x + 10, 33, 2, 2)


def p_tabua(c, x):
    R(c, (206, 160, 100), x, 36, 13, 2)
    R(c, (150, 110, 66), x, 37, 13, 1)
    R(c, (226, 180, 96), x + 2, 33, 8, 3)
    R(c, (176, 130, 60), x + 2, 33, 8, 1)


def p_microondas(c, x):
    R(c, (70, 72, 84), x, 26, 17, 12)
    R(c, K["vidro"], x + 2, 28, 10, 8)
    R(c, (110, 114, 128), x + 13, 28, 3, 8)
    R(c, (250, 200, 60), x + 14, 29, 1, 1)


def p_planta(c, x):
    R(c, (186, 100, 70), x + 2, 34, 7, 4)
    R(c, (140, 74, 50), x + 2, 34, 7, 1)
    R(c, (70, 140, 60), x + 5, 27, 1, 7)
    R(c, (90, 170, 70), x + 2, 28, 4, 2)
    R(c, (90, 170, 70), x + 6, 30, 4, 2)
    R(c, (90, 170, 70), x + 5, 26, 2, 2)


def p_cafeteira(c, x):
    R(c, (50, 50, 58), x, 28, 9, 10)
    R(c, (90, 52, 32), x + 1, 32, 6, 5)
    R(c, (200, 60, 50), x + 6, 29, 1, 1)


PROPS = (p_planta, p_torradeira, p_potes, p_fruteira, p_chaleira, p_microondas, p_tabua, p_cafeteira)
LARGURA_PROP = {p_microondas: 17, p_fruteira: 13, p_tabua: 13, p_potes: 14}


# --- parte de cima da parede ---------------------------------------------

def parte_armarios(c, x, w):
    n = max(1, w // 14)
    dw = w // n
    for k in range(n):
        dx = x + k * dw
        R(c, K["arm_s"], dx, 0, dw, 24)
        R(c, K["arm"], dx + 1, 1, dw - 2, 22)
        R(c, K["arm_c"], dx + 3, 3, dw - 6, 18)
        R(c, K["arm"], dx + 4, 4, dw - 8, 16)
        R(c, K["arm_l"], dx + 4, 4, dw - 8, 1)
        hx = dx + dw - 6 if k % 2 == 0 else dx + 4
        R(c, K["puxador"], hx, 17, 2, 4)


def parte_prateleira(c, x, w):
    cores = [(240, 240, 244), (210, 90, 80), (90, 150, 200), (240, 220, 140)]
    for base, alt in ((12, 6), (24, 6)):
        R(c, K["arm_c"], x, base, w, 2)
        R(c, K["arm_s"], x, base + 2, w, 1)
        cx, k = x + 2, 0
        while cx + 8 < x + w:
            R(c, cores[(k + base) % 4], cx, base - alt, 8, alt)
            R(c, (255, 255, 255), cx + 1, base - alt + 1, 2, alt - 2)
            R(c, K["arm_s"], cx, base - alt, 8, 1)
            cx += 10
            k += 1


def parte_trilho(c, x, w):
    R(c, K["metal_s"], x + 2, 4, w - 4, 1)
    pos, k = x + 6, 0
    while pos < x + w - 7:
        if k % 3 == 0:                                      # frigideira
            R(c, K["metal_s"], pos, 5, 1, 3)
            R(c, (60, 60, 70), pos - 3, 8, 8, 6)
            R(c, K["metal_c"], pos - 3, 8, 8, 1)
        elif k % 3 == 1:                                    # concha
            R(c, K["metal"], pos, 5, 1, 9)
            R(c, K["metal_s"], pos - 1, 14, 3, 3)
        else:                                               # espátula
            R(c, (200, 120, 60), pos, 5, 1, 9)
            R(c, (200, 120, 60), pos - 1, 14, 3, 4)
        pos += 11
        k += 1


def parte_relogio(c, x, w):
    cx = x + w // 2
    pygame.draw.circle(c, (246, 244, 238), (cx, 11), 8)
    pygame.draw.circle(c, K["arm_s"], (cx, 11), 8, 1)
    R(c, (40, 40, 44), cx, 6, 1, 5)
    R(c, (40, 40, 44), cx, 11, 4, 1)
    R(c, (210, 60, 52), cx - 1, 11, 1, 1)


UPPERS = (parte_armarios, parte_prateleira, parte_armarios, parte_trilho, parte_relogio)


# --- módulos da parede -----------------------------------------------------

def mod_bancada(c, x, w, i):
    UPPERS[i % len(UPPERS)](c, x, w)
    if w < 14:
        return
    px, k = x + 2, 0
    while px + 11 <= x + w:
        prop = PROPS[(i * 3 + k) % len(PROPS)] if w >= 20 else p_planta
        larg = LARGURA_PROP.get(prop, 11)
        if px + larg > x + w:
            break
        prop(c, px)
        px += larg + 5
        k += 1


def mod_pia(c, x, w, estilo):
    R(c, (244, 240, 230), x + 3, 2, w - 6, 22)           # moldura
    ceu = {"dia": (150, 206, 236), "noite": (18, 24, 52), "chuva": (50, 54, 78)}[estilo]
    R(c, ceu, x + 5, 4, w - 10, 18)
    if estilo == "dia":
        R(c, (255, 255, 255), x + 9, 7, 8, 2)
        R(c, (255, 255, 255), x + 11, 6, 5, 1)
        R(c, (255, 255, 255), x + w - 20, 10, 9, 2)
        R(c, (110, 170, 90), x + 5, 18, w - 10, 4)
    elif estilo == "noite":
        R(c, (244, 240, 200), x + w - 18, 7, 5, 5)
        R(c, ceu, x + w - 16, 7, 3, 3)
        for (sx, sy) in ((9, 8), (16, 14), (24, 7), (12, 18)):
            R(c, (240, 240, 255), x + sx, sy, 1, 1)
        R(c, (30, 40, 70), x + 5, 19, w - 10, 3)
    else:
        rnd = random.Random(x)
        for _ in range(w // 2):
            sx, sy = rnd.randint(x + 6, x + w - 8), rnd.randint(5, 19)
            R(c, (150, 170, 220), sx, sy, 1, 3)
        raio = [(x + w // 2 + 4, 4), (x + w // 2, 10), (x + w // 2 + 4, 12), (x + w // 2 - 1, 21)]
        pygame.draw.lines(c, (255, 244, 150), False, raio, 2)
    R(c, (244, 240, 230), x + w // 2 - 1, 4, 2, 18)      # travessas
    R(c, (244, 240, 230), x + 5, 12, w - 10, 1)
    R(c, (222, 214, 196), x + 1, 24, w - 2, 2)           # parapeito
    for cx in (x + 4, x + w - 13):                       # cortinas xadrez
        R(c, (212, 84, 78), cx, 2, 9, 17)
        for yy in range(3, 18, 4):
            R(c, (244, 196, 190), cx, yy, 9, 1)
        for xx in range(cx + 1, cx + 9, 3):
            R(c, (244, 196, 190), xx, 2, 1, 17)
    R(c, K["metal_s"], x + 1, 1, w - 2, 1)               # varão
    R(c, (96, 106, 124), x + 6, 38, w - 12, 5)           # cuba
    R(c, (146, 156, 174), x + 7, 38, w - 14, 1)
    tx = x + w // 2                                       # torneira
    R(c, K["metal_c"], tx - 1, 29, 2, 9)
    R(c, K["metal_c"], tx - 1, 28, 6, 2)
    R(c, K["metal_c"], tx + 4, 28, 2, 4)


def mod_fogao(c, x, w):
    R(c, K["metal_s"], x + w // 2 - 6, 0, 12, 6)         # chaminé
    R(c, K["metal_s"], x + 3, 6, w - 6, 11)              # coifa
    R(c, K["metal"], x + 4, 7, w - 8, 9)
    R(c, K["metal_c"], x + 5, 8, w - 10, 1)
    R(c, K["vidro"], x + 7, 13, w - 14, 2)
    R(c, (246, 236, 176), x + 9, 16, w - 18, 1)
    R(c, K["metal_s"], x, 36, w, 3)                      # mesa do fogão
    for bx in (x + 7, x + w - 19):
        R(c, (30, 30, 34), bx, 36, 12, 2)
        R(c, (250, 150, 40), bx + 4, 36, 4, 1)
    px = x + 8                                            # panela com vapor
    R(c, K["metal"], px + 1, 29, 10, 7)
    R(c, K["metal_c"], px + 1, 29, 10, 1)
    R(c, K["metal_s"], px - 2, 31, 3, 1)
    R(c, K["metal_s"], px + 11, 31, 3, 1)
    for (sx, sy) in ((px + 3, 26), (px + 6, 24), (px + 4, 22)):
        R(c, (240, 244, 248), sx, sy, 2, 2)
    R(c, K["metal_s"], x, 43, w, 15)                     # forno
    R(c, K["metal"], x + 1, 44, w - 2, 13)
    R(c, K["metal_c"], x + 4, 45, w - 8, 1)
    R(c, K["vidro"], x + 5, 47, w - 10, 8)
    gx = x + w // 2 - 5                                   # assadeira listrada (da referência)
    R(c, (122, 144, 78), gx, 49, 10, 6)
    for yy in (50, 52, 54):
        R(c, (78, 100, 48), gx, yy, 10, 1)


def mod_geladeira(c, x, w, aberta=False):
    if aberta:
        R(c, K["gel_s"], x, 4, w, 54)
        R(c, (232, 244, 252), x + 1, 5, w - 10, 52)
        rnd = random.Random(5)
        for yy in (16, 28, 40, 52):
            R(c, (150, 180, 200), x + 1, yy, w - 10, 1)
            cx = x + 3
            while cx + 5 < x + w - 9:
                h = rnd.randint(4, 9)
                R(c, rnd.choice([(214, 70, 60), (240, 200, 70), (90, 160, 90), (120, 150, 210)]), cx, yy - h, 5, h)
                cx += 7
        R(c, K["gel_s"], x + w - 9, 4, 9, 54)            # porta aberta, de lado
        R(c, K["gel"], x + w - 8, 5, 6, 52)
        R(c, K["metal_s"], x + w - 8, 14, 1, 14)
        return
    R(c, K["gel_s"], x, 4, w, 54)
    R(c, K["gel"], x + 1, 5, w - 3, 52)
    R(c, K["gel_s"], x + 1, 21, w - 3, 2)
    R(c, K["metal_c"], x + 2, 6, w - 6, 1)
    R(c, K["metal_s"], x + w - 7, 9, 2, 9)
    R(c, K["metal_s"], x + w - 7, 27, 2, 16)
    R(c, (250, 250, 250), x + 6, 28, 8, 10)              # bilhete e ímãs
    for yy in (30, 32, 34):
        R(c, (170, 170, 180), x + 7, yy, 5, 1)
    R(c, (214, 60, 52), x + 9, 27, 2, 2)
    R(c, (60, 130, 200), x + 18, 33, 3, 3)
    R(c, (240, 200, 60), x + 15, 44, 3, 3)


def mod_despensa(c, x, w, i):
    R(c, K["arm_s"], x, 2, w, 56)
    R(c, K["arm"], x + 1, 3, w - 2, 54)
    R(c, (62, 46, 38), x + 4, 6, w - 8, 46)
    rnd = random.Random(i * 7 + x)
    cores = [(226, 196, 120), (150, 190, 160), (210, 120, 90), (240, 236, 220), (170, 150, 200), (200, 70, 60)]
    for yy in (16, 28, 40, 52):
        R(c, K["arm_c"], x + 4, yy, w - 8, 2)
        cx = x + 6
        while cx + 6 < x + w - 4:
            h = rnd.randint(5, 10)
            cor = rnd.choice(cores)
            R(c, cor, cx, yy - h, 6, h)
            R(c, K["arm_s"], cx, yy - h, 6, 1)
            R(c, (255, 255, 255), cx + 1, yy - h + 2, 1, 3)
            cx += 8
    R(c, K["arm"], x + w // 2 - 1, 6, 2, 46)
    R(c, K["puxador"], x + w // 2 + 2, 26, 2, 8)
    R(c, K["puxador"], x + w // 2 - 4, 26, 2, 8)


def pos(layout, tipo):
    x = 0
    for t, w in layout:
        if t == tipo:
            return x, w
        x += w
    return None


def cozinha(layout, janela="dia"):
    c = tela_baixa()
    c.fill(K["parede"])
    for x in range(0, 200, 6):
        R(c, K["parede_s"], x, 0, 1, 60)
    for ty, y in enumerate(range(24, 38, 6)):                         # azulejo da parede
        for tx, x in enumerate(range(0, 200, 6)):
            R(c, K["az_a"] if (tx + ty) % 2 == 0 else K["az_b"], x, y, 6, 6)
    R(c, K["banc"], 0, 38, 200, 4)                                    # bancada
    R(c, (255, 252, 244), 0, 38, 200, 1)
    R(c, K["banc_f"], 0, 42, 200, 2)
    R(c, K["arm_s"], 0, 44, 200, 14)                                  # armários de baixo
    for dx in range(0, 200, 14):
        R(c, K["base"], dx + 1, 45, 12, 12)
        R(c, K["arm_c"], dx + 3, 47, 8, 8)
        R(c, K["base"], dx + 4, 48, 6, 6)
        R(c, K["puxador"], dx + 11 if (dx // 14) % 2 == 0 else dx + 2, 46, 1, 4)
    R(c, K["rodape"], 0, 58, 200, 2)
    for ty, y in enumerate(range(60, 150, 12)):                       # piso de azulejo
        for tx, x in enumerate(range(0, 200, 12)):
            R(c, K["piso_a"] if (tx + ty) % 2 == 0 else K["piso_b"], x, y, 12, 12)
    for y in range(60, 150, 12):
        R(c, K["piso_r"], 0, y, 200, 1)
    for x in range(0, 200, 12):
        R(c, K["piso_r"], x, 60, 1, 90)
    R(c, (196, 172, 138), 0, 60, 200, 2)

    x = 0
    for i, (tipo, w) in enumerate(layout):
        if tipo == "B":
            mod_bancada(c, x, w, i)
        elif tipo == "PIA":
            mod_pia(c, x, w, janela)
        elif tipo == "FOGAO":
            mod_fogao(c, x, w)
        elif tipo == "GEL":
            mod_geladeira(c, x, w)
        elif tipo == "GELA":
            mod_geladeira(c, x, w, aberta=True)
        elif tipo == "DESP":
            mod_despensa(c, x, w, i)
        x += w
    return c


L1 = [("B", 20), ("PIA", 48), ("B", 28), ("FOGAO", 46), ("B", 22), ("GEL", 36)]
L2 = [("GEL", 36), ("B", 22), ("FOGAO", 46), ("B", 28), ("PIA", 48), ("B", 20)]
L3 = [("B", 30), ("FOGAO", 46), ("B", 24), ("PIA", 48), ("GEL", 36), ("B", 16)]
L4 = [("DESP", 40), ("DESP", 40), ("B", 22), ("FOGAO", 46), ("B", 16), ("GEL", 36)]
L5 = [("B", 26), ("PIA", 64), ("B", 30), ("FOGAO", 44), ("GEL", 36)]
L6 = [("GEL", 36), ("B", 28), ("PIA", 48), ("B", 24), ("FOGAO", 46), ("B", 18)]
L7 = [("B", 26), ("PIA", 56), ("B", 30), ("FOGAO", 44), ("B", 8), ("GEL", 36)]
L8 = [("FOGAO", 46), ("B", 30), ("GEL", 36), ("B", 28), ("PIA", 48), ("B", 12)]
LB = [("B", 28), ("FOGAO", 46), ("B", 26), ("PIA", 40), ("B", 24), ("GELA", 36)]


# --- as 9 situações da mesma cozinha -----------------------------------------

def gerar_fundo_fase1():
    """Manhã: sol entrando pela janela da pia."""
    c = cozinha(L1)
    px, pw = pos(L1, "PIA")
    luz(c, [(px + 6, 24), (px + pw - 6, 24), (px + pw + 50, 150), (px - 10, 150)], (255, 238, 170), 34)
    return ampliar(c)


def gerar_fundo_fase2():
    """Noite: só a luz da coifa acesa."""
    c = cozinha(L2, "noite")
    graduar(c, (112, 124, 184), (0, 0, 10))
    fx, fw = pos(L2, "FOGAO")
    luz(c, [(fx + 9, 17), (fx + fw - 9, 17), (fx + fw + 14, 62), (fx - 14, 62)], (255, 232, 150), 62)
    luz(c, [(fx + 9, 17), (fx + fw - 9, 17), (fx + fw + 26, 110), (fx - 26, 110)], (255, 232, 150), 22)
    return ampliar(c)


def gerar_fundo_fase3():
    """Tarde de sol, tapete de cozinha e as tigelas do bicho de estimação."""
    c = cozinha(L3)
    graduar(c, (255, 232, 196))
    R(c, (170, 56, 48), 14, 66, 172, 14)                    # tapete comprido
    R(c, (232, 176, 76), 16, 68, 168, 10)
    for x in range(18, 182, 6):
        R(c, (186, 70, 54) if ((x - 18) // 6) % 2 == 0 else (130, 44, 38), x, 70, 6, 6)
    for x in range(14, 188, 4):
        R(c, (236, 220, 176), x, 63, 2, 3)
        R(c, (236, 220, 176), x, 80, 2, 3)
    R(c, (70, 130, 200), 6, 128, 14, 6)                     # tigelas
    R(c, (150, 90, 50), 8, 126, 10, 2)
    R(c, (210, 80, 70), 26, 130, 12, 5)
    R(c, (120, 180, 220), 28, 129, 8, 1)
    return ampliar(c)


def gerar_fundo_fase4():
    """Canto da despensa: dois armários de mantimentos e sacos no chão."""
    c = cozinha(L4)
    graduar(c, (255, 238, 212))
    for (sx, sy, cor) in ((3, 120, (232, 216, 172)), (20, 128, (214, 190, 140)), (172, 124, (232, 216, 172))):
        R(c, cor, sx, sy, 15, 17)
        R(c, (170, 146, 100), sx, sy, 15, 2)
        R(c, (120, 96, 60), sx + 3, sy + 7, 9, 4)
        R(c, (250, 240, 210), sx + 4, sy + 8, 7, 2)
    return ampliar(c)


def gerar_fundo_fase5():
    """Tempestade lá fora, cozinha na penumbra."""
    c = cozinha(L5, "chuva")
    graduar(c, (116, 122, 158), (0, 2, 12))
    px, pw = pos(L5, "PIA")
    luz(c, [(px + 6, 24), (px + pw - 6, 24), (px + pw + 20, 150), (px - 20, 150)], (190, 210, 255), 24)
    return ampliar(c)


def gerar_fundo_fase6():
    """Cozinha abandonada: escura, empoeirada e cheia de teias."""
    c = cozinha(L6, "noite")
    graduar(c, (92, 86, 112), (2, 0, 8))
    fio = (200, 200, 214)
    for (cx, sx) in ((0, 1), (199, -1)):
        for r in (14, 26, 38):
            for k in range(0, 16):
                a = k / 15 * math.pi / 2
                R(c, fio, cx + sx * int(math.cos(a) * r), int(math.sin(a) * r), 1, 1)
        for k in range(0, 91, 22):
            a = math.radians(k)
            pygame.draw.line(c, fio, (cx, 0), (cx + sx * int(math.cos(a) * 40), int(math.sin(a) * 40)))
    for (wx, wy) in ((100, 14), (150, 60)):
        for r in (5, 9, 13):
            pygame.draw.circle(c, (160, 160, 178), (wx, wy), r, 1)
        for k in range(0, 360, 45):
            a = math.radians(k)
            pygame.draw.line(c, (160, 160, 178), (wx, wy), (wx + int(math.cos(a) * 14), wy + int(math.sin(a) * 14)))
    return ampliar(c)


def gerar_fundo_fase7():
    """Cozinha suja: lodo escorrendo dos armários, louça empilhada na pia."""
    c = cozinha(L7)
    graduar(c, (150, 196, 128), (0, 6, 0))
    verde, verde_c = (110, 160, 54), (176, 220, 104)
    rnd = random.Random(8)
    for x in range(4, 200, 11):
        h = rnd.randint(6, 20)
        R(c, verde, x, 0, 4, h)
        R(c, verde, x - 1, h, 6, 3)
        R(c, verde_c, x + 1, 0, 1, h)
    px, pw = pos(L7, "PIA")
    for k, yy in enumerate((35, 33, 31)):                    # pilha de pratos sujos
        R(c, (232, 232, 224), px + 12 + (k % 2), yy, 12, 2)
        R(c, verde, px + 14, yy, 4, 1)
    for _ in range(9):
        x, y, w = rnd.randint(8, 176), rnd.randint(70, 142), rnd.randint(10, 22)
        R(c, verde, x, y, w, 6)
        R(c, verde, x + 2, y - 1, w - 4, 8)
        R(c, verde_c, x + 3, y + 1, 3, 1)
    return ampliar(c)


def gerar_fundo_fase8():
    """Alerta máximo: luz de emergência vermelha e panelas caídas pelo chão."""
    c = cozinha(L8)
    graduar(c, (212, 120, 112))
    gx, gw = pos(L8, "GEL")
    R(c, (250, 60, 50), gx + gw // 2 - 6, 0, 12, 4)
    R(c, (255, 190, 170), gx + gw // 2 - 4, 1, 4, 1)
    brilho_redondo(c, (gx + gw // 2, 2), 46, (255, 40, 30), 36)
    brilho_redondo(c, (gx + gw // 2, 2), 24, (255, 60, 40), 44)
    pygame.draw.circle(c, (90, 92, 104), (34, 126), 9)       # panela virada
    pygame.draw.circle(c, (140, 142, 156), (34, 126), 9, 1)
    R(c, (90, 92, 104), 42, 124, 14, 3)
    R(c, (232, 232, 224), 150, 118, 5, 3)                    # cacos de prato
    R(c, (232, 232, 224), 158, 124, 4, 2)
    R(c, (232, 232, 224), 146, 128, 3, 3)
    R(c, K["metal"], 100, 136, 18, 2)                        # colher e garfo caídos
    R(c, K["metal_c"], 120, 140, 14, 2)
    return ampliar(c)


def gerar_fundo_chefe():
    """O ninho: geladeira aberta no escuro, ootecas nas paredes."""
    c = cozinha(LB, "noite")
    graduar(c, (96, 62, 76), (8, 0, 4))
    gx, gw = pos(LB, "GELA")
    luz(c, [(gx, 58), (gx + gw - 8, 58), (gx - 20, 150), (gx - 100, 150)], (200, 232, 255), 40)
    rnd = random.Random(21)
    for (cx0, cy0) in ((8, 4), (70, 2), (118, 6), (4, 30), (92, 28), (140, 30)):   # ootecas
        for _ in range(4):
            ox, oy = cx0 + rnd.randint(0, 14), cy0 + rnd.randint(0, 8)
            R(c, (120, 70, 40), ox, oy, 4, 8)
            R(c, (150, 96, 60), ox + 1, oy, 1, 8)
            for yy in (oy + 2, oy + 4, oy + 6):
                R(c, (76, 44, 26), ox, yy, 4, 1)
    for _ in range(6):                                       # rachaduras vermelhas no chão
        x, y = rnd.randint(10, 190), rnd.randint(66, 140)
        pts = [(x, y)]
        for _ in range(4):
            x += rnd.randint(-6, 6)
            y += rnd.randint(3, 8)
            pts.append((x, y))
        pygame.draw.lines(c, (200, 50, 40), False, pts, 1)
    s = ampliar(c)
    escuro = pygame.Surface((800, 600), pygame.SRCALPHA)
    for i in range(0, 120, 8):
        pygame.draw.rect(escuro, (0, 0, 0, 6 + i // 4), (i, i, 800 - 2 * i, 600 - 2 * i), 8)
    s.blit(escuro, (0, 0))
    return s


# ---------------------------------------------------------------------------

GERADORES = {
    "mimi.png": gerar_mimi,
    "robo.png": gerar_robo,
    "inseto_reto.png": gerar_inseto_reto,
    "inseto_zigzag.png": gerar_inseto_zigzag,
    "barata_voadora.png": gerar_barata_voadora,
    "formiga.png": gerar_formiga,
    "traca.png": gerar_traca,
    "aranha.png": gerar_aranha,
    "mosquito.png": gerar_mosquito,
    "mosca.png": gerar_mosca,
    "pulga.png": gerar_pulga,
    "lesma.png": gerar_lesma,
    "rainha_barata.png": gerar_rainha_barata,
    "tiro.png": gerar_tiro,
    "tiro_teleguiado.png": gerar_tiro_teleguiado,
    "tiro_inimigo.png": gerar_tiro_inimigo,
    "teia.png": gerar_teia,
    "lodo.png": gerar_lodo,
    "item_tiro_triplo.png": gerar_item_tiro_triplo,
    "item_escudo.png": gerar_item_escudo,
    "item_vida_extra.png": gerar_item_vida_extra,
    "item_tiro_rapido.png": gerar_item_tiro_rapido,
    "item_pimenta.png": gerar_item_pimenta,
    "item_detergente.png": gerar_item_detergente,
    "item_migalha.png": gerar_item_migalha,
    "fundo_fase1.png": gerar_fundo_fase1,
    "fundo_fase2.png": gerar_fundo_fase2,
    "fundo_fase3.png": gerar_fundo_fase3,
    "fundo_fase4.png": gerar_fundo_fase4,
    "fundo_fase5.png": gerar_fundo_fase5,
    "fundo_fase6.png": gerar_fundo_fase6,
    "fundo_fase7.png": gerar_fundo_fase7,
    "fundo_fase8.png": gerar_fundo_fase8,
    "fundo_chefe.png": gerar_fundo_chefe,
}


if __name__ == "__main__":
    for nome, funcao in GERADORES.items():
        salvar(funcao(), nome)
    print(f"\n{len(GERADORES)} sprites geradas em {PASTA}/")
