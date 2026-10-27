
import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

from src.data_loader import load_data

st.set_page_config(page_title="Flags — EDA", layout="wide")


@st.cache_data
def get_data():
    df = load_data()
    return df.drop(columns=["image"], errors="ignore")


df = get_data()

NUM_VARS = [
    c for c in [
        "area", "population", "colours", "bars", "stripes",
        "circles", "crosses", "saltires", "quarters", "sunstars"
    ]
    if c in df.columns
]

# ---------------------------------------------------------------- Sidebar
st.sidebar.header("Filtros")

vars_sel = st.sidebar.multiselect(
    "Variáveis",
    NUM_VARS,
    default=[
        v for v in [
            "area", "population", "colours", "stripes", "sunstars"
        ]
        if v in NUM_VARS
    ]
)

metodo = st.sidebar.selectbox(
    "Correlação",
    ["spearman", "pearson", "kendall"]
)

usar_log = st.sidebar.checkbox("Histogramas em log1p", value=False)

nbins = st.sidebar.slider("Nº de bins", 5, 60, 20)

# ---------------------------------------------------------------- Título
st.title("Flags — Distribuição e Correlação")

if not vars_sel:
    st.warning("Selecione pelo menos uma variável na barra lateral.")
    st.stop()

df_f = df.copy()

# ---------------------------------------------------------------- KPIs
k1, k2, k3 = st.columns(3)
k1.metric("Total de países", len(df_f))
k2.metric("Variáveis selecionadas", len(vars_sel))
k3.metric("Método de correlação", metodo.capitalize())

# ---------------------------------------------------------------- Distribuições compactas
st.subheader("Distribuição das variáveis")

# Até 3 gráficos pequenos por linha
colunas_por_linha = 3

for i in range(0, len(vars_sel), colunas_por_linha):
    cols = st.columns(colunas_por_linha)

    for j, var in enumerate(vars_sel[i:i + colunas_por_linha]):
        with cols[j]:
            dados = df_f[var].dropna()

            if dados.empty:
                st.caption(f"{var}: sem dados")
                continue

            if usar_log and (dados >= 0).all():
                dados_plot = np.log1p(dados)
                rotulo = f"log1p({var})"
            else:
                dados_plot = dados
                rotulo = var

            fig = px.histogram(
                x=dados_plot,
                nbins=nbins,
                labels={"x": rotulo, "y": ""},
            )

            fig.update_layout(
                title=dict(text=var, font=dict(size=14)),
                height=210,
                margin=dict(l=5, r=5, t=35, b=25),
                showlegend=False,
                xaxis=dict(
                    title=None,
                    showticklabels=True,
                    tickfont=dict(size=8),
                    nticks=4
                ),
                yaxis=dict(
                    title=None,
                    showticklabels=False
                ),
                bargap=0.08
            )

            fig.update_traces(
                hovertemplate="Intervalo: %{x}<br>Países: %{y}<extra></extra>"
            )

            st.plotly_chart(
                fig,
                width="stretch",
                key=f"hist_{var}"
            )

# ---------------------------------------------------------------- Correlação e resumo
st.divider()

c_corr, c_resumo = st.columns([3, 2])


with c_corr:
    st.subheader("Correlação")

    if len(vars_sel) < 2:
        st.info("Selecione pelo menos 2 variáveis.")

    elif len(df_f) < 3:
        st.warning("Poucos países para calcular a correlação.")

    else:
        corr = df_f[vars_sel].corr(method=metodo)

        # Remove a metade superior da matriz
        mascara = np.triu(
            np.ones(corr.shape, dtype=bool),
            k=1
        )
        corr_plot = corr.mask(mascara)

        fig_c = px.imshow(
            corr_plot,
            text_auto=".2f",
            zmin=-1,
            zmax=1,
            color_continuous_scale="RdBu_r",
            aspect="auto"
        )

        fig_c.update_layout(
            height=450,
            margin=dict(l=10, r=10, t=40, b=10)
        )

        st.plotly_chart(
            fig_c,
            width="stretch",
            key="heatmap_correlacao"
        )

with c_resumo:
    st.subheader("Resumo estatístico")

    st.dataframe(
        df_f[vars_sel].describe().T.round(2),
        width="stretch"
    )
