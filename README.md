## Como rodar

```
pip install pygame
python main.py
```

## Controles

- `A` / `D` ou setas: mover
- `Espaço`: atirar
- `SHIFT`: dash invencível (só com a Mimi)
- `E`: espuma em área (só com o R0-BÔ)
- `ESC`: volta pro menu
- `M`: liga/desliga o som

## Som

Música em 3 temas (menu, fases, chefe) e 43 efeitos: tiro de cada personagem,
um som pra cada inseto, morte da Mimi e do R0-BÔ, game over, vitória e a
animação inicial. Tudo gerado em código (`gerar_sons.py`) e tocado pelo
`audio.py`. Tabela completa de quando cada som toca e como trocar por um seu
em `sons/LEIA-ME.md`. Volumes no `config.py` (`VOLUME_MUSICA`, `VOLUME_EFEITOS`).

## Fases e inimigos

São 8 fases + a fase do chefe. Cada fase soma insetos novos aos anteriores
(e já começa mais rápida que a anterior):

1. **Baratas na Cozinha** - Inseto Reto, Inseto Ziguezague
2. **Pragas Voadoras** - + Barata Voadora, Traça
3. **Enxame de Pulgas** - + Pulga Saltadora (sempre em grupo de 3)
4. **Reforços Blindados** - + Formiga Blindada
5. **Ataque Relâmpago** - + Mosca Varejeira
6. **Perigo Aracnídeo** - + Aranha
7. **Lodo da Despensa** - + Lesma Gosmenta
8. **Enxame Final** - todos juntos + Mosquito Ferrão
9. **Chefe** - Rainha Barata

| Inseto | Comportamento |
|---|---|
| Inseto Reto | Desce em linha reta |
| Inseto Ziguezague | Desce em zigue-zague |
| Barata Voadora | Zigue-zague + atira reto pra baixo |
| Traça Saltitante | Pula de lado, difícil de prever |
| Pulga Saltadora | Minúscula, rapidíssima, nasce em grupo de 3 |
| Formiga Blindada | Lenta, aguenta 3 tiros |
| Mosca Varejeira | De tempos em tempos faz uma investida na direção do jogador |
| Aranha Doméstica | Solta teia que deixa o jogador lento (sem tirar vida) |
| Lesma Gosmenta | Muito lenta, aguenta 4 tiros, deixa rastro de lodo que atola |
| Mosquito Ferrão | Voo errático, solta um leque de 5 tiros ao morrer |
| **Rainha Barata** | Espiral de tiros + leque mirado no jogador + invoca insetos. Barra de vida própria |

Todos os mapas são a mesma cozinha (armários, fogão com coifa, pia com janela,
geladeira, bancada com utensílios, piso de azulejo), mudando a parte que
aparece e a situação: manhã de sol, noite com só a luz da coifa acesa, tarde
com tapete e tigelas do bicho, canto da despensa, tempestade, cozinha
abandonada cheia de teias, cozinha suja com lodo, alerta vermelho com panelas
caídas e, no chefe, o ninho: geladeira aberta no escuro com ootecas nas paredes.

## Arte

Pixel art feita em código (`gerar_sprites.py`) - ver `sprites/LEIA-ME.md`.
`python gerar_sprites.py` regenera tudo e `python montar_ficha.py` monta as
folhas de conferência (`ficha_sprites.png`, `ficha_fundos.png`).

## Estrutura dos arquivos

- `config.py` - todas as constantes
- `entidade.py` - classe base, carrega a sprite (cai pra retângulo se faltar a imagem)
- `jogador.py` - Mimi e R0-BÔ: tiro, cooldown, dash, espuma, hitbox, status "lento"
- `inimigo.py` - os 10 insetos, o lodo e a Rainha Barata
- `tiro.py` - tiro do jogador (comum e teleguiado) e tiro de inimigo
- `item.py` - os 7 itens e o sorteio de drop
- `onda.py` - dificuldade crescente dentro de cada fase
- `fase.py` - insetos e fundo de cada fase
- `loja.py` - upgrades permanentes com Migalhas Douradas
- `hud.py` - vidas, pontos, fase/onda, migalhas, barra da despensa, barra do chefe
- `telas.py` - menu, seleção de personagem, loja, transição de fase, game over, vitória
- `main.py` - loop principal
- `audio.py` - música e efeitos sonoros (liga o mixer, carrega `sons/`, mudo)
- `gerar_sons.py` - sintetiza todos os sons em `sons/`
- `gerar_sprites.py`, `montar_ficha.py` - geram e conferem a arte
- `sprites/` - os PNGs
- `sons/` - os WAVs (ver `sons/LEIA-ME.md`)

