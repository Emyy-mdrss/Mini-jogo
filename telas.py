import sys
import os
import random
import pygame
import config
import loja
import fase
import audio
from entidade import carregar_imagem

pygame.font.init()
 
try:
    FONTE_ARQUIVO = "pixel.ttf" 
    FONTE_TITULO = pygame.font.Font(FONTE_ARQUIVO, 64)
    FONTE_SUBTITULO = pygame.font.Font(FONTE_ARQUIVO, 28)
    FONTE_BOTAO = pygame.font.Font(FONTE_ARQUIVO, 32)
    FONTE_TEXTO = pygame.font.Font(FONTE_ARQUIVO, 24)
    _USA_ARQUIVO = True
except FileNotFoundError:
    FONTE_TITULO = pygame.font.SysFont("courier", 64, bold=True)
    FONTE_SUBTITULO = pygame.font.SysFont("courier", 28, bold=True)
    FONTE_BOTAO = pygame.font.SysFont("courier", 32, bold=True)
    FONTE_TEXTO = pygame.font.SysFont("courier", 24, bold=True)
    _USA_ARQUIVO = False

_TAM_BASE = {FONTE_TITULO: 64, FONTE_SUBTITULO: 28, FONTE_BOTAO: 32, FONTE_TEXTO: 24}
_FONTES_EXTRA = {}


def _fonte(tamanho):
    tamanho = max(10, int(tamanho))
    if tamanho not in _FONTES_EXTRA:
        if _USA_ARQUIVO:
            _FONTES_EXTRA[tamanho] = pygame.font.Font(FONTE_ARQUIVO, tamanho)
        else:
            _FONTES_EXTRA[tamanho] = pygame.font.SysFont("courier", tamanho, bold=True)
    return _FONTES_EXTRA[tamanho]


def _ajustar(fonte, texto, largura_max):
    """Devolve (fonte, tamanho) - a própria fonte ou uma menor onde o texto cabe."""
    tam = _TAM_BASE.get(fonte, 24)
    if fonte.size(texto)[0] <= largura_max:
        return fonte, tam
    while tam > 10:
        tam -= 1
        candidata = _fonte(tam)
        if candidata.size(texto)[0] <= largura_max:
            return candidata, tam
    return _fonte(10), 10


def _quebrar(texto, fonte, largura_max):
    linhas, atual = [], ""
    for palavra in texto.split(" "):
        teste = (atual + " " + palavra).strip()
        if fonte.size(teste)[0] <= largura_max or not atual:
            atual = teste
        else:
            linhas.append(atual)
            atual = palavra
    if atual:
        linhas.append(atual)
    return linhas


def _linhas(texto, fonte, cor, largura_max):
    """Surfaces (uma por linha) do texto, garantidamente dentro de largura_max."""
    if fonte.size(texto)[0] <= largura_max:
        return [fonte.render(texto, False, cor)]
    base = _TAM_BASE.get(fonte, 24)
    menor, tam = _ajustar(fonte, texto, largura_max)
    if tam >= base * 0.75:
        return [menor.render(texto, False, cor)]
    f = _fonte(base * 0.75)
    saida = []
    for linha in _quebrar(texto, f, largura_max):
        ajustada, _ = _ajustar(f, linha, largura_max)
        saida.append(ajustada.render(linha, False, cor))
    return saida


def _basico(evento):
    """O que vale pra qualquer tela: fechar a janela, M (mudo) e o som de tecla."""
    if evento.type == pygame.QUIT:
        pygame.quit()
        sys.exit()
    if evento.type == pygame.KEYDOWN:
        if evento.key == pygame.K_m:
            audio.alternar_mudo()
        else:
            audio.tocar("tecla")


