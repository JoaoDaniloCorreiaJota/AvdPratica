import numpy as np
import plotly.express as px
import streamlit as st

from src.data_loader import load_data  # ajuste o nome se a função tiver outro nome

st.set_page_config(page_title="Flags — EDA", layout="wide")


@st.cache_data
def get_data():
    df = load_data()
    return df.drop(columns=["image"], errors="ignore")


df = get_data()

# Variáveis realmente numéricas (landmass, zone, language e religion são códigos categóricos)
NUM_VARS = [
    c for c in ["area", "population", "colours", "bars", "stripes",
                "circles", "crosses", "saltires", "quarters", "sunstars"]
    if c in df.columns
]

# ---------------------------------------------------------------- Sidebar
st.sidebar.header("Filtros")

vars_sel = st.sidebar.multiselect(
    "Variáveis", NUM_VARS,
    default=[v for v in ["area", "population", "colours", "stripes", "sunstars"] if v in NUM_VARS],
)

var_hist = st.sidebar.selectbox("Variável do histograma e do intervalo", vars_sel or NUM_VARS)

col_min, col_max = float(df[var_hist].min()), float(df[var_hist].max())
if col_min < col_max:
    intervalo = st.sidebar.slider(f"Intervalo de {var_hist}", col_min, col_max, (col_min, col_max))
else:
    intervalo = (col_min, col_max)
    st.sidebar.caption(f"{var_hist} tem valor único ({col_min:g}).")

metodo = st.sidebar.selectbox("Correlação", ["spearman", "pearson", "kendall"])
usar_log = st.sidebar.checkbox("Histograma em log1p", value=False)
nbins = st.sidebar.slider("Nº de bins", 5, 60, 20)

# ---------------------------------------------------------------- Filtragem
df_f = df[df[var_hist].between(*intervalo)]

st.title("Flags — Distribuição e Correlação")

if df_f.empty:
    st.warning("Nenhum país no intervalo selecionado.")
    st.stop()

x = np.log1p(df_f[var_hist]) if usar_log else df_f[var_hist]
rotulo_x = f"log1p({var_hist})" if usar_log else var_hist

# ---------------------------------------------------------------- Linha 1: KPIs
k1, k2, k3 = st.columns(3)
k1.metric("Países no filtro", f"{len(df_f)} de {len(df)}")
k2.metric("Assimetria (skew)", f"{x.skew():.2f}" if len(df_f) > 2 else "—")
k3.metric("Média / Mediana", f"{x.mean():.2f} / {x.median():.2f}")

# ---------------------------------------------------------------- Linha 2: histograma (largura total)
st.subheader(f"Distribuição (histograma) — {rotulo_x}")
fig_h = px.histogram(x=x, nbins=nbins, marginal="box", labels={"x": rotulo_x})
fig_h.update_layout(yaxis_title="Nº de países", bargap=0.05)
st.plotly_chart(fig_h, width="stretch")

# ---------------------------------------------------------------- Linha 3: heatmap + resumo
c_corr, c_resumo = st.columns([3, 2])

with c_corr:
    st.subheader("Correlação (heatmap)")
    if len(vars_sel) < 2:
        st.info("Selecione ao menos 2 variáveis na sidebar.")
    elif len(df_f) < 3:
        st.warning("Poucos países no intervalo para calcular correlação.")
    else:
        corr = df_f[vars_sel].corr(method=metodo)
        fig_c = px.imshow(corr, text_auto=".2f", zmin=-1, zmax=1,
                          color_continuous_scale="RdBu_r", aspect="auto")
        st.plotly_chart(fig_c, width="stretch")
        st.caption("Células vazias = variável constante no intervalo filtrado.")

with c_resumo:
    st.subheader("Resumo")
    cols_resumo = vars_sel or [var_hist]
    st.dataframe(df_f[cols_resumo].describe().T.round(2), width="stretch")