---

Miau ou Nunca
Justificativa: O jogo adota uma temática leve, humorística e cartunesca baseada em uma cozinha doméstica sob ataque de pragas domésticas mutantes. O jogador assume o papel de um protetor incomum (um gato corajoso ou um robô faxineiro) com a missão de evitar de maneira frenética que insetos tomem conta da geladeira e da despensa.

Diferenciais
Diferencial 1 - Sistema de Defesa de Posição Baseado em Linha e Hitbox Justa: Ao contrário da movimentação livre comum, o jogador atua em um eixo único horizontal na parte inferior da tela, protegendo uma barreira com medidor de vida próprio da despensa. A hitbox do jogador é estrategicamente menor que o sprite visível, permitindo esquivas finas no melhor estilo de jogos bullet hell.
Diferencial 2 - Identidade Narrativa e Dualidade de Protagonistas: Introdução de dois personagens selecionáveis com mecânicas e propostas distintas: Mimi (focada em tiros teleguiados de curto alcance e habilidade de dash invencível) e o Robô R0-BÔ (tiro em linha reta rápido e habilidade em área que destrói projéteis inimigos através de espuma).
Diferencial 3 - Sistema de Progressão de Padrões e Meta-Economia: O jogo abandona ondas aleatórias para adotar progressões geométricas pré-definidas e legíveis para cada tipo de inseto. Além disso, introduz a coleta de moedas in-game ("Migalhas Douradas") para compra de melhorias permanentes em uma loja entre os mundos.

Mecânica Base
3.1 O que será mantido
Será reaproveitada a base estrutural do loop de jogo (Update/Draw), os cálculos lógicos para a detecção de colisões básicas por caixas (AABB) e o modelo básico de classes para gerenciamento de objetos em tela (Player, Bullet e Enemy).

3.2 O que será modificado ou substituído
A movimentação do jogador passará a ser travada estritamente no eixo horizontal (side-scrolling fixo). A cadência livre de tiros contínuos será limitada por um temporizador (cooldown), e a mecânica de morte instantânea será substituída por um sistema modular de vidas por pontos e por uma barra de resistência para a retaguarda da despensa.

Implementações
4.1 Dificuldade Crescente
Variável de progressão utilizada: Estrutura de sub-ondas (Waves) acoplada ao tempo decorrido na fase (90 a 180 segundos por nível).
Fórmula ou regra de aumento: A cada troca interna de onda de insetos, a frequência de surgimento (spawn rate) no topo diminui em 12%, e a velocidade dos padrões de tiro geométricos dos inimigos aumenta em 10% de forma cumulativa.
Existe um teto (dificuldade máxima)?: Sim. Para garantir o pilar de design de leitura clara e justa dos projéteis, a velocidade máxima será limitada ao dobro do valor inicial definido para o mundo em questão.

4.2 Temporizador entre Tiros (Cooldown)
Duração inicial do cooldown: 250 milissegundos.
Forma de controle do tempo: Controle em milissegundos calculado via relógio interno do framework de desenvolvimento (Delta Time).
Interação com o power-up de tiro mais rápido: Quando o jogador coleta o item correspondente, o cooldown padrão de disparo é reduzido pela metade (125 milissegundos) por uma janela de tempo fixa.

4.3 Itens Colecionáveis (Drops dos Inimigos)
Os itens obrigatórios e adicionais serão representados visualmente como potes de tempero, alimentos ou itens de limpeza clássicos que flutuam em direção à base da tela após a derrota de pragas específicas.

Tiro triplo
Modifica os projéteis básicos para cobrir três direções simultâneas em formato de leque.
10 segundos
10%

Escudo
Gera um campo magnético de proteção que absorve o próximo projétil ou contato hostil.
Até ser atingido
8%

Vida extra
Adiciona uma unidade de "pata" ou "parafuso" ao contador de saúde primário do personagem.
Permanente
4%

Tiro mais rápido
Reduz o intervalo de recarga do cooldown de disparo pela metade da taxa base.
7 segundos
12%

Pimenta Malagueta
Ativa o tiro penetrante: as balas atravessam múltiplos insetos menores na vertical.
6 segundos
7%

Detergente Concentrado
Provoca lentidão global em todas as pragas e projéteis ativos na tela (efeito Slow Motion).
5 segundos
5%

Migalhas Douradas
Item essencial de economia coletado para ser gasto na loja permanente entre as fases.
Imediato
45%
#   M i n i - j o g o  
 