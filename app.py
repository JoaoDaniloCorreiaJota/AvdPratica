import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

from src.data_loader import load_data

# ------------------------------------------------------------------ Identidade visual
# (as cores do tema da interface ficam em .streamlit/config.toml)
LARANJA = "#F26B0F"
AZUL = "#2A6F97"
CREME = "#FFF7EC"
TEXTO = "#3A3A3A"
ESCALA_DIVERGENTE = [[0.0, AZUL], [0.5, CREME], [1.0, LARANJA]]  # azul (−1) → creme (0) → laranja (+1)


def estilo(fig):
    """Deixa os gráficos do Plotly com a identidade do app (aplicar antes de ajustes próprios)."""
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_color=TEXTO,
        margin=dict(l=10, r=10, t=30, b=10),
    )
    return fig


# Rótulos dos códigos numéricos (conferir com a descrição do dataset Flags)
ROTULOS = {
    "landmass": {1: "América do Norte", 2: "América do Sul", 3: "Europa",
                 4: "África", 5: "Ásia", 6: "Oceania"},
    "zone": {1: "Nordeste", 2: "Sudeste", 3: "Sudoeste", 4: "Noroeste"},
    "language": {1: "Inglês", 2: "Espanhol", 3: "Francês", 4: "Alemão", 5: "Eslavo",
                 6: "Outra indo-europeia", 7: "Chinês", 8: "Árabe",
                 9: "Japonês/Turco/Finlandês/Húngaro", 10: "Outras"},
    "religion": {0: "Católica", 1: "Outra cristã", 2: "Muçulmana", 3: "Budista",
                 4: "Hindu", 5: "Étnica", 6: "Marxista", 7: "Outras"},
}

st.set_page_config(page_title="Flags — EDA", layout="wide")


# ------------------------------------------------------------------ Dados
@st.cache_data
def get_data():
    df = load_data().drop(columns=["image"], errors="ignore")
    # Discretização: divide os países pela mediana da população
    df["population_category"] = np.where(
        df["population"] <= df["population"].median(), "Baixa (≤ mediana)", "Alta (> mediana)"
    )
    return df


df = get_data()

# landmass, zone, language e religion são códigos categóricos: ficam fora das variáveis numéricas
NUM_VARS = [
    c for c in [
        "area", "population", "colours", "bars", "stripes",
        "circles", "crosses", "saltires", "quarters", "sunstars"
    ]
    if c in df.columns
]

# ------------------------------------------------------------------ Sidebar (filtros do Dashboard 1)
st.sidebar.header("Filtros")
st.sidebar.caption("Valem para a aba Dashboard 1.")

vars_sel = st.sidebar.multiselect(
    "Variáveis",
    NUM_VARS,
    default=[v for v in ["area", "population", "colours", "stripes", "sunstars"] if v in NUM_VARS],
    help="Variáveis que entram nos histogramas, no heatmap e no resumo.",
)

var_int = st.sidebar.selectbox(
    "Variável do intervalo",
    vars_sel or NUM_VARS,
    help="O slider abaixo filtra os países por esta variável.",
)

col_min, col_max = float(df[var_int].min()), float(df[var_int].max())
if col_min < col_max:
    intervalo = st.sidebar.slider(f"Intervalo de {var_int}", col_min, col_max, (col_min, col_max))
else:
    intervalo = (col_min, col_max)
    st.sidebar.caption(f"{var_int} tem valor único ({col_min:g}).")

metodo = st.sidebar.selectbox(
    "Correlação",
    ["spearman", "pearson", "kendall"],
    help="Spearman não exige normalidade, e nenhuma variável quantitativa passou no Shapiro-Wilk.",
)

usar_log = st.sidebar.checkbox("Histogramas em log1p", value=False,
                               help="Reduz a assimetria de area e population.")

nbins = st.sidebar.slider("Nº de bins", 5, 60, 20)


# ------------------------------------------------------------------ Dashboard 1
def dados_para_plot(serie, var):
    """Valores que vão para o histograma (log1p só se pedido e se não houver negativos)."""
    dados = serie.dropna()
    if usar_log and not dados.empty and (dados >= 0).all():
        return np.log1p(dados), f"log1p({var})"
    return dados, var


