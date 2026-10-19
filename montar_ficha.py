"""Monta duas folhas de contato pra conferir a arte de uma vez:
ficha_sprites.png (personagens, insetos, chefe, projéteis, itens) e
ficha_fundos.png (um fundo por fase)."""
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

pygame.init()
pygame.display.set_mode((1, 1))
pygame.font.init()

PASTA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sprites")
FONTE = pygame.font.SysFont(None, 18)

GRUPOS = [
    ("Personagens", ["mimi.png", "robo.png"]),
    ("Insetos", [
        "inseto_reto.png", "inseto_zigzag.png", "barata_voadora.png", "formiga.png", "traca.png",
        "aranha.png", "mosquito.png", "mosca.png", "pulga.png", "lesma.png",
    ]),
    ("Chefe", ["rainha_barata.png"]),
    ("Projeteis e perigos", ["tiro.png", "tiro_teleguiado.png", "tiro_inimigo.png", "teia.png", "lodo.png"]),
    ("Itens", [
        "item_tiro_triplo.png", "item_escudo.png", "item_vida_extra.png", "item_tiro_rapido.png",
        "item_pimenta.png", "item_detergente.png", "item_migalha.png",
    ]),
]
CEL = 120
COLS = 8
ALVO = 100  # lado máximo de cada sprite na ficha


def carregar_ampliada(nome):
    img = pygame.image.load(os.path.join(PASTA, nome)).convert_alpha()
    fator = max(1, ALVO // max(img.get_size()))
    if max(img.get_size()) > ALVO:
        fator = 1
    return pygame.transform.scale(img, (img.get_width() * fator, img.get_height() * fator))


linhas_total = sum(-(-len(n) // COLS) for _, n in GRUPOS)
altura = 20 + len(GRUPOS) * 26 + linhas_total * CEL
ficha = pygame.Surface((CEL * COLS + 20, altura))
ficha.fill((226, 222, 214))

y = 10
for titulo, nomes in GRUPOS:
    ficha.blit(FONTE.render(titulo, True, (30, 30, 30)), (10, y))
    y += 22
    for i, nome in enumerate(nomes):
        col, lin = i % COLS, i // COLS
        x = 10 + col * CEL
        yy = y + lin * CEL
        pygame.draw.rect(ficha, (244, 238, 226), (x, yy, CEL - 8, CEL - 8))
        pygame.draw.rect(ficha, (190, 182, 170), (x, yy, CEL - 8, CEL - 8), 1)
        img = carregar_ampliada(nome)
        ficha.blit(img, img.get_rect(center=(x + (CEL - 8) / 2, yy + (CEL - 8) / 2 - 6)))
        ficha.blit(FONTE.render(nome.replace(".png", ""), True, (70, 70, 70)), (x + 3, yy + CEL - 24))
    y += (-(-len(nomes) // COLS)) * CEL + 4
pygame.image.save(ficha, "ficha_sprites.png")

fundos = [f"fundo_fase{i}.png" for i in range(1, 9)] + ["fundo_chefe.png"]
W, H = 260, 195
ficha_f = pygame.Surface((W * 3 + 20, H * 3 + 40))
ficha_f.fill((226, 222, 214))
ficha_f.blit(FONTE.render("Fundos por fase", True, (30, 30, 30)), (10, 8))
for i, nome in enumerate(fundos):
    img = pygame.image.load(os.path.join(PASTA, nome)).convert()
    img = pygame.transform.scale(img, (W - 10, H - 28))
    x, y = 10 + (i % 3) * W, 28 + (i // 3) * H
    ficha_f.blit(img, (x, y))
    ficha_f.blit(FONTE.render(nome.replace(".png", ""), True, (30, 30, 30)), (x, y + H - 24))
pygame.image.save(ficha_f, "ficha_fundos.png")
print("fichas geradas")
