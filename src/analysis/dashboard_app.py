from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import scipy.stats as stats
import seaborn as sns
import streamlit as st

sns.set_theme(style="whitegrid", palette="colorblind")

CLEAN_PATH = Path(__file__).resolve().parents[2] / "data" / "processed" / "results_clean.csv"


@st.cache_data
def load_data():
    return pd.read_csv(CLEAN_PATH)


def calc_teste(df):
    def testar(grupo_rest, grupo_gql):
        _, p_rest = stats.shapiro(grupo_rest)
        _, p_gql = stats.shapiro(grupo_gql)
        normal = p_rest > 0.05 and p_gql > 0.05
        if normal:
            t_stat, p_val = stats.ttest_ind(grupo_gql, grupo_rest, alternative="less")
            nome = "t de Student (unicaudal)"
        else:
            t_stat, p_val = stats.mannwhitneyu(grupo_gql, grupo_rest, alternative="less")
            nome = "Wilcoxon-Mann-Whitney (unicaudal)"
        return nome, round(t_stat, 2), p_val

    rest_t = df[df["tratamento"] == "REST"]["tempo_ms"]
    gql_t = df[df["tratamento"] == "GraphQL"]["tempo_ms"]
    rest_b = df[df["tratamento"] == "REST"]["bytes"]
    gql_b = df[df["tratamento"] == "GraphQL"]["bytes"]

    return {
        "RQ1 (tempo)": testar(rest_t, gql_t),
        "RQ2 (bytes)": testar(rest_b, gql_b),
    }


def _estilo_grafico():
    plt.rcParams.update({
        "font.size": 14,
        "axes.titlesize": 16,
        "axes.labelsize": 14,
        "xtick.labelsize": 12,
        "ytick.labelsize": 12,
        "legend.fontsize": 12,
        "figure.facecolor": "white",
        "axes.facecolor": "white",
    })


def plot_boxplot_tempo(df):
    _estilo_grafico()
    fig, ax = plt.subplots(figsize=(7.5, 4.5))
    sns.boxplot(data=df, x="tratamento", y="tempo_ms", ax=ax, width=0.5)
    medians = df.groupby("tratamento")["tempo_ms"].median()
    for i, t in enumerate(["REST", "GraphQL"]):
        ax.text(i, medians[t] + 20, f"{medians[t]:.0f} ms",
                ha="center", va="bottom", fontweight="bold", fontsize=13)
    ax.set_title("Tempo de Resposta", fontweight="bold")
    ax.set_ylabel("Tempo (ms)")
    ax.set_xlabel("")
    return fig


def plot_boxplot_bytes(df):
    _estilo_grafico()
    fig, ax = plt.subplots(figsize=(7.5, 4.5))
    sns.boxplot(data=df, x="tratamento", y="bytes", ax=ax, width=0.5)
    medians = df.groupby("tratamento")["bytes"].median()
    for i, t in enumerate(["REST", "GraphQL"]):
        ax.text(i, medians[t] + 150, f"{int(medians[t])} B",
                ha="center", va="bottom", fontweight="bold", fontsize=13)
    ax.set_title("Tamanho do Payload", fontweight="bold")
    ax.set_ylabel("Bytes")
    ax.set_xlabel("")
    return fig


def plot_histograma(df):
    _estilo_grafico()
    fig, ax = plt.subplots(figsize=(7.5, 4.5))
    for t in ["REST", "GraphQL"]:
        subset = df[df["tratamento"] == t]
        sns.histplot(subset["tempo_ms"], label=t, alpha=0.5, bins=10, ax=ax)
    ax.set_title("Distribuicao do Tempo de Resposta", fontweight="bold")
    ax.set_xlabel("Tempo (ms)")
    ax.set_ylabel("Frequencia")
    ax.legend()
    return fig


def plot_scatter(df):
    _estilo_grafico()
    fig, ax = plt.subplots(figsize=(7.5, 4.5))
    sns.scatterplot(data=df, x="trial_id", y="tempo_ms",
                    hue="tratamento", style="tratamento",
                    s=80, ax=ax)
    ax.set_title("Tempo de Resposta por Trial", fontweight="bold")
    ax.set_xlabel("Trial")
    ax.set_ylabel("Tempo (ms)")
    return fig


def card_valor(rotulo, valor, destaque=""):
    if destaque:
        return f"""
        <div style="background:#f0f2f6;border-radius:10px;padding:16px;text-align:center;
                    border-left:4px solid {destaque};margin-bottom:8px;">
            <div style="font-size:14px;color:#555;margin-bottom:4px;">{rotulo}</div>
            <div style="font-size:28px;font-weight:700;color:#111;">{valor}</div>
        </div>
        """
    return f"""
    <div style="background:#f0f2f6;border-radius:10px;padding:16px;text-align:center;margin-bottom:8px;">
        <div style="font-size:14px;color:#555;margin-bottom:4px;">{rotulo}</div>
        <div style="font-size:28px;font-weight:700;color:#111;">{valor}</div>
    </div>
    """


