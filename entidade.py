import os
import pygame

import config


def carregar_imagem(nome_arquivo, largura, altura, cor_reserva):
    if nome_arquivo:
        caminho = os.path.join(config.PASTA_SPRITES, nome_arquivo)
        if os.path.exists(caminho):
            imagem = pygame.image.load(caminho).convert_alpha()
            if imagem.get_size() != (largura, altura):
                imagem = pygame.transform.scale(imagem, (largura, altura))
            return imagem

    superficie = pygame.Surface((largura, altura), pygame.SRCALPHA)
    superficie.fill(cor_reserva)
    return superficie


class Entidade(pygame.sprite.Sprite):
    def __init__(self, x, y, largura, altura, cor, velocidade, sprite=None):
        super().__init__()
        self.velocidade = velocidade
        self.image = carregar_imagem(sprite, largura, altura, cor)
        self.rect = self.image.get_rect(center=(x, y))

    def mover(self, dx, dy):
        self.rect.x += dx
        self.rect.y += dy
