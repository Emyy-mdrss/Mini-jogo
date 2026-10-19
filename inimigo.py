import random
import math
import pygame

import audio
from entidade import Entidade
from tiro import TiroInimigo
import config


class Inseto(Entidade):
    som_morte = "inseto"
    som_dano = None

    def __init__(self, x, y, velocidade, cor, sprite=None, vida=1, tamanho=48):
        super().__init__(x, y, tamanho, tamanho, cor, velocidade, sprite=sprite)
        self.vida = vida
        self.valor_pontos = 10

    def receber_dano(self, dano=1):
        self.vida -= dano
        return self.vida <= 0

    def update(self, fator=1.0, tiros_inimigos=None, inimigos=None, jogador=None, perigos=None):
        self.rect.y += self.velocidade * fator


class InsetoReto(Inseto):
    som_morte = "inseto_reto"

    def __init__(self, x, y, velocidade):
        super().__init__(x, y, velocidade, config.VERMELHO, sprite="inseto_reto.png")


class InsetoZigueZague(Inseto):
    som_morte = "inseto_zigzag"

    def __init__(self, x, y, velocidade):
        super().__init__(x, y, velocidade, config.ROXO, sprite="inseto_zigzag.png")
        self.direcao = random.choice([-1, 1])

    def update(self, fator=1.0, tiros_inimigos=None, inimigos=None, jogador=None, perigos=None):
        self.rect.y += self.velocidade * fator
        self.rect.x += self.direcao * (self.velocidade * 0.8) * fator
        if self.rect.x <= 0 or self.rect.x >= config.LARGURA - self.rect.width:
            self.direcao *= -1


class BarataVoadora(Inseto):
    """Barata Voadora Comum - zigue-zague descendo e atira reto pra baixo."""

    som_morte = "barata_voadora"

    def __init__(self, x, y, velocidade):
        super().__init__(x, y, velocidade, (120, 70, 20), sprite="barata_voadora.png")
        self.valor_pontos = 15
        self.direcao = random.choice([-1, 1])
        self.ultimo_tiro = pygame.time.get_ticks() + random.randint(0, config.COOLDOWN_TIRO_INIMIGO)

    def update(self, fator=1.0, tiros_inimigos=None, inimigos=None, jogador=None, perigos=None):
        self.rect.y += self.velocidade * fator
        self.rect.x += self.direcao * (self.velocidade * 0.7) * fator
        if self.rect.x <= 0 or self.rect.x >= config.LARGURA - self.rect.width:
            self.direcao *= -1

        if tiros_inimigos is not None:
            agora = pygame.time.get_ticks()
            if agora - self.ultimo_tiro >= config.COOLDOWN_TIRO_INIMIGO:
                self.ultimo_tiro = agora
                audio.tocar("tiro_inimigo")
                tiros_inimigos.add(
                    TiroInimigo(self.rect.centerx, self.rect.bottom, 0, config.VELOCIDADE_TIRO_INIMIGO)
                )


class FormigaBlindada(Inseto):
    """Formiga Blindada - marcha reto e lenta, mas aguenta 3 tiros (dano por contato)."""

    som_morte = "formiga"
    som_dano = "armadura"

    def __init__(self, x, y, velocidade):
        super().__init__(x, y, velocidade * 0.6, (90, 70, 30), sprite="formiga.png", vida=3)
        self.valor_pontos = 30


class Traca(Inseto):
    """Traça Saltitante - pula em pequenos arcos, difícil de prever."""

    som_morte = "traca"

    def __init__(self, x, y, velocidade):
        super().__init__(x, y, velocidade, (150, 130, 90), sprite="traca.png")
        self.valor_pontos = 12
        self.timer_pulo = random.randint(15, 30)
        self.vel_x_pulo = 0

    def update(self, fator=1.0, tiros_inimigos=None, inimigos=None, jogador=None, perigos=None):
        self.timer_pulo -= 1
        if self.timer_pulo <= 0:
            self.timer_pulo = random.randint(20, 40)
            self.vel_x_pulo = random.choice([-1, 1]) * random.randint(3, 6)

        self.rect.y += self.velocidade * fator
        self.rect.x += self.vel_x_pulo * fator
        self.rect.x = max(0, min(self.rect.x, config.LARGURA - self.rect.width))


