import pygame
from entidade import Entidade
import config

SPRITES_JOGADOR = {
    "mimi": "mimi.png",
    "robo": "robo.png",
}


class Jogador(Entidade):
    def __init__(self, x, y, tipo="robo", vidas_iniciais=None, cooldown_inicial=None):
        cor = config.ROXO if tipo == "mimi" else config.AZUL
        sprite = SPRITES_JOGADOR.get(tipo)
        super().__init__(x, y, 48, 48, cor, config.VELOCIDADE_JOGADOR, sprite=sprite)

        self.tipo = tipo
        # hitbox menor que o sprite visível, pra permitir esquivas finas (Diferencial 1 do GDD)
        self.hitbox = self.rect.inflate(-24, -22)

        self.vidas = vidas_iniciais if vidas_iniciais is not None else config.VIDAS_INICIAIS
        self.escudo = False
        self.ultimo_tiro = 0
        self.cooldown_base = cooldown_inicial if cooldown_inicial is not None else config.COOLDOWN_TIRO_INICIAL
        self.cooldown_atual = self.cooldown_base
        self.tiro_triplo_ate = 0
        self.tiro_rapido_ate = 0
        self.pimenta_ate = 0
        self.tiro_triplo_ativo = False
        self.pimenta_ativa = False

        # teia da aranha deixa o jogador lento por um tempo
        self.lento_ate = 0

        # dash da Mimi
        self.invencivel_ate = 0
        self.ultimo_dash = -config.DASH_COOLDOWN

        # habilidade de área do R0-BÔ
        self.ultimo_especial = -config.ESPUMA_COOLDOWN

    def update(self):
        agora = pygame.time.get_ticks()
        velocidade_atual = self.velocidade // 2 if agora < self.lento_ate else self.velocidade

        teclas = pygame.key.get_pressed()
        if teclas[pygame.K_a] or teclas[pygame.K_LEFT]:
            self.mover(-velocidade_atual, 0)
        if teclas[pygame.K_d] or teclas[pygame.K_RIGHT]:
            self.mover(velocidade_atual, 0)

        self.rect.x = max(0, min(self.rect.x, config.LARGURA - self.rect.width))
        self.hitbox.center = self.rect.center

        self.tiro_triplo_ativo = agora < self.tiro_triplo_ate
        self.pimenta_ativa = agora < self.pimenta_ate

        if agora < self.tiro_rapido_ate:
            self.cooldown_atual = self.cooldown_base // 2
        else:
            self.cooldown_atual = self.cooldown_base

    def pode_atirar(self):
        agora = pygame.time.get_ticks()
        return agora - self.ultimo_tiro >= self.cooldown_atual

    def registrar_tiro(self):
        self.ultimo_tiro = pygame.time.get_ticks()

    def ativar_tiro_triplo(self):
        self.tiro_triplo_ate = pygame.time.get_ticks() + config.DURACAO_TIRO_TRIPLO

    def ativar_tiro_rapido(self):
        self.tiro_rapido_ate = pygame.time.get_ticks() + config.DURACAO_TIRO_RAPIDO

    def ativar_pimenta(self):
        self.pimenta_ate = pygame.time.get_ticks() + config.DURACAO_PIMENTA

    def aplicar_lentidao(self, duracao):
        self.lento_ate = pygame.time.get_ticks() + duracao

    def ganhar_vida(self):
        self.vidas += 1

    def ativar_escudo(self):
        self.escudo = True

    def levar_hit(self):
        if self.escudo:
            self.escudo = False
            return False
        self.vidas -= 1
        return True

    @property
    def invencivel(self):
        return pygame.time.get_ticks() < self.invencivel_ate

    def tentar_dash(self):
        """Dash invencível da Mimi: some por um instante na direção pressionada."""
        agora = pygame.time.get_ticks()
        if agora - self.ultimo_dash < config.DASH_COOLDOWN:
            return False

        self.ultimo_dash = agora
        self.invencivel_ate = agora + config.DASH_DURACAO

        teclas = pygame.key.get_pressed()
        direcao = 0
        if teclas[pygame.K_a] or teclas[pygame.K_LEFT]:
            direcao = -1
        elif teclas[pygame.K_d] or teclas[pygame.K_RIGHT]:
            direcao = 1

        self.mover(direcao * config.DASH_DISTANCIA, 0)
        self.rect.x = max(0, min(self.rect.x, config.LARGURA - self.rect.width))
        self.hitbox.center = self.rect.center
        return True

    def tentar_especial(self):
        """Habilidade de área do R0-BÔ (espuma). Retorna True se pôde ativar."""
        agora = pygame.time.get_ticks()
        if agora - self.ultimo_especial < config.ESPUMA_COOLDOWN:
            return False
        self.ultimo_especial = agora
        return True