def dashboard_1():
    st.header("Dashboard 1 — Distribuição e correlação")

    if not vars_sel:
        st.warning("Selecione pelo menos uma variável na barra lateral.")
        return

    df_f = df[df[var_int].between(*intervalo)]

    if df_f.empty:
        st.warning("Nenhum país no intervalo selecionado.")
        return

    # Dados de cada histograma (e a assimetria, na mesma escala em que são plotados)
    plots = {var: dados_para_plot(df_f[var], var) for var in vars_sel}
    assimetrias = {
        var: dados.skew()
        for var, (dados, _) in plots.items()
        if len(dados) > 2 and pd.notna(dados.skew())
    }

    # ---------------------------------------------------------------- KPIs
    k1, k2, k3, k4 = st.columns(4)

    k1.metric("Países no filtro", f"{len(df_f)} de {len(df)}",
              help="Quantos países passaram pelo intervalo escolhido na sidebar.")

    k2.metric("Mediana da população (milhões)", f"{df_f['population'].median():.1f}",
              help="Mediana em vez da média, porque a população tem assimetria muito alta.")

    if assimetrias:
        mais_assimetrica = max(assimetrias, key=lambda v: abs(assimetrias[v]))
        k3.metric("Variável mais assimétrica", mais_assimetrica,
                  delta=f"skew {assimetrias[mais_assimetrica]:.2f}", delta_color="off",
                  help="Entre as variáveis selecionadas, a de maior assimetria (em valor absoluto), "
                       "na escala dos histogramas. Acima de 1 = cauda longa à direita.")
    else:
        k3.metric("Variável mais assimétrica", "—")

    if "mainhue" in df_f.columns:
        freq = df_f["mainhue"].value_counts(normalize=True)
        k4.metric("Cor predominante mais comum", str(freq.index[0]),
                  delta=f"{freq.iloc[0]:.1%} dos países", delta_color="off",
                  help="Moda da coluna mainhue entre os países filtrados.")

    # ---------------------------------------------------------------- Distribuições compactas
    st.subheader("Distribuição das variáveis")

    colunas_por_linha = 3  # até 3 gráficos pequenos por linha

    for i in range(0, len(vars_sel), colunas_por_linha):
        cols = st.columns(colunas_por_linha)

        for j, var in enumerate(vars_sel[i:i + colunas_por_linha]):
            with cols[j]:
                dados_plot, rotulo = plots[var]

                if dados_plot.empty:
                    st.caption(f"{var}: sem dados")
                    continue

                fig = px.histogram(
                    x=dados_plot,
                    nbins=nbins,
                    labels={"x": rotulo, "y": ""},
                    color_discrete_sequence=[LARANJA],
                )
                estilo(fig)
                fig.update_layout(
                    title=dict(text=var, font=dict(size=14)),
                    height=210,
                    margin=dict(l=5, r=5, t=35, b=25),
                    showlegend=False,
                    xaxis=dict(title=None, showticklabels=True, tickfont=dict(size=8), nticks=4),
                    yaxis=dict(title=None, showticklabels=False),
                    bargap=0.08,
                )
                fig.update_traces(hovertemplate="Intervalo: %{x}<br>Países: %{y}<extra></extra>")

                st.plotly_chart(fig, width="stretch", key=f"hist_{var}")

    # ---------------------------------------------------------------- Correlação e resumo
    st.divider()

    c_corr, c_resumo = st.columns([3, 2])

    with c_corr:
        st.subheader("Correlação (heatmap)")

        if len(vars_sel) < 2:
            st.info("Selecione pelo menos 2 variáveis.")
        elif len(df_f) < 3:
            st.warning("Poucos países para calcular a correlação.")
        else:
            corr = df_f[vars_sel].corr(method=metodo)

            # Remove a metade superior da matriz (a matriz é simétrica)
            mascara = np.triu(np.ones(corr.shape, dtype=bool), k=1)
            corr_plot = corr.mask(mascara)

            fig_c = px.imshow(
                corr_plot,
                text_auto=".2f",
                zmin=-1,
                zmax=1,
                color_continuous_scale=ESCALA_DIVERGENTE,
                aspect="auto",
            )
            estilo(fig_c)
            fig_c.update_layout(height=450, margin=dict(l=10, r=10, t=40, b=10))

            st.plotly_chart(fig_c, width="stretch", key="heatmap_correlacao")
            st.caption("Células vazias = metade repetida da matriz, ou variável constante no filtro.")

    with c_resumo:
        st.subheader("Resumo estatístico")
        st.dataframe(df_f[vars_sel].describe().T.round(2), width="stretch")