class Botao:
    def __init__(self, x, y, largura, altura, texto, cor=config.AZUL, desativado=False):
        self.rect = pygame.Rect(x, y, largura, altura)
        self.texto = texto
        self.cor = cor
        self.desativado = desativado
        self.cor_clara = tuple(min(c + 60, 255) for c in self.cor)
        self.cor_escura = tuple(max(c - 60, 0) for c in self.cor)
        self.cor_hover = tuple(min(c + 30, 255) for c in self.cor)

    def desenhar(self, tela):
        mouse = pygame.mouse.get_pos()
        clicando = pygame.mouse.get_pressed()[0]
        em_cima = self.rect.collidepoint(mouse) and not self.desativado
        
        cor_fundo = config.CINZA if self.desativado else (self.cor_hover if em_cima else self.cor)
        
        pygame.draw.rect(tela, cor_fundo, self.rect)
        
        pygame.draw.rect(tela, config.PRETO, self.rect, 2)

        if em_cima and clicando:
            pygame.draw.line(tela, self.cor_escura, self.rect.topleft, self.rect.topright, 2)
            pygame.draw.line(tela, self.cor_escura, self.rect.topleft, self.rect.bottomleft, 2)
            pygame.draw.line(tela, self.cor_clara, self.rect.bottomleft, self.rect.bottomright, 2)
            pygame.draw.line(tela, self.cor_clara, self.rect.topright, self.rect.bottomright, 2)
            offset_y = 2
        else:
            pygame.draw.line(tela, self.cor_clara, self.rect.topleft, self.rect.topright, 2)
            pygame.draw.line(tela, self.cor_clara, self.rect.topleft, self.rect.bottomleft, 2)
            pygame.draw.line(tela, self.cor_escura, self.rect.bottomleft, self.rect.bottomright, 2)
            pygame.draw.line(tela, self.cor_escura, self.rect.topright, self.rect.bottomright, 2)
            offset_y = 0

        cor_texto = (150, 150, 150) if self.desativado else config.BRANCO

        fonte, _ = _ajustar(FONTE_BOTAO, self.texto, self.rect.width - 20)
        sombra = fonte.render(self.texto, False, config.PRETO)
        tela.blit(sombra, sombra.get_rect(center=(self.rect.centerx + 2, self.rect.centery + 2 + offset_y)))
        
        texto_render = fonte.render(self.texto, False, cor_texto)
        tela.blit(texto_render, texto_render.get_rect(center=(self.rect.centerx, self.rect.centery + offset_y)))

    def clicado(self, pos):
        return not self.desativado and self.rect.collidepoint(pos)

_CACHE = {}

