# Sons

Todos os sons foram **sintetizados em código** (`gerar_sons.py`, na raiz), no
estilo chiptune pra combinar com a pixel art - nenhum áudio foi baixado.
Quem toca os sons é o `audio.py`; o resto do jogo só chama
`audio.tocar("nome")` ou `audio.musica("nome")`.

> Eu não tenho como *ouvir* o resultado. Conferi tecnicamente (sem estouro,
> sem estalos, loops emendando) e testei que cada som toca na hora certa,
> mas o gosto é seu: se algum estiver alto/baixo/feio, veja "Como mexer" abaixo.

## Quando cada som toca

| Momento | Som |
|---|---|
| Música do menu, loja, seleção de fase/personagem e animação inicial | `tema_menu` |
| Música durante as fases 1-8 | `tema_jogo` |
| Música da fase do chefe | `tema_chefe` |
| Clicar num botão / voltar | `click` |
| Apertar qualquer tecla (menus) ou A/D/setas (jogo) | `tecla` |
| Escolher personagem | `moeda` + o tiro dele |
| Clicar em fase bloqueada / comprar sem saldo / habilidade recarregando | `erro` |
| Comprar na loja | `compra` |
| Início de fase / fim de fase / chefe entrando | `fase_inicio` / `fase_concluida` / `rainha_entrada` |
| Mimi atira / R0-BÔ atira | `tiro_mimi` / `tiro_robo` |
| Dash da Mimi | `dash` |
| Espuma do R0-BÔ | `espuma` |
| Pegar migalha / vida extra / outro item | `moeda` / `vida` / `powerup` |
| Levar dano / escudo absorvendo | `dano` / `escudo` |
| Pegar teia / pisar no lodo | `teia_presa` / `gosma` |
| Inseto escapou (despensa apanhou) | `erro` |
| **Cada inseto morrendo** | `inseto_reto`, `inseto_zigzag`, `barata_voadora`, `formiga`, `traca`, `aranha`, `mosquito`, `mosca`, `pulga`, `lesma` |
| Formiga / lesma / rainha levando tiro sem morrer | `armadura` / `gosma` / `rainha_hit` |
| Barata atira / aranha solta teia / chefe atira leque | `tiro_inimigo` / `teia_tiro` / `tiro_inimigo` |
| Rainha invoca insetos / morre | `invoca` / `rainha_morte` |
| **Mimi morre / R0-BÔ morre** | `morte_mimi` / `morte_robo` (a tela treme em vermelho junto) |
| Game over | `gameover` |
| **Zerar o jogo** (derrotar a rainha) | `rainha_morte` e depois `vitoria` |
| Animação inicial | `cena_fedor`, `cena_pragas`, `invoca` (e `cena_herois`/`digita` já estão prontos pra animação nova) |

Tecla **M** liga/desliga todo o som (no jogo e nos menus).

## Como mexer

- **Volume geral**: `VOLUME_MUSICA` e `VOLUME_EFEITOS` no `config.py` (0.0 a 1.0).
- **Trocar um som por um seu**: coloque `sons/<nome>.ogg` (ou `.wav`/`.mp3`)
  com o mesmo nome da tabela. Ordem de prioridade: ogg, wav, mp3. Não precisa
  mexer em código.
- **Mudar o jeito dos meus sons**: edite a função `sfx_*` correspondente em
  `gerar_sons.py` (ou o volume de cada um em `GANHO`) e rode
  `pip install numpy scipy` + `python gerar_sons.py`.
- Sem placa de som, o jogo roda normalmente, só que mudo.
