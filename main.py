import os
import sys
import random
import pygame

import config
import hud
import telas
import fase
from jogador import Jogador
from inimigo import InsetoReto, InsetoZigueZague, RainhaBarata
from tiro import Tiro, TiroTeleguiado
from item import sortear_drop
from onda import ControladorOndas
import audio


def esperar(relogio, ms):
    fim = pygame.time.get_ticks() + ms
    while pygame.time.get_ticks() < fim:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                sys.exit()
        relogio.tick(config.FPS)


def sofrer_hit(jogador):
    audio.tocar("dano" if jogador.levar_hit() else "escudo")


def cena_derrota(tela, relogio, personagem, morreu):
    """Congela a tela com um tremor vermelho enquanto toca o som da morte."""
    audio.parar_musica(200)
    if morreu:
        audio.tocar("morte_mimi" if personagem == "mimi" else "morte_robo")
    else:
        audio.tocar("dano")
    foto = tela.copy()
    duracao = 1200 if morreu else 700
    inicio = pygame.time.get_ticks()
    veu = pygame.Surface((config.LARGURA, config.ALTURA), pygame.SRCALPHA)
    while True:
        decorrido = pygame.time.get_ticks() - inicio
        if decorrido >= duracao:
            return
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                sys.exit()
        restante = 1 - decorrido / duracao
        tela.blit(foto, (random.randint(-4, 4) * restante, random.randint(-4, 4) * restante))
        veu.fill((200, 20, 20, int(110 * (1 - restante) ** 0.5 * restante * 2)))
        tela.blit(veu, (0, 0))
        pygame.display.flip()
        relogio.tick(config.FPS)


class Economia:
    def __init__(self):
        self.migalhas = 0
        self.niveis = {}
        self.fase_maxima = 0 

    @property
    def vidas_bonus(self): return self.niveis.get("vida_extra", 0)
    @property
    def despensa_bonus(self): return self.niveis.get("despensa", 0) * 20
    @property
    def cooldown_bonus(self): return self.niveis.get("cooldown", 0) * 20
    @property
    def escudo_inicial(self): return self.niveis.get("escudo_inicial", 0) >= 1

def carregar_imagem_fundo(nome_arquivo):
    caminho = os.path.join(config.PASTA_SPRITES, nome_arquivo)
    if os.path.exists(caminho):
        return pygame.transform.scale(pygame.image.load(caminho).convert(), (config.LARGURA, config.ALTURA))
    return None

def carregar_fundos():
    fundos = {f["nome"]: carregar_imagem_fundo(f["fundo"]) for f in fase.Fases}
    fundos["chefe"] = carregar_imagem_fundo(fase.Nome_fundo_chefe)
    return fundos

def colisao_hitbox_jogador(jogador, alvo): return jogador.hitbox.colliderect(alvo.rect)

def criar_tiros(jogador, grupo_tiros):
    classe_tiro = TiroTeleguiado if jogador.tipo == "mimi" else Tiro
    velocidade = 8 if jogador.tipo == "mimi" else 13
    deslocamentos = [-4, 0, 4] if jogador.tiro_triplo_ativo else [0]
    for dx in deslocamentos:
        tiro = classe_tiro(jogador.rect.centerx, jogador.rect.top, dx, velocidade)
        tiro.perfurante = jogador.pimenta_ativa
        grupo_tiros.add(tiro)

def aplicar_item(item, jogador):
    if item.tipo == "tiro_triplo": jogador.ativar_tiro_triplo()
    elif item.tipo == "tiro_rapido": jogador.ativar_tiro_rapido()
    elif item.tipo == "escudo": jogador.ativar_escudo()
    elif item.tipo == "vida_extra": jogador.ganhar_vida()
    elif item.tipo == "pimenta": jogador.ativar_pimenta()

def matar_inimigo(inimigo, tiros_inimigos, volume=1.0):
    audio.tocar(getattr(inimigo, "som_morte", "inseto"), volume)
    if hasattr(inimigo, "ao_morrer"):
        for t in inimigo.ao_morrer(): tiros_inimigos.add(t)
    inimigo.kill()

def spawnar_inimigo(inimigos, ondas, classes_da_fase):
    classe = random.choice(classes_da_fase)
    x = random.randint(30, config.LARGURA - 30)
    velocidade = ondas.velocidade_inimigo()
    qtd = fase.Spawn_em_grupo.get(classe, 1)

    if qtd == 1:
        inimigos.add(classe(x, -20, velocidade))
    else:
        espaco = 30
        inicio = -(qtd - 1) * espaco // 2
        for i in range(qtd):
            xi = max(10, min(config.LARGURA - 10, x + inicio + i * espaco))
            inimigos.add(classe(xi, -20, velocidade))