class Aranha(Inseto):
    """Aranha Doméstica - desce devagar e solta teias que deixam o jogador lento."""

    som_morte = "aranha"

    def __init__(self, x, y, velocidade):
        super().__init__(x, y, velocidade * 0.6, (50, 50, 50), sprite="aranha.png")
        self.valor_pontos = 15
        self.ultimo_tiro = pygame.time.get_ticks() + random.randint(0, config.COOLDOWN_TIRO_INIMIGO)

    def update(self, fator=1.0, tiros_inimigos=None, inimigos=None, jogador=None, perigos=None):
        self.rect.y += self.velocidade * fator

        if tiros_inimigos is not None:
            agora = pygame.time.get_ticks()
            if agora - self.ultimo_tiro >= config.COOLDOWN_TIRO_INIMIGO * 1.4:
                self.ultimo_tiro = agora
                audio.tocar("teia_tiro")
                tiros_inimigos.add(
                    TiroInimigo(
                        self.rect.centerx, self.rect.bottom, 0,
                        config.VELOCIDADE_TIRO_INIMIGO - 1, efeito="lentidao",
                    )
                )


class MosquitoFerrao(Inseto):
    """Mosquito Ferrão - voo errático, solta um leque de projéteis ao morrer."""

    som_morte = "mosquito"

    def __init__(self, x, y, velocidade):
        super().__init__(x, y, velocidade, (110, 60, 110), sprite="mosquito.png")
        self.valor_pontos = 15

    def update(self, fator=1.0, tiros_inimigos=None, inimigos=None, jogador=None, perigos=None):
        self.rect.y += self.velocidade * fator
        self.rect.x += random.randint(-3, 3) * fator
        self.rect.x = max(0, min(self.rect.x, config.LARGURA - self.rect.width))

    def ao_morrer(self):
        tiros = []
        for angulo in (-60, -30, 0, 30, 60):
            rad = math.radians(angulo)
            dx = math.sin(rad) * 4
            dy = math.cos(rad) * 4
            tiros.append(TiroInimigo(self.rect.centerx, self.rect.centery, dx, dy))
        return tiros


class Lodo(Entidade):
    """Poça de lodo deixada pela Lesma Gosmenta. Fica parada no chão por um
    tempo e deixa o jogador lento enquanto ele estiver em cima dela."""

    def __init__(self, x, y):
        super().__init__(x, y, 30, 16, (120, 150, 60), 0, sprite="lodo.png")
        self.criado_em = pygame.time.get_ticks()
        self.efeito = "lentidao"

    def update(self, *args, **kwargs):
        if pygame.time.get_ticks() - self.criado_em >= config.DURACAO_LODO:
            self.kill()


class LesmaGosmenta(Inseto):
    """Lesma Gosmenta - bem lenta e resistente (4 tiros), deixa um rastro de
    lodo escorregadio que atola o jogador se ele pisar nele."""

    som_morte = "lesma"
    som_dano = "gosma"

    def __init__(self, x, y, velocidade):
        super().__init__(x, y, velocidade * 0.45, (130, 160, 70), sprite="lesma.png", vida=4)
        self.valor_pontos = 35
        self.ultimo_lodo = pygame.time.get_ticks()

    def update(self, fator=1.0, tiros_inimigos=None, inimigos=None, jogador=None, perigos=None):
        self.rect.y += self.velocidade * fator

        if perigos is not None:
            agora = pygame.time.get_ticks()
            if agora - self.ultimo_lodo >= config.INTERVALO_LODO:
                self.ultimo_lodo = agora
                perigos.add(Lodo(self.rect.centerx, self.rect.bottom))


class MoscaVarejeira(Inseto):
    """Mosca Varejeira - voa descendo normalmente, mas de tempos em tempos
    dispara numa investida rápida na direção horizontal do jogador."""

    som_morte = "mosca"

    def __init__(self, x, y, velocidade):
        super().__init__(x, y, velocidade, (70, 90, 60), sprite="mosca.png")
        self.valor_pontos = 18
        self.ultima_investida = pygame.time.get_ticks() + random.randint(0, config.INTERVALO_INVESTIDA_MOSCA)
        self.investida_ate = 0
        self.dx_investida = 0

    def update(self, fator=1.0, tiros_inimigos=None, inimigos=None, jogador=None, perigos=None):
        agora = pygame.time.get_ticks()

        if agora < self.investida_ate:
            self.rect.x += self.dx_investida * fator
            self.rect.y += self.velocidade * 1.4 * fator
        else:
            self.rect.y += self.velocidade * fator
            if jogador is not None and agora - self.ultima_investida >= config.INTERVALO_INVESTIDA_MOSCA:
                self.ultima_investida = agora
                self.investida_ate = agora + config.DURACAO_INVESTIDA_MOSCA
                direcao = 1 if jogador.rect.centerx >= self.rect.centerx else -1
                self.dx_investida = direcao * (self.velocidade * 2.2)

        self.rect.x = max(0, min(self.rect.x, config.LARGURA - self.rect.width))


