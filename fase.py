import config
from inimigo import (
    InsetoReto,
    InsetoZigueZague,
    BarataVoadora,
    FormigaBlindada,
    Traca,
    Aranha,
    MosquitoFerrao,
    LesmaGosmenta,
    MoscaVarejeira,
    PulgaSaltadora,
)

Fases = [
    {
        "nome": "baratas na cozinha",
        "inimigos": [InsetoReto, InsetoZigueZague],
        "duracao": 60000,
        "fundo": "fundo_fase1.png",
    },
    {
        "nome": "pragas voadoras",
        "inimigos": [InsetoReto, InsetoZigueZague, BarataVoadora, Traca],
        "duracao": 75000,
        "fundo": "fundo_fase2.png",
    },
    {
        "nome": "enxame de pulgas",
        "inimigos": [InsetoZigueZague, BarataVoadora, Traca, PulgaSaltadora],
        "duracao": 75000,
        "fundo": "fundo_fase3.png",
    },
    {
        "nome": "reforços blindados",
        "inimigos": [BarataVoadora, Traca, PulgaSaltadora, FormigaBlindada],
        "duracao": 80000,
        "fundo": "fundo_fase4.png",
    },
    {
        "nome": "ataque relâmpago",
        "inimigos": [FormigaBlindada, PulgaSaltadora, MoscaVarejeira],
        "duracao": 80000,
        "fundo": "fundo_fase5.png",
    },
    {
        "nome": "perigo aracnídeo",
        "inimigos": [FormigaBlindada, MoscaVarejeira, Aranha],
        "duracao": 85000,
        "fundo": "fundo_fase6.png",
    },
    {
        "nome": "lodo da despensa",
        "inimigos": [MoscaVarejeira, Aranha, LesmaGosmenta],
        "duracao": 85000,
        "fundo": "fundo_fase7.png",
    },
    {
        "nome": "enxame final",
        "inimigos": [FormigaBlindada, Aranha, LesmaGosmenta, MosquitoFerrao, MoscaVarejeira, PulgaSaltadora],
        "duracao": 90000,
        "fundo": "fundo_fase8.png",
    },
]

Nome_fundo_chefe = "fundo_chefe.png"

Spawn_em_grupo = {
    PulgaSaltadora: 3,
}

def parametros_dificuldade(indice_fase):
    intervalo_inicial = max(
        config.INTERVALO_SPAWN_MINIMO,
        config.INTERVALO_SPAWN_INICIAL - 60 * indice_fase,
    )
    velocidade_extra = 0.1 * indice_fase
    return intervalo_inicial, velocidade_extra