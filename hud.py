import pygame
import config

pygame.font.init()
FONTE = pygame.font.SysFont(None, 28)
FONTE_TITULO = pygame.font.SysFont(None, 20)


def desenhar_hud(
    tela, jogador, vida_despensa, pontos, numero_onda,
    migalhas=0, vida_despensa_max=None, numero_fase=None, chefe=None,
):
    if vida_despensa_max is None:
        vida_despensa_max = config.VIDA_DESPENSA_INICIAL

    # textos da coluna da esquerda
    if numero_fase is not None:
        rotulo_fase = f"Fase {numero_fase} - Onda {numero_onda}"
    else:
        rotulo_fase = "Fase do Chefe"
    linhas_hud = [
        (f"Vidas: {jogador.vidas}", config.BRANCO),
        (f"Pontos: {pontos}", config.BRANCO),
        (rotulo_fase, config.BRANCO if numero_fase is not None else config.VERMELHO),
        (f"Migalhas: {migalhas}", config.DOURADO),
    ]

    largura_painel = max(FONTE.size(txt)[0] for txt, _ in linhas_hud) + 20
    painel = pygame.Surface((max(largura_painel, 220), 124), pygame.SRCALPHA)
    painel.fill((12, 10, 16, 150))
    tela.blit(painel, (4, 4))

    for i, (txt, cor_txt) in enumerate(linhas_hud):
        tela.blit(FONTE.render(txt, True, cor_txt), (10, 10 + i * 30))

    # barra de resistência da despensa
    largura_barra = 200
    x_barra = config.LARGURA - largura_barra - 20
    y_barra = 15

    pygame.draw.rect(tela, (60, 60, 60), (x_barra, y_barra, largura_barra, 20))

    proporcao = max(vida_despensa, 0) / vida_despensa_max
    largura_atual = int(largura_barra * proporcao)

    pygame.draw.rect(tela, (0, 200, 100), (x_barra, y_barra, largura_atual, 20))

    texto_despensa = FONTE_TITULO.render("Despensa", True, config.BRANCO)
    tela.blit(texto_despensa, (x_barra, y_barra - 18))

    # barra de vida do chefe (só durante a fase do chefe)
    if chefe is not None and chefe.alive():
        largura_barra_chefe = 400
        x_chefe = config.LARGURA // 2 - largura_barra_chefe // 2
        y_chefe = 50
        pygame.draw.rect(tela, (60, 60, 60), (x_chefe, y_chefe, largura_barra_chefe, 16))
        proporcao_chefe = max(chefe.vida, 0) / chefe.vida_max
        pygame.draw.rect(tela, config.VERMELHO, (x_chefe, y_chefe, int(largura_barra_chefe * proporcao_chefe), 16))
        texto_chefe = FONTE_TITULO.render("Rainha Barata", True, config.BRANCO)
        tela.blit(texto_chefe, texto_chefe.get_rect(center=(config.LARGURA // 2, y_chefe - 10)))

    # avisos de status (escudo, teia/lodo), empilhados pra não ficarem um em cima do outro
    avisos = []
    if jogador.escudo:
        avisos.append(("ESCUDO ATIVO", config.AZUL))
    if pygame.time.get_ticks() < jogador.lento_ate:
        avisos.append(("ATOLADO NA TEIA", config.CIANO))
    for i, (txt, cor_aviso) in enumerate(avisos):
        render = FONTE.render(txt, True, cor_aviso)
        tela.blit(render, render.get_rect(center=(config.LARGURA // 2, config.ALTURA - 80 - i * 28)))

    # habilidade especial: dash da Mimi ou espuma do R0-BÔ
    agora = pygame.time.get_ticks()
    if jogador.tipo == "mimi":
        pronto = agora - jogador.ultimo_dash >= config.DASH_COOLDOWN
        rotulo = "Dash (SHIFT)"
    else:
        pronto = agora - jogador.ultimo_especial >= config.ESPUMA_COOLDOWN
        rotulo = "Espuma (E)"

    cor = config.VERDE if pronto else (120, 120, 120)
    texto_habilidade = FONTE_TITULO.render(rotulo + (" pronto" if pronto else " recarregando"), True, cor)
    tela.blit(texto_habilidade, (10, config.ALTURA - 26))
