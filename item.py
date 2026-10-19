import random
from entidade import Entidade
import config

# cor de reserva (enquanto a sprite não existe) + nome do arquivo esperado em sprites/
TIPOS_ITEM = {
    "tiro_triplo": (config.AZUL, "item_tiro_triplo.png"),
    "escudo": (config.BRANCO, "item_escudo.png"),
    "vida_extra": (config.VERMELHO, "item_vida_extra.png"),
    "tiro_rapido": (config.LARANJA, "item_tiro_rapido.png"),
    "pimenta": ((200, 40, 0), "item_pimenta.png"),
    "detergente": (config.CIANO, "item_detergente.png"),
    "migalha": (config.DOURADO, "item_migalha.png"),
}


class Item(Entidade):
    def __init__(self, x, y, tipo):
        cor, sprite = TIPOS_ITEM[tipo]
        super().__init__(x, y, 28, 28, cor, config.VELOCIDADE_ITEM, sprite=sprite)
        self.tipo = tipo

    def update(self):
        self.rect.y += self.velocidade
        if self.rect.y > config.ALTURA:
            self.kill()


def sortear_drop(x, y):
    """Sorteia o item que cai de um inseto derrotado, seguindo as chances do GDD.
    A soma das chances é 91%, então sobra 9% de chance de não cair nada.
    """
    sorteio = random.random()
    acumulado = 0
    for tipo, chance in config.CHANCE_ITEM.items():
        acumulado += chance
        if sorteio <= acumulado:
            return Item(x, y, tipo)
    return None
