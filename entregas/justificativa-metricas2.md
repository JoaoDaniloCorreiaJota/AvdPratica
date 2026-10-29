# Justificativa das métricas — Dashboards 1 e 2 (Flags)

# Dashboard 1

Dataset: 193 países, descrito por 30 colunas (a coluna `image` foi removida por ter 61% de ausentes).
Todas as métricas são calculadas no `app.py` com `st.metric`, sobre os países que passam pelo intervalo escolhido na sidebar.

---

## 1. Países no filtro

- **Variável:** a variável escolhida em "Variável do intervalo" (contagem de linhas após o filtro).
- **O que mede:** quantos países, entre os 193, ficam dentro do intervalo selecionado.
- **Por que foi escolhida:** todos os outros gráficos e KPIs mudam com o filtro. Sem essa contagem, não dá para saber em quantos países eles se baseiam.
- **Público-alvo:** quem explora o dashboard (alunos e analistas de dados).
- **Decisão apoiada:** decidir se o recorte ainda tem países suficientes para confiar na correlação e no histograma. Com poucos países, a correlação fica instável.
- **O que comunica:** o tamanho da amostra por trás de tudo o que está na tela.

## 2. Mediana da população (milhões)

- **Variável:** `population`.
- **O que mede:** o valor central da população dos países filtrados.
- **Por que foi escolhida:** a EDA mostrou que `population` é muito assimétrica (skewness ≈ 8,55). Poucos países enormes puxam a média para cima, então a mediana resume melhor o país típico. Foi também a mediana que separou os grupos Low_Pop e High_Pop.
- **Público-alvo:** analistas que querem resumir o porte populacional de um recorte.
- **Decisão apoiada:** escolher a mediana, e não a média, para descrever população, e comparar recortes (por exemplo, países pequenos em área) com a base inteira.
- **O que comunica:** o tamanho do país típico do recorte, sem distorção dos outliers.

## 3. Variável mais assimétrica

- **Variável:** as variáveis selecionadas na sidebar (a que tiver a maior assimetria, em valor absoluto), na mesma escala dos histogramas (original ou `log1p`).
- **O que mede:** qual das variáveis selecionadas tem a distribuição mais torta, e o valor da assimetria (skew). Perto de 0 é simétrica, e valores altos indicam cauda longa à direita.
- **Por que foi escolhida:** o notebook usou a assimetria para decidir o tratamento. `area` (≈ 6,8) e `population` (≈ 8,55) foram transformadas com `log1p`, e a assimetria caiu para −0,27 e 0,72. Com vários histogramas na tela, o KPI aponta qual deles merece atenção primeiro.
- **Público-alvo:** analistas que decidem como tratar variáveis antes de modelar ou testar hipóteses.
- **Decisão apoiada:** aplicar ou não `log1p`, e escolher entre testes paramétricos e não paramétricos.
- **O que comunica:** quem é o "vilão" da assimetria no recorte atual, e se ele deixa de ser ao ligar o `log1p`.

## 4. Cor predominante mais comum

- **Variável:** `mainhue`.
- **O que mede:** a cor predominante mais frequente nas bandeiras dos países filtrados, com a porcentagem de países que a têm.
- **Por que foi escolhida:** é a única variável qualitativa do dashboard e mostra um padrão do design das bandeiras. No notebook, `mainhue` era desbalanceada, com vermelho em cerca de 36,8% dos países.
- **Público-alvo:** quem se interessa pelo design das bandeiras e pelos padrões de cores.
- **Decisão apoiada:** verificar se o padrão de cor muda quando o filtro muda (por exemplo, em países muito populosos), e se vale incluir `mainhue` em análises por grupo.
- **O que comunica:** que uma cor domina, e o quanto ela domina, em cada recorte.

---

## Observação

São 4 KPIs, dentro da faixa recomendada de 3 a 5. Os KPIs 2 e 3 vêm direto de achados da EDA (assimetria e escolha da mediana). O KPI 1 dá o contexto do filtro, e o KPI 4 traz uma variável qualitativa para o dashboard não ficar só com numéricas.


