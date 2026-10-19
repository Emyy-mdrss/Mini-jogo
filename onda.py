import pygame
import config


class ControladorOndas:
    def __init__(self, intervalo_spawn_inicial=None, velocidade_extra=0.0):
        self.numero_onda = 1
        self.intervalo_spawn = intervalo_spawn_inicial or config.INTERVALO_SPAWN_INICIAL
        self.multiplicador_velocidade = 1.0 + velocidade_extra
        self.ultimo_spawn = pygame.time.get_ticks()
        self.inicio_onda = pygame.time.get_ticks()

    def deve_spawnar(self):
        agora = pygame.time.get_ticks()
        if agora - self.ultimo_spawn >= self.intervalo_spawn:
            self.ultimo_spawn = agora
            return True
        return False

    def atualizar(self):
        agora = pygame.time.get_ticks()
        if agora - self.inicio_onda >= config.DURACAO_ONDA:
            self._avancar_onda()

    def _avancar_onda(self):
        self.numero_onda += 1
        self.inicio_onda = pygame.time.get_ticks()
        self.intervalo_spawn = max(
            config.INTERVALO_SPAWN_MINIMO,
            self.intervalo_spawn * config.FATOR_REDUCAO_SPAWN,
        )
        self.multiplicador_velocidade = min(
            self.multiplicador_velocidade + config.FATOR_AUMENTO_VELOCIDADE,
            config.VELOCIDADE_MAXIMA_MULTIPLICADOR,
        )

    def velocidade_inimigo(self):
        return config.VELOCIDADE_INIMIGO_BASE * self.multiplicador_velocidade
