# Justificativa das métricas — Dashboard 2

## Métrica 1: Nº de grupos
- **Variável:** a variável escolhida em "Agrupar por" (`landmass`, `zone`, `language`, `religion`, `mainhue`, `topleft`, `botright` ou `population_category`, a população dividida em baixa e alta pela mediana).
- **O que mede:** quantas categorias distintas a variável escolhida tem (por exemplo, 6 continentes).
- **Por que foi escolhida:** o número de categorias muda a leitura do gráfico. Com 2 grupos a comparação é direta, e com 10 grupos já é preciso ordenar as barras e consultar a tabela.
- **Público-alvo:** quem explora o dashboard: estudantes e analistas de dados.
- **Qual decisão pode ser apoiada por essa métrica?** Escolher se a variável serve para comparar grupos ou se tem categorias demais e precisa ser reagrupada.
- **O que comunica ao público-alvo:** a granularidade do agrupamento, isto é, em quantas partes os 193 países foram divididos.

## Métrica 2: Maior grupo
- **Variável:** a variável escolhida em "Agrupar por".
- **O que mede:** a categoria com mais países e a porcentagem do total que ela representa.
- **Por que foi escolhida:** na EDA, várias variáveis qualitativas eram desbalanceadas (por exemplo, o vermelho em `mainhue` e em `botright`). Este KPI mostra o tamanho do grupo dominante em qualquer variável escolhida.
- **Público-alvo:** analistas que vão comparar grupos ou usar a variável como filtro.
- **Qual decisão pode ser apoiada por essa métrica?** Decidir se um grupo é grande o bastante para ser analisado sozinho e quais categorias pequenas podem ser juntadas em "Outras".
- **O que comunica ao público-alvo:** quem domina a variável e por quanto.

## Métrica 3: Balanceamento (0 a 1)
- **Variável:** a variável escolhida em "Agrupar por".
- **O que mede:** a entropia normalizada da distribuição dos países entre os grupos. Perto de 0, um grupo domina. Perto de 1, os grupos têm tamanhos parecidos.
- **Por que foi escolhida:** a EDA já usava a entropia para medir o desbalanceamento das variáveis qualitativas. Este KPI leva a mesma medida para o dashboard, num único número que dá para comparar entre variáveis.
- **Público-alvo:** analistas que pretendem usar a variável em testes estatísticos ou em modelos.
- **Qual decisão pode ser apoiada por essa métrica?** Decidir se a variável é boa para comparar grupos (balanceamento alto) ou se as comparações ficariam dominadas por um grupo só (balanceamento baixo).
- **O que comunica ao público-alvo:** o quanto a divisão dos países é equilibrada, sem precisar ler a tabela inteira.

## Métrica 4: Grupo líder na métrica
- **Variável:** a variável escolhida em "Agrupar por" combinada com a métrica escolhida em "Métrica da barra" (nº de países, mediana de `population`, mediana de `area` ou média de `colours`).
- **O que mede:** o grupo com o maior valor da métrica escolhida (por exemplo, o continente com a maior mediana de população) e esse valor.
- **Por que foi escolhida:** é a resposta direta do gráfico de barras, em destaque para quem não quer ler todas as barras. As medianas foram usadas em `population` e `area` porque essas variáveis são muito assimétricas.
- **Público-alvo:** quem quer a resposta rápida de qual grupo se destaca.
- **Qual decisão pode ser apoiada por essa métrica?** Apontar o grupo que merece atenção numa comparação, para aprofundar a análise nele.
- **O que comunica ao público-alvo:** qual é o grupo campeão da métrica e quanto ele vale.

## Métrica 5: Países na seleção
- **Variável:** os grupos clicados no gráfico de barras e a métrica escolhida em "Métrica da barra".
- **O que mede:** quantos países pertencem aos grupos selecionados e o valor da métrica calculado só sobre eles (por exemplo, a mediana da população dos países da Europa).
- **Por que foi escolhida:** liga o gráfico às métricas (seleção ligada entre gráfico e KPI). Sem ela, o gráfico só mostra o quadro geral. Com ela, dá para ir de um grupo até os países que o compõem.
- **Público-alvo:** quem explora o dashboard e quer olhar um grupo de perto.
- **Qual decisão pode ser apoiada por essa métrica?** Verificar se um grupo, ou uma combinação de grupos, se comporta diferente do conjunto inteiro, e escolher quais países inspecionar na tabela.
- **O que comunica ao público-alvo:** o tamanho e o perfil do recorte escolhido. Sem seleção, o cartão mostra "—" e indica que basta clicar numa barra.