---

# Dashboard 2 — Perfil por grupo

## Do dado à visualização

| Etapa | Escolha |
|---|---|
| **Pergunta do dashboard** | Como os países se distribuem entre grupos (continente, idioma, religião, cor...) e qual grupo se destaca? |
| **Variáveis de agrupamento** | `landmass`, `zone`, `language`, `religion`, `mainhue`, `topleft`, `botright` e `population_category` (discretização: população ≤ mediana ou > mediana) |
| **Variáveis medidas** | contagem de países, `population` (mediana), `area` (mediana) e `colours` (média) |
| **Métricas / KPIs** | Nº de grupos, Maior grupo, Balanceamento e Grupo líder na métrica |
| **Visualização** | Gráfico de barras horizontais do agrupamento escolhido, mais a tabela com os valores exatos |

As variáveis de agrupamento são as qualitativas do dataset. As quantitativas do Dashboard 1 entram aqui apenas como "o que se mede" em cada grupo. Para medir, usei a mediana em `population` e `area` (muito assimétricas) e a média em `colours` (contagem pequena, quase simétrica).

## 1. Nº de grupos

- **Variável:** a variável de agrupamento escolhida em "Agrupar por".
- **O que mede:** quantas categorias distintas ela tem (por exemplo, 6 continentes).
- **Por que foi escolhida:** o número de categorias muda a leitura do gráfico. Com 2 grupos a comparação é simples, e com 10 já é preciso ordenar e olhar a tabela.
- **Público-alvo:** quem explora o dashboard (alunos e analistas de dados).
- **Decisão apoiada:** escolher se a variável serve para comparar grupos ou se tem categorias demais e precisa ser reagrupada.
- **O que comunica:** a granularidade do agrupamento.

## 2. Maior grupo

- **Variável:** a variável de agrupamento escolhida.
- **O que mede:** a categoria com mais países e a porcentagem do total que ela representa.
- **Por que foi escolhida:** no notebook, várias qualitativas eram desbalanceadas (por exemplo, o vermelho em `mainhue` e `botright`). Esse KPI mostra o tamanho do grupo dominante em qualquer variável.
- **Público-alvo:** analistas que vão comparar grupos ou usá-los como filtro.
- **Decisão apoiada:** decidir se um grupo é grande o suficiente para ser analisado sozinho, e quais categorias pequenas podem ser juntadas em "Outras".
- **O que comunica:** quem domina a variável e por quanto.

## 3. Balanceamento (0 a 1)

- **Variável:** a variável de agrupamento escolhida.
- **O que mede:** a entropia normalizada da distribuição dos países entre os grupos. Perto de 0, um grupo domina. Perto de 1, os grupos têm tamanhos parecidos.
- **Por que foi escolhida:** o notebook já usava entropia para medir o desbalanceamento das qualitativas, e esse KPI leva a mesma medida para o dashboard, num único número comparável entre variáveis.
- **Público-alvo:** analistas que pretendem usar a variável em testes ou modelos.
- **Decisão apoiada:** decidir se uma variável é boa para comparar grupos (alta) ou se as comparações ficariam dominadas por um grupo só (baixa).
- **O que comunica:** o quão equilibrada é a divisão, sem precisar ler a tabela inteira.

## 4. Grupo líder na métrica

- **Variável:** a variável de agrupamento mais a métrica escolhida em "Métrica da barra".
- **O que mede:** o grupo com o maior valor da métrica (por exemplo, o continente com a maior mediana de população).
- **Por que foi escolhida:** é a resposta direta do gráfico de barras, e aparece em destaque para quem não quer ler todas as barras.
- **Público-alvo:** quem quer a resposta rápida de "qual grupo se destaca".
- **Decisão apoiada:** apontar o grupo que merece atenção numa comparação, para aprofundar nele.
- **O que comunica:** o campeão da métrica e o valor dele.

---

## Observação

São 4 KPIs, dentro da faixa recomendada de 3 a 5. O Dashboard 2 funciona independente dos filtros da sidebar, que valem só para o Dashboard 1.