def _sprite_ampliada(nome, lado_final, cor_reserva):
    chave = (nome, lado_final)
    if chave not in _CACHE:
        img = carregar_imagem(nome, 48, 48, cor_reserva)
        fator = max(1, lado_final // img.get_width())
        _CACHE[chave] = pygame.transform.scale(img, (img.get_width() * fator, img.get_height() * fator))
    return _CACHE[chave]

def _fundo(nome="fundo_fase1.png", escurecer=140):
    chave = ("fundo", nome, escurecer)
    if chave not in _CACHE:
        caminho = os.path.join(config.PASTA_SPRITES, nome)
        if os.path.exists(caminho):
            img = pygame.image.load(caminho).convert()
            img = pygame.transform.scale(img, (config.LARGURA, config.ALTURA))
        else:
            img = pygame.Surface((config.LARGURA, config.ALTURA))
            img.fill(config.PRETO)
        veu = pygame.Surface((config.LARGURA, config.ALTURA), pygame.SRCALPHA)
        veu.fill((10, 8, 14, escurecer))
        img.blit(veu, (0, 0))
        _CACHE[chave] = img
    return _CACHE[chave]

def _largura_livre(x):
    """Maior largura que um texto centralizado em x pode ter sem sair da tela."""
    return 2 * min(x, config.LARGURA - x) - 24

def _texto_centralizado(tela, texto, x, y, fonte, cor, largura_max=None):
    if largura_max is None:
        largura_max = _largura_livre(x)
    renders = _linhas(texto, fonte, cor, largura_max)
    topo = y - sum(r.get_height() for r in renders) // 2
    for r in renders:
        tela.blit(r, r.get_rect(midtop=(x, topo)))
        topo += r.get_height()

def _titulo_com_sombra(tela, texto, fonte, cor, centro):
    largura_max = _largura_livre(centro[0])
    _texto_centralizado(tela, texto, centro[0] + 4, centro[1] + 4, fonte, (10, 8, 14), largura_max)
    _texto_centralizado(tela, texto, centro[0], centro[1], fonte, cor, largura_max)

def _texto_esquerda(tela, texto, x, y, fonte, cor, largura_max):
    ajustada, _ = _ajustar(fonte, texto, largura_max)
    tela.blit(ajustada.render(texto, False, cor), (x, y))

def _texto_multilinha(tela, linhas, x, y, espaco=22, largura_max=None):
    for i, linha in enumerate(linhas):
        if linha:
            _texto_centralizado(tela, linha, x, y + i * espaco, FONTE_TEXTO, config.BRANCO, largura_max)

def tela_cutscene(tela, relogio):
    botao_pular = Botao(config.LARGURA - 160, config.ALTURA - 60, 140, 40, "pular ->", cor=config.CINZA)
    inicio = pygame.time.get_ticks()
    
    olhos = [(random.randint(50, config.LARGURA-50), random.randint(50, config.ALTURA-150)) for _ in range(8)]

    audio.musica("tema_menu")
    # som de cada cena: (começa em ms, nome do som)
    sons_da_cena = [(2000, "cena_fedor"), (4000, "cena_pragas"), (6000, "invoca")]
    ja_tocou = set()

    while True:
        tempo = pygame.time.get_ticks() - inicio
        if tempo > 8000: return

        for ms, som in sons_da_cena:
            if tempo >= ms and som not in ja_tocou:
                ja_tocou.add(som)
                audio.tocar(som)

        for evento in pygame.event.get():
            _basico(evento)
            if evento.type == pygame.KEYDOWN and evento.key in (pygame.K_ESCAPE, pygame.K_RETURN, pygame.K_SPACE):
                return
            if evento.type == pygame.MOUSEBUTTONDOWN and botao_pular.clicado(evento.pos):
                audio.tocar("click")
                return

        tela.fill((15, 15, 20)) 
        
        if tempo < 2000:
            _texto_centralizado(tela, "na calada da noite...", config.LARGURA//2, config.ALTURA//2, FONTE_SUBTITULO, config.BRANCO)
        
        elif tempo < 4000:
            pygame.draw.rect(tela, (220, 220, 225), (config.LARGURA//2 - 60, config.ALTURA//2 - 120, 120, 200))
            pygame.draw.rect(tela, (150, 150, 150), (config.LARGURA//2 - 60, config.ALTURA//2 - 20, 120, 4)) 
            pygame.draw.rect(tela, (50, 200, 50), (config.LARGURA//2 + 30, config.ALTURA//2 - 40, 40, 15)) 
            _texto_centralizado(tela, "um cheiro peculiar surgiu.", config.LARGURA//2, config.ALTURA//2 + 120, FONTE_SUBTITULO, (100, 255, 100))
            
        elif tempo < 6000:
            for ox, oy in olhos:
                pygame.draw.rect(tela, config.VERMELHO, (ox, oy, 8, 8))
                pygame.draw.rect(tela, config.VERMELHO, (ox + 16, oy, 8, 8))
            _texto_centralizado(tela, "atraindo as piores pragas.", config.LARGURA//2, config.ALTURA//2 + 100, FONTE_SUBTITULO, config.AMARELO)
            
        else:
            tela.fill((40, 10, 10))
            _texto_centralizado(tela, "A DESPENSA ESTÁ EM PERIGO!", config.LARGURA//2, config.ALTURA//2, FONTE_TITULO, config.VERMELHO)

        botao_pular.desenhar(tela)
        pygame.display.flip()
        relogio.tick(config.FPS)

def tela_menu(tela, relogio, personagem, economia):
    botao_iniciar = Botao(config.LARGURA // 2 - 220, 260, 440, 50, "jogar", cor=config.VERDE)
    botao_selecionar = Botao(config.LARGURA // 2 - 220, 325, 440, 50, "selecionar personagem")
    botao_loja = Botao(config.LARGURA // 2 - 220, 390, 440, 50, "loja da despensa", cor=config.LARANJA)

    audio.musica("tema_menu")

    while True:
        for evento in pygame.event.get():
            _basico(evento)
            if evento.type == pygame.MOUSEBUTTONDOWN:
                if botao_iniciar.clicado(evento.pos):
                    audio.tocar("click")
                    return "jogar", personagem
                if botao_selecionar.clicado(evento.pos):
                    audio.tocar("click")
                    personagem = tela_selecao_personagem(tela, relogio, personagem)
                if botao_loja.clicado(evento.pos):
                    audio.tocar("click")
                    tela_loja(tela, relogio, economia)

        tela.blit(_fundo(), (0, 0))
        
        _titulo_com_sombra(tela, "miau ou nunca", FONTE_TITULO, config.AMARELO, (config.LARGURA // 2, 70))
        
        _texto_centralizado(tela, "defenda a despensa das pragas mutantes", config.LARGURA // 2, 130, FONTE_SUBTITULO, config.BRANCO, 560)
       
        tela.blit(_sprite_ampliada("mimi.png", 96, config.ROXO), (20, 20))
        tela.blit(_sprite_ampliada("robo.png", 96, config.AZUL), (config.LARGURA - 116, 20))

        nome_personagem = "mimi" if personagem == "mimi" else "r0-bo"
        _texto_centralizado(tela, f"personagem: {nome_personagem}", config.LARGURA // 2, 210, FONTE_TEXTO, config.AMARELO)
        _texto_centralizado(tela, f"migalhas douradas: {economia.migalhas}", config.LARGURA // 2, 480, FONTE_TEXTO, config.DOURADO)

        botao_iniciar.desenhar(tela)
        botao_selecionar.desenhar(tela)
        botao_loja.desenhar(tela)
        pygame.display.flip()
        relogio.tick(config.FPS)

def tela_selecao_fase(tela, relogio, economia):
    fase_max = economia.fase_maxima
    botoes = []
    
    colunas = 4
    x_base = config.LARGURA // 2 - 320
    y_base = 200
    
    for i in range(len(fase.Fases)):
        x = x_base + (i % colunas) * 165
        y = y_base + (i // colunas) * 100
        botoes.append((i, Botao(x, y, 140, 60, f"fase {i+1}", desativado=(i > fase_max))))
        
    botoes.append(('chefe', Botao(config.LARGURA//2 - 120, y_base + 200, 240, 60, "chefe final", cor=config.VERMELHO, desativado=(len(fase.Fases) > fase_max))))
    botao_voltar = Botao(config.LARGURA // 2 - 90, config.ALTURA - 70, 180, 45, "voltar", cor=config.CINZA)

    audio.musica("tema_menu")

    while True:
        for evento in pygame.event.get():
            _basico(evento)
            if evento.type == pygame.MOUSEBUTTONDOWN:
                if botao_voltar.clicado(evento.pos):
                    audio.tocar("click")
                    return None
                for idx, b in botoes:
                    if b.clicado(evento.pos):
                        audio.tocar("click")
                        return idx
                    if b.desativado and b.rect.collidepoint(evento.pos):
                        audio.tocar("erro")      # fase ainda bloqueada

        tela.blit(_fundo(escurecer=200), (0, 0))
        _titulo_com_sombra(tela, "mapa da cozinha", FONTE_TITULO, config.BRANCO, (config.LARGURA // 2, 100))
        _texto_centralizado(tela, "escolha a área para defender", config.LARGURA // 2, 150, FONTE_SUBTITULO, config.AMARELO)

        for _, b in botoes:
            b.desenhar(tela)
        botao_voltar.desenhar(tela)

        pygame.display.flip()
        relogio.tick(config.FPS)

def tela_selecao_personagem(tela, relogio, atual):
    carta_mimi = pygame.Rect(config.LARGURA // 2 - 330, 200, 310, 260)
    carta_robo = pygame.Rect(config.LARGURA // 2 + 20, 200, 310, 260)
    botao_voltar = Botao(config.LARGURA // 2 - 90, 500, 180, 45, "voltar", cor=config.CINZA)

    audio.musica("tema_menu")

    while True:
        for evento in pygame.event.get():
            _basico(evento)
            if evento.type == pygame.MOUSEBUTTONDOWN:
                if carta_mimi.collidepoint(evento.pos):
                    audio.tocar("moeda")
                    audio.tocar("tiro_mimi", 0.9)
                    return "mimi"
                if carta_robo.collidepoint(evento.pos):
                    audio.tocar("moeda")
                    audio.tocar("tiro_robo", 0.9)
                    return "robo"
                if botao_voltar.clicado(evento.pos):
                    audio.tocar("click")
                    return atual

        tela.blit(_fundo(escurecer=170), (0, 0))
        _titulo_com_sombra(tela, "escolha seu protetor", FONTE_TITULO, config.BRANCO, (config.LARGURA // 2, 100))

        cor_borda_mimi = config.AMARELO if atual == "mimi" else config.BRANCO
        tela.blit(_sprite_ampliada("mimi.png", 96, config.ROXO), (carta_mimi.centerx - 48, carta_mimi.top + 8))
        pygame.draw.rect(tela, cor_borda_mimi, carta_mimi, 3) # Sem border_radius para pixel art
        _texto_centralizado(tela, "mimi", carta_mimi.centerx, 318, FONTE_BOTAO, config.BRANCO)
        _texto_multilinha(tela, ["tiro teleguiado", "de curto alcance", "", "dash invencivel", "(shift)"], carta_mimi.centerx, 348, largura_max=carta_mimi.width - 24)

        cor_borda_robo = config.AMARELO if atual == "robo" else config.BRANCO
        tela.blit(_sprite_ampliada("robo.png", 96, config.AZUL), (carta_robo.centerx - 48, carta_robo.top + 8))
        pygame.draw.rect(tela, cor_borda_robo, carta_robo, 3) # Sem border_radius
        _texto_centralizado(tela, "r0-bo", carta_robo.centerx, 318, FONTE_BOTAO, config.BRANCO)
        _texto_multilinha(tela, ["tiro reto e rapido", "", "espuma destroi", "pragas ao redor (e)"], carta_robo.centerx, 348, largura_max=carta_robo.width - 24)

        botao_voltar.desenhar(tela)
        pygame.display.flip()
        relogio.tick(config.FPS)

def tela_loja(tela, relogio, economia):
    botao_voltar = Botao(config.LARGURA // 2 - 90, 520, 180, 45, "voltar", cor=config.CINZA)

    audio.musica("tema_menu")

    while True:
        linhas_botoes = []
        y = 150
        for upgrade in loja.UPGRADES:
            nivel = economia.niveis.get(upgrade["id"], 0)
            maxed = nivel >= upgrade["max_nivel"]
            custo = loja.custo_atual(upgrade, nivel)
            texto_botao = "max" if maxed else f"{custo} moedas"
            botao = Botao(config.LARGURA - 215, y, 185, 40, texto_botao, cor=config.CINZA if maxed else config.LARANJA)
            linhas_botoes.append((upgrade, botao))
            y += 70

        for evento in pygame.event.get():
            _basico(evento)
            if evento.type == pygame.MOUSEBUTTONDOWN:
                if botao_voltar.clicado(evento.pos):
                    audio.tocar("click")
                    return
                for upgrade, botao in linhas_botoes:
                    if botao.clicado(evento.pos):
                        audio.tocar("compra" if loja.comprar(economia, upgrade["id"]) else "erro")
                    elif botao.desativado and botao.rect.collidepoint(evento.pos):
                        audio.tocar("erro")

        tela.blit(_fundo(escurecer=190), (0, 0))
        _titulo_com_sombra(tela, "loja da despensa", FONTE_TITULO, config.LARANJA, (config.LARGURA // 2, 70))
        _texto_esquerda(tela, f"migalhas douradas: {economia.migalhas}", 30, 110, FONTE_TEXTO, config.DOURADO, config.LARGURA - 60)

        y = 150
        for upgrade, botao in linhas_botoes:
            nivel = economia.niveis.get(upgrade["id"], 0)
            largura_texto = botao.rect.x - 30 - 20          # o texto nunca encosta no botão
            _texto_esquerda(tela, f"{upgrade['nome']} (nivel {nivel}/{upgrade['max_nivel']})", 30, y, FONTE_BOTAO, config.BRANCO, largura_texto)
            _texto_esquerda(tela, upgrade["descricao"], 30, y + 28, FONTE_TEXTO, (180, 180, 180), largura_texto)
            botao.desenhar(tela)
            y += 70

        botao_voltar.desenhar(tela)
        pygame.display.flip()
        relogio.tick(config.FPS)

def tela_transicao_fase(tela, relogio, nome_fase, numero_fase, total_fases, chefe=False, concluida=False):
    duracao = 2500
    inicio = pygame.time.get_ticks()
    audio.tocar("fase_concluida" if concluida else ("rainha_entrada" if chefe else "fase_inicio"))

    while pygame.time.get_ticks() - inicio < duracao:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                sys.exit()

        tela.fill(config.PRETO)
        
        if concluida:
            _texto_centralizado(tela, "sala limpa!", config.LARGURA // 2, 250, FONTE_TITULO, config.VERDE)
            _texto_centralizado(tela, "a ameaça recuou por agora...", config.LARGURA // 2, 310, FONTE_SUBTITULO, config.BRANCO)
        elif chefe:
            _texto_centralizado(tela, "fase final", config.LARGURA // 2, 230, FONTE_SUBTITULO, config.VERMELHO)
            _texto_centralizado(tela, nome_fase, config.LARGURA // 2, 290, FONTE_TITULO, config.VERMELHO)
        else:
            _texto_centralizado(tela, f"fase {numero_fase}/{total_fases}", config.LARGURA // 2, 230, FONTE_SUBTITULO, config.AMARELO)
            _texto_centralizado(tela, nome_fase, config.LARGURA // 2, 290, FONTE_TITULO, config.BRANCO)

        pygame.display.flip()
        relogio.tick(config.FPS)

def _fade_out(tela):
    fade = pygame.Surface((config.LARGURA, config.ALTURA))
    fade.fill(config.PRETO)
    for alpha in range(0, 255, 15):
        fade.set_alpha(alpha)
        tela.blit(fade, (0, 0))
        pygame.display.flip()
        pygame.time.delay(16)

def tela_game_over(tela, relogio, resultado):
    _fade_out(tela)
    botao_menu = Botao(config.LARGURA // 2 - 160, 420, 320, 50, "voltar ao menu", cor=config.CINZA)

    while True:
        for evento in pygame.event.get():
            _basico(evento)
            if evento.type == pygame.MOUSEBUTTONDOWN:
                if botao_menu.clicado(evento.pos):
                    audio.tocar("click")
                    return "menu"

        tela.blit(_fundo(escurecer=210), (0, 0))
        _titulo_com_sombra(tela, "a despensa caiu!", FONTE_TITULO, config.VERMELHO, (config.LARGURA // 2, 120))

        texto_fase = "você pereceu perante a rainha barata" if resultado.get("chefe") else f"ondas sobrevividas: fase {resultado['fase']} de {len(fase.Fases)}"
        _texto_centralizado(tela, texto_fase, config.LARGURA // 2, 200, FONTE_SUBTITULO, config.BRANCO)
        
        painel = pygame.Rect(config.LARGURA // 2 - 280, 250, 560, 120)
        pygame.draw.rect(tela, (40, 40, 40), painel)
        pygame.draw.rect(tela, config.BRANCO, painel, 2)

        _texto_centralizado(tela, f"pontuação final: {resultado['pontos']}", config.LARGURA // 2, 285, FONTE_BOTAO, config.BRANCO, painel.width - 30)
        _texto_centralizado(tela, f"migalhas coletadas: {resultado['migalhas']}", config.LARGURA // 2, 335, FONTE_BOTAO, config.DOURADO, painel.width - 30)

        botao_menu.desenhar(tela)
        pygame.display.flip()
        relogio.tick(config.FPS)

def tela_vitoria(tela, relogio, resultado):
    botao_continuar = Botao(config.LARGURA // 2 - 160, 420, 320, 50, "voltar ao menu")

    while True:
        for evento in pygame.event.get():
            _basico(evento)
            if evento.type == pygame.MOUSEBUTTONDOWN and botao_continuar.clicado(evento.pos):
                audio.tocar("click")
                return

        tela.blit(_fundo(escurecer=190), (0, 0))
        _titulo_com_sombra(tela, "vitória!", FONTE_TITULO, config.VERDE, (config.LARGURA // 2, 150))
        _texto_centralizado(tela, "você derrotou a rainha barata e salvou a despensa!", config.LARGURA // 2, 215, FONTE_SUBTITULO, config.BRANCO, config.LARGURA - 60)
        _texto_centralizado(tela, f"pontos: {resultado['pontos']}", config.LARGURA // 2, 270, FONTE_BOTAO, config.BRANCO)
        _texto_centralizado(tela, f"migalhas coletadas: {resultado['migalhas']}", config.LARGURA // 2, 305, FONTE_BOTAO, config.DOURADO)
        botao_continuar.desenhar(tela)
        pygame.display.flip()
        relogio.tick(config.FPS)