# ------------------------------------------------------------------ Dashboard 2
GRUPOS = {
    "landmass": "Continente (landmass)",
    "zone": "Zona geográfica (zone)",
    "language": "Idioma (language)",
    "religion": "Religião (religion)",
    "mainhue": "Cor predominante (mainhue)",
    "topleft": "Cor do canto superior esquerdo (topleft)",
    "botright": "Cor do canto inferior direito (botright)",
    "population_category": "População (baixa/alta pela mediana)",
}
GRUPOS = {k: v for k, v in GRUPOS.items() if k in df.columns}

# rótulo -> (coluna, função de agregação); coluna None = contagem de países
METRICAS = {
    "Nº de países": (None, "count"),
    "Mediana da população (milhões)": ("population", "median"),
    "Mediana da área (mil km²)": ("area", "median"),
    "Média de cores na bandeira (colours)": ("colours", "mean"),
}
METRICAS = {k: v for k, v in METRICAS.items() if v[0] is None or v[0] in df.columns}


def dashboard_2():
    st.header("Dashboard 2 — Perfil por grupo")

    # Widgets do Dashboard 2 (ficam na própria aba)
    w1, w2 = st.columns(2)
    grupo = w1.selectbox("Agrupar por", list(GRUPOS), format_func=GRUPOS.get, key="grupo")
    nome_metrica = w2.selectbox("Métrica da barra", list(METRICAS), key="metrica")
    coluna, funcao = METRICAS[nome_metrica]

    # Agrupamento: troca códigos por rótulos legíveis
    rotulo_grupo = df[grupo].map(ROTULOS.get(grupo, {})).fillna(df[grupo].astype(str))
    g = df.assign(grupo=rotulo_grupo)

    contagem = g["grupo"].value_counts()
    valor = contagem if coluna is None else g.groupby("grupo")[coluna].agg(funcao)

    tabela = pd.DataFrame({"Nº de países": contagem, "% dos países": contagem / len(g) * 100})
    if coluna is not None:
        tabela[nome_metrica] = valor
    tabela = tabela.sort_values(nome_metrica if coluna is not None else "Nº de países", ascending=False)
    tabela.index.name = "Grupo"

    # KPIs
    p = contagem / contagem.sum()
    k = len(p)
    balanceamento = float(-(p * np.log(p)).sum() / np.log(k)) if k > 1 else None
    lider = tabela.index[0]
    valor_lider = tabela[nome_metrica if coluna is not None else "Nº de países"].iloc[0]

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Nº de grupos", k,
              help="Quantas categorias a variável escolhida tem.")
    k2.metric("Maior grupo", str(contagem.index[0]),
              delta=f"{p.iloc[0]:.1%} dos países", delta_color="off",
              help="Categoria com mais países.")
    k3.metric("Balanceamento (0 a 1)", f"{balanceamento:.2f}" if balanceamento is not None else "—",
              help="Entropia normalizada. Perto de 0 = um grupo domina. Perto de 1 = grupos parecidos.")
    k4.metric(f"Grupo líder — {nome_metrica}", str(lider),
              delta=f"{valor_lider:,.0f}" if coluna is None else f"{valor_lider:,.1f}", delta_color="off",
              help="Grupo com o maior valor da métrica escolhida.")

    # Gráfico de barras + tabela
    c_bar, c_tab = st.columns([3, 2])
    with c_bar:
        st.subheader(f"{nome_metrica} por {GRUPOS[grupo].split(' (')[0].lower()}")
        dados = tabela.reset_index()
        eixo = nome_metrica if coluna is not None else "Nº de países"
        fig = px.bar(dados, x=eixo, y="Grupo", orientation="h",
                     text_auto=".0f" if coluna is None else ".1f",
                     color_discrete_sequence=[LARANJA])
        fig.update_yaxes(categoryorder="total ascending", title=None)
        st.plotly_chart(estilo(fig), width="stretch")
    with c_tab:
        st.subheader("Tabela do agrupamento")
        st.dataframe(tabela.round(1), width="stretch")


# ------------------------------------------------------------------ Tabs
st.title("Flags — Análise de bandeiras")
aba1, aba2 = st.tabs(["Dashboard 1", "Dashboard 2"])
with aba1:
    dashboard_1()
with aba2:
    dashboard_2()