class PulgaSaltadora(Inseto):
    """Pulga Saltadora - minúscula e rapidíssima, sempre aparece em grupos de
    3 (ver fase.py / main.py) e pula de forma bem errática."""

    som_morte = "pulga"

    def __init__(self, x, y, velocidade):
        super().__init__(x, y, velocidade * 1.4, (60, 45, 35), sprite="pulga.png", tamanho=24)
        self.valor_pontos = 8
        self.timer_pulo = random.randint(8, 16)
        self.vel_x_pulo = 0

    def update(self, fator=1.0, tiros_inimigos=None, inimigos=None, jogador=None, perigos=None):
        self.timer_pulo -= 1
        if self.timer_pulo <= 0:
            self.timer_pulo = random.randint(10, 18)
            self.vel_x_pulo = random.choice([-1, 1]) * random.randint(5, 9)

        self.rect.y += self.velocidade * fator
        self.rect.x += self.vel_x_pulo * fator
        self.rect.x = max(0, min(self.rect.x, config.LARGURA - self.rect.width))


class RainhaBarata(Entidade):
    """Chefe final - espiral de tiros, leque mirado no jogador e invocação de minions."""

    som_morte = "rainha_morte"
    som_dano = "rainha_hit"

    def __init__(self, x, y):
        super().__init__(x, y, 120, 120, (150, 20, 20), 2, sprite="rainha_barata.png")
        self.vida = config.VIDA_BOSS
        self.vida_max = config.VIDA_BOSS
        self.valor_pontos = 500
        self.e_chefe = True

        self.y_alvo = 150
        self.direcao = 1
        self.angulo_espiral = 0
        self.ultimo_espiral = 0
        self.ultimo_leque = pygame.time.get_ticks()
        self.ultima_invocacao = pygame.time.get_ticks()

    def receber_dano(self, dano=1):
        self.vida -= dano
        return self.vida <= 0

    def update(self, fator=1.0, tiros_inimigos=None, inimigos=None, jogador=None, perigos=None):
        if self.rect.centery < self.y_alvo:
            self.rect.y += 3
            return

        self.rect.x += self.direcao * 2
        if self.rect.left <= 0 or self.rect.right >= config.LARGURA:
            self.direcao *= -1

        agora = pygame.time.get_ticks()

        if tiros_inimigos is not None:
            if agora - self.ultimo_espiral >= config.COOLDOWN_ESPIRAL_BOSS:
                self.ultimo_espiral = agora
                self.angulo_espiral = (self.angulo_espiral + 25) % 360
                rad = math.radians(self.angulo_espiral)
                dx = math.sin(rad) * 4
                dy = abs(math.cos(rad) * 4) + 2
                tiros_inimigos.add(TiroInimigo(self.rect.centerx, self.rect.centery, dx, dy))

            if agora - self.ultimo_leque >= config.COOLDOWN_LEQUE_BOSS:
                self.ultimo_leque = agora
                audio.tocar("tiro_inimigo", 1.0)
                # o leque mira na direção do jogador em vez de sempre reto pra baixo
                if jogador is not None:
                    dx_alvo = jogador.rect.centerx - self.rect.centerx
                    dy_alvo = max(jogador.rect.centery - self.rect.centery, 1)
                else:
                    dx_alvo, dy_alvo = 0, 1
                angulo_base = math.atan2(dx_alvo, dy_alvo)
                for deslocamento_graus in (-50, -25, 0, 25, 50):
                    ang = angulo_base + math.radians(deslocamento_graus)
                    dx = math.sin(ang) * 5
                    dy = math.cos(ang) * 5
                    tiros_inimigos.add(TiroInimigo(self.rect.centerx, self.rect.centery, dx, dy))

        if inimigos is not None and agora - self.ultima_invocacao >= config.COOLDOWN_INVOCACAO_BOSS:
            self.ultima_invocacao = agora
            audio.tocar("invoca")
            for deslocamento in (-40, 40):
                classe = random.choice([InsetoReto, InsetoZigueZague])
                inimigos.add(
                    classe(self.rect.centerx + deslocamento, self.rect.bottom, config.VELOCIDADE_INIMIGO_BASE)
                )
