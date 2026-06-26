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
        "font.size": 13,
        "axes.titlesize": 15,
        "axes.labelsize": 13,
        "xtick.labelsize": 11,
        "ytick.labelsize": 11,
        "legend.fontsize": 11,
        "figure.facecolor": "white",
        "axes.facecolor": "white",
    })


def plot_boxplot_tempo(df):
    _estilo_grafico()
    fig, ax = plt.subplots(figsize=(7, 4))
    sns.boxplot(data=df, x="tratamento", y="tempo_ms", ax=ax, width=0.5)
    medians = df.groupby("tratamento")["tempo_ms"].median()
    for i, t in enumerate(["REST", "GraphQL"]):
        ax.text(i, medians[t] + 20, f"{medians[t]:.0f} ms",
                ha="center", va="bottom", fontweight="bold", fontsize=12)
    ax.set_title("Boxplot - Tempo de Resposta", fontweight="bold")
    ax.set_ylabel("Tempo (ms)")
    ax.set_xlabel("")
    return fig


def plot_boxplot_bytes(df):
    _estilo_grafico()
    fig, ax = plt.subplots(figsize=(7, 4))
    sns.boxplot(data=df, x="tratamento", y="bytes", ax=ax, width=0.5)
    medians = df.groupby("tratamento")["bytes"].median()
    for i, t in enumerate(["REST", "GraphQL"]):
        ax.text(i, medians[t] + 150, f"{int(medians[t])} B",
                ha="center", va="bottom", fontweight="bold", fontsize=12)
    ax.set_title("Boxplot - Tamanho do Payload", fontweight="bold")
    ax.set_ylabel("Bytes")
    ax.set_xlabel("")
    return fig


def plot_histograma(df):
    _estilo_grafico()
    fig, ax = plt.subplots(figsize=(7, 4))
    for t in ["REST", "GraphQL"]:
        subset = df[df["tratamento"] == t]
        sns.histplot(subset["tempo_ms"], label=t, alpha=0.5, bins=10, ax=ax)
    ax.set_title("Distribuicao do Tempo", fontweight="bold")
    ax.set_xlabel("Tempo (ms)")
    ax.set_ylabel("Frequencia")
    ax.legend()
    return fig


def plot_scatter(df):
    _estilo_grafico()
    fig, ax = plt.subplots(figsize=(7, 4))
    sns.scatterplot(data=df, x="trial_id", y="tempo_ms",
                    hue="tratamento", style="tratamento",
                    s=80, ax=ax)
    ax.set_title("Evolucao Temporal", fontweight="bold")
    ax.set_xlabel("Ordem dos Trials")
    ax.set_ylabel("Tempo (ms)")
    return fig


def card(rotulo, valor, cor=""):
    if cor:
        return f"""
        <div style="background:#f0f2f6;border-radius:8px;padding:12px 16px;text-align:center;
                    border-left:4px solid {cor};margin-bottom:6px;min-width:140px;">
            <div style="font-size:12px;color:#555;">{rotulo}</div>
            <div style="font-size:24px;font-weight:700;color:#111;">{valor}</div>
        </div>
        """
    return f"""
    <div style="background:#f0f2f6;border-radius:8px;padding:12px 16px;text-align:center;margin-bottom:6px;min-width:140px;">
        <div style="font-size:12px;color:#555;">{rotulo}</div>
        <div style="font-size:24px;font-weight:700;color:#111;">{valor}</div>
    </div>
    """


