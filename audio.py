import os
import pygame
import config

PASTA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sons")
EXTENSOES = (".ogg", ".wav", ".mp3")

INTERVALO_MINIMO = {"tecla": 35, "digita": 15, "click": 60}
INTERVALO_PADRAO = 55

_ativo = False
_mudo = False
_efeitos = {}
_ultimo_toque = {}
_musica_atual = None


def iniciar():
    global _ativo
    if _ativo:
        return True
    try:
        if not pygame.mixer.get_init():
            pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
        pygame.mixer.set_num_channels(32)
        _ativo = True
    except pygame.error as erro:
        print(f"aviso: sem áudio ({erro}) - o jogo vai rodar sem som.")
        _ativo = False
    return _ativo


def _achar(nome):
    for extensao in EXTENSOES:
        caminho = os.path.join(PASTA, nome + extensao)
        if os.path.exists(caminho):
            return caminho
    return None


def carregar():
    if not _ativo or not os.path.isdir(PASTA):
        return
    nomes = {os.path.splitext(arq)[0] for arq in os.listdir(PASTA)
             if os.path.splitext(arq)[1].lower() in EXTENSOES}
    for nome in sorted(nomes):
        if nome.startswith("tema_") or nome in _efeitos:
            continue
        caminho = _achar(nome)
        try:
            _efeitos[nome] = pygame.mixer.Sound(caminho)
        except pygame.error as erro:
            print(f"aviso: não consegui carregar {caminho}: {erro}")


def existe(nome):
    return nome in _efeitos


def duracao(nome):
    return int(_efeitos[nome].get_length() * 1000) if nome in _efeitos else 0


def tocar(nome, volume=1.0):
    if not _ativo or _mudo:
        return None
    som = _efeitos.get(nome)
    if som is None:
        return None
    agora = pygame.time.get_ticks()
    if agora - _ultimo_toque.get(nome, -10_000) < INTERVALO_MINIMO.get(nome, INTERVALO_PADRAO):
        return None
    _ultimo_toque[nome] = agora
    som.set_volume(max(0.0, min(1.0, config.VOLUME_EFEITOS * volume)))
    return som.play()


def musica(nome, fade_ms=600):
    global _musica_atual
    if not _ativo:
        return
    if nome == _musica_atual and pygame.mixer.music.get_busy():
        return
    caminho = _achar(nome)
    if caminho is None:
        parar_musica(fade_ms)
        return
    try:
        pygame.mixer.music.load(caminho)
        pygame.mixer.music.set_volume(0.0 if _mudo else config.VOLUME_MUSICA)
        pygame.mixer.music.play(-1, fade_ms=fade_ms)
        _musica_atual = nome
    except pygame.error as erro:
        print(f"aviso: não consegui tocar a música {caminho}: {erro}")
        _musica_atual = None


def parar_musica(fade_ms=400):
    global _musica_atual
    _musica_atual = None
    if _ativo:
        pygame.mixer.music.fadeout(fade_ms) if fade_ms else pygame.mixer.music.stop()


def alternar_mudo():
    global _mudo
    _mudo = not _mudo
    if _ativo:
        pygame.mixer.music.set_volume(0.0 if _mudo else config.VOLUME_MUSICA)
        if _mudo:
            pygame.mixer.stop()
    return _mudo


def esta_mudo():
    return _mudo
