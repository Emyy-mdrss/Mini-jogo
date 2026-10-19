from entidade import Entidade, carregar_imagem
import config


class Tiro(Entidade):
    def __init__(self, x, y, dx=0, velocidade=10):
        super().__init__(x, y, 8, 20, config.AMARELO, velocidade, sprite="tiro.png")
        self.dx = dx
        self.perfurante = False  # vira True com a Pimenta Malagueta - atravessa vários insetos

    def update(self, inimigos=None):
        self.rect.y -= self.velocidade
        self.rect.x += self.dx
        if self.rect.y < -20:
            self.kill()


class TiroTeleguiado(Tiro):
    """Tiro da Mimi: persegue o inseto mais próximo, mas só por um alcance curto."""

    def __init__(self, x, y, dx=0, velocidade=8):
        super().__init__(x, y, dx, velocidade)
        self.image = carregar_imagem("tiro_teleguiado.png", 8, 20, config.ROXO)
        self.y_inicial = y

    def update(self, inimigos=None):
        if inimigos:
            candidatos = [i for i in inimigos if i.rect.centery < self.rect.centery]
            if candidatos:
                alvo = min(
                    candidatos,
                    key=lambda i: (i.rect.centerx - self.rect.centerx) ** 2
                    + (i.rect.centery - self.rect.centery) ** 2,
                )
                if alvo.rect.centerx > self.rect.centerx:
                    self.dx = min(self.dx + 0.5, 4)
                elif alvo.rect.centerx < self.rect.centerx:
                    self.dx = max(self.dx - 0.5, -4)

        super().update()

        if self.y_inicial - self.rect.y >= config.ALCANCE_TELEGUIADO:
            self.kill()


class TiroInimigo(Entidade):
    """Projétil disparado por inimigos (Barata Voadora, Aranha, Rainha Barata).

    efeito=None -> tiro comum, tira 1 vida.
    efeito="lentidao" -> teia da aranha, deixa o jogador lento sem tirar vida.
    """

    def __init__(self, x, y, dx=0, dy=4, efeito=None):
        cor = config.CIANO if efeito == "lentidao" else (200, 30, 30)
        sprite = "teia.png" if efeito == "lentidao" else "tiro_inimigo.png"
        super().__init__(x, y, 10, 10, cor, dy, sprite=sprite)
        self.dx = dx
        self.efeito = efeito

    def update(self, *args, **kwargs):
        self.rect.y += self.velocidade
        self.rect.x += self.dx
        fora_da_tela = (
            self.rect.top > config.ALTURA
            or self.rect.bottom < 0
            or self.rect.right < 0
            or self.rect.left > config.LARGURA
        )
        if fora_da_tela:
            self.kill()
