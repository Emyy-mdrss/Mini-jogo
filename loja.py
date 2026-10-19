UPGRADES = [
    {
        "id": "vida_extra",
        "nome": "Reforco de Vida",
        "descricao": "+1 vida inicial",
        "custo_base": 15,
        "custo_incremento": 10,
        "max_nivel": 3,
    },
    {
        "id": "despensa",
        "nome": "Despensa Reforcada",
        "descricao": "+20 na resistencia da despensa",
        "custo_base": 20,
        "custo_incremento": 10,
        "max_nivel": 3,
    },
    {
        "id": "cooldown",
        "nome": "Gatilho Rapido",
        "descricao": "-20ms no cooldown de tiro",
        "custo_base": 25,
        "custo_incremento": 15,
        "max_nivel": 3,
    },
    {
        "id": "escudo_inicial",
        "nome": "Escudo de Partida",
        "descricao": "Comeca a fase com escudo ativo",
        "custo_base": 30,
        "custo_incremento": 0,
        "max_nivel": 1,
    },
]


def custo_atual(upgrade, nivel_atual):
    return upgrade["custo_base"] + upgrade["custo_incremento"] * nivel_atual


def comprar(economia, upgrade_id):
    upgrade = next((u for u in UPGRADES if u["id"] == upgrade_id), None)
    if upgrade is None:
        return False

    nivel_atual = economia.niveis.get(upgrade_id, 0)
    if nivel_atual >= upgrade["max_nivel"]:
        return False

    custo = custo_atual(upgrade, nivel_atual)
    if economia.migalhas < custo:
        return False

    economia.migalhas -= custo
    economia.niveis[upgrade_id] = nivel_atual + 1
    return True