def main():
    st.set_page_config(page_title="GraphQL vs REST", layout="wide")

    df = load_data()
    testes = calc_teste(df)

    rest_t = df[df["tratamento"] == "REST"]["tempo_ms"]
    gql_t = df[df["tratamento"] == "GraphQL"]["tempo_ms"]
    rest_b = df[df["tratamento"] == "REST"]["bytes"]
    gql_b = df[df["tratamento"] == "GraphQL"]["bytes"]

    reducao_t = (rest_t.mean() - gql_t.mean()) / rest_t.mean() * 100
    reducao_b = (rest_b.mean() - gql_b.mean()) / rest_b.mean() * 100
    p_t = testes["RQ1 (tempo)"][2]
    p_b = testes["RQ2 (bytes)"][2]

    st.markdown("""
    <h1 style="font-size:32px;margin-bottom:4px;">GraphQL vs REST</h1>
    <p style="font-size:16px;color:#666;margin-top:0;">
        Experimento controlado &mdash; API do GitHub &mdash;
        N = 60 trials (30 por tratamento) &mdash; 5 repositorios
    </p>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div style="background:#1a1a2e;border-radius:12px;padding:20px;text-align:center;margin:12px 0 20px 0;">
        <span style="font-size:22px;color:#e0e0e0;">Conclusao: </span>
        <span style="font-size:24px;font-weight:700;color:#ffffff;">
            GraphQL foi {reducao_t:.0f}% mais rapido
        </span>
        <span style="font-size:22px;color:#e0e0e0;"> e </span>
        <span style="font-size:24px;font-weight:700;color:#ffffff;">
            {reducao_b:.1f}% mais eficiente
        </span>
        <span style="font-size:22px;color:#e0e0e0;"> que REST (p &lt; 0,001 em ambos)</span>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        <h2 style="font-size:22px;font-weight:600;margin-bottom:8px;">
            RQ1 - Tempo de Resposta
        </h2>
        """, unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        c1.markdown(card_valor("REST (media)", f"{rest_t.mean():.0f} ms"), unsafe_allow_html=True)
        c2.markdown(card_valor("GraphQL (media)", f"{gql_t.mean():.0f} ms",
                               destaque="#2ecc71"), unsafe_allow_html=True)
        c3.markdown(card_valor("p-valor", f"{p_t:.6f}" if p_t >= 0.001 else "< 0,001"),
                    unsafe_allow_html=True)
        st.markdown(f"""
        <p style="font-size:15px;color:#555;margin:-4px 0 8px 0;">
            Teste: {testes["RQ1 (tempo)"][0]} | Estatistica: {testes["RQ1 (tempo)"][1]} |
            Rejeita H<sub>0</sub>: {"Sim" if p_t < 0.05 else "Nao"}
        </p>
        """, unsafe_allow_html=True)
        st.pyplot(plot_boxplot_tempo(df))

    with col2:
        st.markdown("""
        <h2 style="font-size:22px;font-weight:600;margin-bottom:8px;">
            RQ2 - Tamanho do Payload
        </h2>
        """, unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        c1.markdown(card_valor("REST (media)", f"{rest_b.mean():.0f} B"), unsafe_allow_html=True)
        c2.markdown(card_valor("GraphQL (media)", f"{gql_b.mean():.0f} B",
                               destaque="#2ecc71"), unsafe_allow_html=True)
        c3.markdown(card_valor("p-valor", f"{p_b:.6f}" if p_b >= 0.001 else "< 0,001"),
                    unsafe_allow_html=True)
        st.markdown(f"""
        <p style="font-size:15px;color:#555;margin:-4px 0 8px 0;">
            Teste: {testes["RQ2 (bytes)"][0]} | Estatistica: {testes["RQ2 (bytes)"][1]} |
            Rejeita H<sub>0</sub>: {"Sim" if p_b < 0.001 else "Nao"}
        </p>
        """, unsafe_allow_html=True)
        st.pyplot(plot_boxplot_bytes(df))

    st.markdown("""
    <hr style="margin:24px 0 16px 0;">
    <h2 style="font-size:22px;font-weight:600;margin-bottom:12px;">
        Visualizacoes Complementares
    </h2>
    """, unsafe_allow_html=True)

    g1, g2 = st.columns(2)
    with g1:
        st.pyplot(plot_histograma(df))
    with g2:
        st.pyplot(plot_scatter(df))

    st.markdown("""
    <hr style="margin:24px 0 16px 0;">
    <h2 style="font-size:22px;font-weight:600;margin-bottom:12px;">
        Dados Brutos
    </h2>
    """, unsafe_allow_html=True)
    st.dataframe(df, use_container_width=True, hide_index=True)

    st.markdown("""
    <hr style="margin:24px 0 16px 0;">
    <h2 style="font-size:22px;font-weight:600;margin-bottom:12px;">
        Estatisticas Descritivas Completas
    </h2>
    """, unsafe_allow_html=True)
    desc = df.groupby("tratamento")[["tempo_ms", "bytes"]].describe().round(2)
    st.dataframe(desc, use_container_width=True)


if __name__ == "__main__":
    main()