def jogar(tela, relogio, personagem, economia, fundos, fase_inicial):
    vidas_iniciais = config.VIDAS_INICIAIS + economia.vidas_bonus
    vida_despensa_max = config.VIDA_DESPENSA_INICIAL + economia.despensa_bonus
    cooldown_inicial = max(100, config.COOLDOWN_TIRO_INICIAL - economia.cooldown_bonus)

    jogador = Jogador(config.LARGURA // 2, config.ALTURA - 46, personagem, vidas_iniciais, cooldown_inicial)
    if economia.escudo_inicial: jogador.ativar_escudo()

    grupo_jogador = pygame.sprite.GroupSingle(jogador)
    inimigos, tiros, tiros_inimigos, perigos, itens = (pygame.sprite.Group() for _ in range(5))

    vida_despensa = vida_despensa_max
    pontos, migalhas_coletadas, detergente_ate = 0, 0, 0
    espuma_efeito, chefe = None, None

    total_fases = len(fase.Fases)
    indice_fase = fase_inicial if fase_inicial != 'chefe' else total_fases
    em_fase_chefe = indice_fase >= total_fases

    audio.parar_musica(250)
    if em_fase_chefe:
        telas.tela_transicao_fase(tela, relogio, "rainha barata", total_fases + 1, total_fases, chefe=True)
    else:
        ondas = ControladorOndas(*fase.parametros_dificuldade(indice_fase))
        telas.tela_transicao_fase(tela, relogio, fase.Fases[indice_fase]["nome"], indice_fase + 1, total_fases)
        
    inicio_fase = pygame.time.get_ticks()
    audio.musica("tema_chefe" if em_fase_chefe else "tema_jogo")
    vitoria, rodando = None, True

    while rodando:
        relogio.tick(config.FPS)
        agora = pygame.time.get_ticks()

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                sys.exit()
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_m:
                    audio.alternar_mudo()
                elif evento.key in (pygame.K_a, pygame.K_d, pygame.K_LEFT, pygame.K_RIGHT):
                    audio.tocar("tecla")
                if evento.key == pygame.K_ESCAPE:
                    audio.tocar("click")
                    audio.parar_musica(250)
                    return {"pontos": pontos, "fase": total_fases if em_fase_chefe else indice_fase + 1, "chefe": em_fase_chefe, "migalhas": migalhas_coletadas, "vitoria": None}
                if evento.key == pygame.K_SPACE and jogador.pode_atirar():
                    criar_tiros(jogador, tiros)
                    jogador.registrar_tiro()
                    audio.tocar("tiro_mimi" if personagem == "mimi" else "tiro_robo")
                if evento.key == pygame.K_LSHIFT and jogador.tipo == "mimi":
                    audio.tocar("dash" if jogador.tentar_dash() else "erro", 0.8)
                if evento.key == pygame.K_e and jogador.tipo == "robo":
                    if not jogador.tentar_especial():
                        audio.tocar("erro", 0.8)
                    else:
                        audio.tocar("espuma")
                        for inimigo in list(inimigos):
                            dist = ((inimigo.rect.centerx - jogador.rect.centerx)**2 + (inimigo.rect.centery - jogador.rect.centery)**2)**0.5
                            if dist <= config.ESPUMA_RAIO and inimigo.receber_dano(3):
                                pontos += getattr(inimigo, "valor_pontos", 10)
                                if getattr(inimigo, "e_chefe", False): migalhas_coletadas += 20
                                matar_inimigo(inimigo, tiros_inimigos, 0.6)
                        espuma_efeito = (jogador.rect.center, agora + 300)

        jogador.update()
        fator_lentidao = 0.4 if agora < detergente_ate else 1.0
        inimigos.update(fator_lentidao, tiros_inimigos, inimigos, jogador, perigos)
        tiros.update(inimigos)
        tiros_inimigos.update()
        perigos.update()
        itens.update()

        if em_fase_chefe:
            if chefe is None:
                chefe = RainhaBarata(config.LARGURA // 2, -80)
                inimigos.add(chefe)
        else:
            ondas.atualizar()
            if ondas.deve_spawnar():
                spawnar_inimigo(inimigos, ondas, fase.Fases[indice_fase]["inimigos"])

        for tiro in list(tiros):
            for inimigo in pygame.sprite.spritecollide(tiro, inimigos, False):
                if inimigo.receber_dano(1):
                    if getattr(inimigo, "e_chefe", False): migalhas_coletadas += 20
                    else:
                        item_dropado = sortear_drop(inimigo.rect.centerx, inimigo.rect.centery)
                        if item_dropado: itens.add(item_dropado)
                    pontos += getattr(inimigo, "valor_pontos", 10)
                    matar_inimigo(inimigo, tiros_inimigos)
                else:
                    som_dano = getattr(inimigo, "som_dano", None)
                    if som_dano:
                        audio.tocar(som_dano)
                if not tiro.perfurante:
                    tiro.kill()
                    break

        for inimigo in pygame.sprite.spritecollide(jogador, inimigos, False, collided=colisao_hitbox_jogador):
            if not jogador.invencivel: 
                sofrer_hit(jogador)
            if inimigo.receber_dano(1):
                pontos += getattr(inimigo, "valor_pontos", 10)
                matar_inimigo(inimigo, tiros_inimigos)

        for projetil in pygame.sprite.spritecollide(jogador, tiros_inimigos, True, collided=colisao_hitbox_jogador):
            if jogador.invencivel: continue
            if getattr(projetil, "efeito", None) == "lentidao":
                if jogador.escudo:
                    jogador.escudo = False
                    audio.tocar("escudo")
                else:
                    jogador.aplicar_lentidao(config.DURACAO_TEIA)
                    audio.tocar("teia_presa")
            else: 
                sofrer_hit(jogador)

        for _ in pygame.sprite.spritecollide(jogador, perigos, False, collided=colisao_hitbox_jogador):
            if not jogador.invencivel:
                if agora >= jogador.lento_ate:
                    audio.tocar("gosma")
                jogador.aplicar_lentidao(config.DURACAO_LENTIDAO_LODO)

        for inimigo in list(inimigos):
            if inimigo.rect.top > config.ALTURA:
                inimigo.kill()
                vida_despensa -= config.DANO_POR_INIMIGO_ESCAPADO
                audio.tocar("erro", 0.7)

        for item_coletado in pygame.sprite.spritecollide(jogador, itens, True):
            audio.tocar({"migalha": "moeda", "vida_extra": "vida"}.get(item_coletado.tipo, "powerup"))
            if item_coletado.tipo == "migalha": migalhas_coletadas += 1
            elif item_coletado.tipo == "detergente": detergente_ate = agora + config.DURACAO_DETERGENTE
            else: aplicar_item(item_coletado, jogador)

        if jogador.vidas <= 0 or vida_despensa <= 0:
            rodando, vitoria = False, False
            cena_derrota(tela, relogio, personagem, morreu=jogador.vidas <= 0)

        if rodando:
            if em_fase_chefe:
                if chefe is not None and not chefe.alive():
                    rodando, vitoria = False, True
                    audio.parar_musica(400)
                    esperar(relogio, 1800)      # deixa o grito de morte da rainha terminar
            elif agora - inicio_fase >= fase.Fases[indice_fase]["duracao"]:
                indice_fase += 1
                if indice_fase > economia.fase_maxima:
                    economia.fase_maxima = indice_fase 
                
                telas.tela_transicao_fase(tela, relogio, "", 0, 0, concluida=True)
                return {"pontos": pontos, "fase": indice_fase, "chefe": False, "migalhas": migalhas_coletadas, "vitoria": "avancar"}

        nome_fundo = "chefe" if em_fase_chefe else fase.Fases[indice_fase]["nome"]
        fundo_atual = fundos.get(nome_fundo)
        if fundo_atual: tela.blit(fundo_atual, (0, 0))
        else: tela.fill(config.PRETO)
        
        pygame.draw.rect(tela, (90, 60, 30), (0, config.ALTURA - 18, config.LARGURA, 18))
        perigos.draw(tela)
        itens.draw(tela)
        tiros.draw(tela)
        tiros_inimigos.draw(tela)
        inimigos.draw(tela)
        grupo_jogador.draw(tela)

        if espuma_efeito and agora < espuma_efeito[1]:
            pygame.draw.circle(tela, config.CIANO, espuma_efeito[0], config.ESPUMA_RAIO, 3)

        hud.desenhar_hud(tela, jogador, vida_despensa, pontos, ondas.numero_onda if not em_fase_chefe else 0, migalhas_coletadas, vida_despensa_max, numero_fase=None if em_fase_chefe else indice_fase + 1, chefe=chefe if em_fase_chefe else None)
        pygame.display.flip()

    return {"pontos": pontos, "fase": total_fases if em_fase_chefe else indice_fase + 1, "chefe": em_fase_chefe, "migalhas": migalhas_coletadas, "vitoria": vitoria}

def main():
    pygame.init()
    tela = pygame.display.set_mode((config.LARGURA, config.ALTURA))
    pygame.display.set_caption("miau ou nunca")
    relogio, fundos, economia, personagem = pygame.time.Clock(), carregar_fundos(), Economia(), "robo"
    cutscene_vista = False

    audio.iniciar()
    audio.carregar()

    while True:
        acao, personagem = telas.tela_menu(tela, relogio, personagem, economia)
        
        if acao == "jogar":
            if not cutscene_vista:
                telas.tela_cutscene(tela, relogio)
                cutscene_vista = True
            
            fase_escolhida = telas.tela_selecao_fase(tela, relogio, economia)
            
            while fase_escolhida is not None:
                resultado = jogar(tela, relogio, personagem, economia, fundos, fase_escolhida)
                economia.migalhas += resultado["migalhas"]

                if resultado["vitoria"] == True:
                    audio.parar_musica(300)
                    audio.tocar("vitoria")
                    telas.tela_vitoria(tela, relogio, resultado)
                    break
                elif resultado["vitoria"] == False:
                    audio.tocar("gameover")
                    telas.tela_game_over(tela, relogio, resultado)
                    break
                elif resultado["vitoria"] == "avancar":
                    fase_escolhida = telas.tela_selecao_fase(tela, relogio, economia)
                else:
                    break

if __name__ == "__main__":
    main()