def main():
    st.set_page_config(page_title="GraphQL vs REST", layout="wide", initial_sidebar_state="collapsed")

    df = load_data()
    testes = calc_teste(df)

    rest_t = df[df["tratamento"] == "REST"]["tempo_ms"]
    gql_t = df[df["tratamento"] == "GraphQL"]["tempo_ms"]
    rest_b = df[df["tratamento"] == "REST"]["bytes"]
    gql_b = df[df["tratamento"] == "GraphQL"]["bytes"]

    reducao_t = (rest_t.mean() - gql_t.mean()) / rest_t.mean() * 100
    reducao_b = (rest_b.mean() - gql_b.mean()) / rest_b.mean() * 100

    st.markdown("""
    <style>
        .main > .block-container {
            max-width: none !important;
            padding: 1rem 1.5rem !important;
            overflow-x: auto !important;
            white-space: nowrap !important;
        }
        .row-widget.stHorizontal {
            display: block !important;
            white-space: nowrap !important;
            overflow: visible !important;
            flex-wrap: nowrap !important;
        }
        section[data-testid="stSidebar"] { display: none; }
        div[data-testid="column"] {
            display: inline-block !important;
            vertical-align: top !important;
            min-width: 88vw !important;
            white-space: normal !important;
            margin-right: 1.5rem !important;
            padding: 0.8rem 1rem !important;
            background: #fafafa;
            border-radius: 10px;
            border: 1px solid #eee;
        }
        hr { margin: 0.5rem 0 !important; }
        h1, h2, h3, h4, p { margin-bottom: 0.3rem !important; }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("""
    <span style="font-size:11px;color:#999;">GraphQL vs REST — Experimento Controlado — API do GitHub — N=60 trials — 5 repositorios</span>
    """, unsafe_allow_html=True)

    c_conclusao, c_rq1, c_rq2, c_charts, c_brutos, c_desc = st.columns(6)

    with c_conclusao:
        st.markdown("""
        <div style="margin-top:24px;">
            <h1 style="font-size:28px;font-weight:700;margin-bottom:4px;">GraphQL vs REST</h1>
        </div>
        """, unsafe_allow_html=True)
        st.markdown(f"""
        <div style="background:#1a1a2e;border-radius:10px;padding:18px;text-align:center;">
            <div style="font-size:13px;color:#aaa;margin-bottom:4px;">Conclusao</div>
            <div style="font-size:22px;font-weight:700;color:#fff;">
                {reducao_t:.0f}% mais rapido<br>
                <span style="font-size:14px;color:#ccc;">e</span><br>
                {reducao_b:.1f}% mais eficiente
            </div>
            <div style="font-size:13px;color:#aaa;margin-top:4px;">p &lt; 0,001 em ambos</div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("""
        <div style="background:#eef2f7;border-radius:6px;padding:10px;font-size:14px;color:#333;margin-top:6px;line-height:1.5;">
            <b>Resumo simples:</b> Neste experimento, a tecnologia GraphQL
            foi mais rapida e devolveu dados menores que a tecnologia REST.
            Isso foi confirmado por testes estatisticos (p &lt; 0,001),
            ou seja, a chance disso ter acontecido por acaso e menor que
            0,1%.
        </div>
        """, unsafe_allow_html=True)

    with c_rq1:
        n_t, st_t, p_t = testes["RQ1 (tempo)"]
        st.markdown("""
        <div style="margin-top:16px;">
            <h2 style="font-size:20px;font-weight:600;margin-bottom:8px;">RQ1 — Tempo de Resposta</h2>
        </div>
        """, unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3, gap="small")
        c1.markdown(card("REST (media)", f"{rest_t.mean():.0f} ms"), unsafe_allow_html=True)
        c2.markdown(card("GraphQL (media)", f"{gql_t.mean():.0f} ms", "#2ecc71"), unsafe_allow_html=True)
        c3.markdown(card("Reducao", f"-{reducao_t:.0f}%", "#2ecc71"), unsafe_allow_html=True)
        st.markdown(f"""
        <p style="font-size:13px;color:#444;margin:4px 0;">
            <b>Teste:</b> {n_t} | p = {p_t:.6f} | Rejeita H<sub>0</sub>: {"Sim" if p_t < 0.05 else "Nao"}
        </p>
        """, unsafe_allow_html=True)
        st.pyplot(plot_boxplot_tempo(df))
        st.markdown("""
        <div style="background:#eef2f7;border-radius:6px;padding:8px 10px;font-size:13px;color:#333;margin-top:2px;line-height:1.4;">
            <b>O que mostra:</b> As caixas mostram o tempo que cada tecnologia levou
            para responder. A linha no meio da caixa e a mediana (valor do meio).
            Quanto mais baixa a caixa, mais rapido.<br>
            <b>Leitura:</b> GraphQL (azul) teve caixa mais baixa que REST (laranja).
            Significa que GraphQL respondeu mais rapido na maioria das vezes.
        </div>
        """, unsafe_allow_html=True)

    with c_rq2:
        n_b, st_b, p_b = testes["RQ2 (bytes)"]
        st.markdown("""
        <div style="margin-top:16px;">
            <h2 style="font-size:20px;font-weight:600;margin-bottom:8px;">RQ2 — Tamanho do Payload</h2>
        </div>
        """, unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3, gap="small")
        c1.markdown(card("REST (media)", f"{rest_b.mean():.0f} B"), unsafe_allow_html=True)
        c2.markdown(card("GraphQL (media)", f"{gql_b.mean():.0f} B", "#2ecc71"), unsafe_allow_html=True)
        c3.markdown(card("Reducao", f"-{reducao_b:.1f}%", "#2ecc71"), unsafe_allow_html=True)
        st.markdown(f"""
        <p style="font-size:13px;color:#444;margin:4px 0;">
            <b>Teste:</b> {n_b} | p = {p_b:.6f} | Rejeita H<sub>0</sub>: {"Sim" if p_b < 0.05 else "Nao"}
        </p>
        """, unsafe_allow_html=True)
        st.pyplot(plot_boxplot_bytes(df))
        st.markdown("""
        <div style="background:#eef2f7;border-radius:6px;padding:8px 10px;font-size:13px;color:#333;margin-top:2px;line-height:1.4;">
            <b>O que mostra:</b> O tamanho dos dados que cada tecnologia enviou
            de volta. Medimos em bytes (quanto menor o numero, menor a resposta).<br>
            <b>Leitura:</b> A caixa do GraphQL (azul) aparece praticamente no zero
            porque os dados sao muito pequenos: cerca de 80 bytes, contra 6.000
            bytes do REST. Isso e uma grande diferenca.
        </div>
        """, unsafe_allow_html=True)

    with c_charts:
        st.markdown("""
        <div style="margin-top:16px;">
            <h2 style="font-size:20px;font-weight:600;margin-bottom:8px;">Complementares</h2>
        </div>
        """, unsafe_allow_html=True)
        st.pyplot(plot_histograma(df))
        st.markdown("""
        <div style="background:#eef2f7;border-radius:6px;padding:8px 10px;font-size:13px;color:#333;margin-top:2px;line-height:1.4;">
            <b>O que mostra:</b> Quantas vezes cada tempo de resposta aconteceu.
            Barras mais altas = mais repeticoes daquele valor.<br>
            <b>Leitura:</b> As barras do GraphQL (azul) concentram-se mais a
            esquerda (tempos menores). As do REST (laranja) espalham-se para a
            direita (tempos maiores). Isso confirma que GraphQL e mais rapido.
        </div>
        """, unsafe_allow_html=True)
        st.pyplot(plot_scatter(df))
        st.markdown("""
        <div style="background:#eef2f7;border-radius:6px;padding:8px 10px;font-size:13px;color:#333;margin-top:2px;line-height:1.4;">
            <b>O que mostra:</b> Cada ponto e uma requisicao. A posicao mostra
            em que ordem ela foi feita e quanto tempo levou.<br>
            <b>Leitura:</b> Os pontos azuis (GraphQL) ficam quase sempre abaixo
            dos laranjas (REST) durante todo o experimento. Isso mostra que a
            vantagem do GraphQL foi consistente do inicio ao fim.
        </div>
        """, unsafe_allow_html=True)

    with c_brutos:
        st.markdown("""
        <div style="margin-top:16px;">
            <h2 style="font-size:20px;font-weight:600;margin-bottom:8px;">Dados Brutos</h2>
        </div>
        """, unsafe_allow_html=True)
        st.dataframe(df, use_container_width=True, hide_index=True, height=520)

    with c_desc:
        st.markdown("""
        <div style="margin-top:16px;">
            <h2 style="font-size:20px;font-weight:600;margin-bottom:8px;">Descritivas</h2>
        </div>
        """, unsafe_allow_html=True)
        desc = df.groupby("tratamento")[["tempo_ms", "bytes"]].describe().round(2)
        st.dataframe(desc, use_container_width=True, height=520)


if __name__ == "__main__":
    main()
