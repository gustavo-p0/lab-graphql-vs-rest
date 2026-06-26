from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import scipy.stats as stats
import seaborn as sns
import streamlit as st

sns.set_theme(style="whitegrid", palette="colorblind")
palette = sns.color_palette("colorblind")

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
    fig, (ax_rest, ax_gql) = plt.subplots(1, 2, figsize=(8, 4))
    rest = df[df["tratamento"] == "REST"]["bytes"]
    gql = df[df["tratamento"] == "GraphQL"]["bytes"]
    sns.boxplot(y=rest, ax=ax_rest, color=palette[0], width=0.4)
    sns.boxplot(y=gql, ax=ax_gql, color=palette[1], width=0.4)
    ax_rest.set_title("REST", fontweight="bold")
    ax_gql.set_title("GraphQL", fontweight="bold")
    ax_rest.set_ylabel("Bytes")
    ax_gql.set_ylabel("Bytes")
    ax_rest.set_ylim(0, rest.max() * 1.15)
    ax_gql.set_ylim(0, gql.max() * 1.15)
    med_rest = rest.median()
    med_gql = gql.median()
    ax_rest.text(0, med_rest + rest.max() * 0.03, f"{int(med_rest)} B",
                 ha="center", va="bottom", fontweight="bold", fontsize=12)
    ax_gql.text(0, med_gql + gql.max() * 0.03, f"{int(med_gql)} B",
                ha="center", va="bottom", fontweight="bold", fontsize=12)
    fig.suptitle("Boxplot - Tamanho do Payload", fontweight="bold", y=1.02)
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

def fmt_p(p):
    return f"{p:.6f}" if p >= 0.001 else "< 0,001"


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
        section[data-testid="stSidebar"] { display: none; }
        .block-container { max-width: 1200px !important; padding: 4rem 2rem 2rem 2rem !important; }
        h1 { margin-bottom: 0.3rem !important; }
        h2 { margin-top: 0.5rem !important; margin-bottom: 0.5rem !important; }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("""
    <h1 style="font-size:32px;font-weight:700;margin-top:8px;margin-bottom:4px;">GraphQL vs REST &mdash; API do GitHub</h1>
    <p style="font-size:13px;color:#888;margin:0 0 8px 0;">N=60 trials &middot; 5 repositorios</p>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div style="background:#1a1a2e;border-radius:10px;padding:20px;text-align:center;margin:8px 0 20px 0;">
        <span style="font-size:26px;font-weight:700;color:#fff;">GraphQL foi {reducao_t:.0f}% mais rapido</span>
        <span style="font-size:22px;color:#ddd;"> e </span>
        <span style="font-size:26px;font-weight:700;color:#fff;">{reducao_b:.1f}% mais eficiente</span>
        <span style="font-size:22px;color:#ddd;"> que REST (p &lt; 0,001 em ambos)</span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <hr style="margin:0 0 16px 0;">
    <h2 style="font-size:24px;font-weight:600;">RQ1 - Tempo de Resposta</h2>
    <p style="font-size:15px;color:#555;margin:2px 0 12px 0;">
        GraphQL e mais rapido que REST?
        H<sub>0</sub>: tempo medio de GraphQL &ge; REST. &nbsp;
        H<sub>1</sub>: tempo medio de GraphQL &lt; REST.
    </p>
    """, unsafe_allow_html=True)

    n_t, st_t, p_t = testes["RQ1 (tempo)"]

    col_a, col_b, col_c = st.columns(3, gap="small")
    col_a.markdown(card("REST (media)", f"{rest_t.mean():.0f} ms", "#3498db"), unsafe_allow_html=True)
    col_b.markdown(card("GraphQL (media)", f"{gql_t.mean():.0f} ms", "#f1c40f"), unsafe_allow_html=True)
    col_c.markdown(card("Diferenca", f"-{reducao_t:.0f}%", "#2ecc71"), unsafe_allow_html=True)

    st.markdown(f"""
    <p style="font-size:14px;color:#444;">
        <b>Teste:</b> {n_t} | p = {fmt_p(p_t)} | Rejeita H<sub>0</sub>: {"Sim" if p_t < 0.05 else "Nao"}
    </p>
    """, unsafe_allow_html=True)

    st.pyplot(plot_boxplot_tempo(df))

    st.markdown("""
    <div style="background:#eef2f7;border-radius:8px;padding:10px 12px;font-size:14px;color:#333;line-height:1.5;">
        A mediana do GraphQL e 433 ms, a do REST e 608 ms.
        O REST chega a levar ate 1.057 ms, enquanto o GraphQL
        no maximo levou 624 ms. GraphQL foi mais rapido na maioria
        das requisicoes.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <hr style="margin:24px 0 16px 0;">
    <h2 style="font-size:24px;font-weight:600;">RQ2 - Tamanho do Payload</h2>
    <p style="font-size:15px;color:#555;margin:2px 0 12px 0;">
        GraphQL retorna menos dados que REST?
        H<sub>0</sub>: payload medio de GraphQL &ge; REST. &nbsp;
        H<sub>1</sub>: payload medio de GraphQL &lt; REST.
    </p>
    """, unsafe_allow_html=True)

    n_b, st_b, p_b = testes["RQ2 (bytes)"]

    col_a, col_b, col_c = st.columns(3, gap="small")
    col_a.markdown(card("REST (media)", f"{rest_b.mean():.0f} B", "#3498db"), unsafe_allow_html=True)
    col_b.markdown(card("GraphQL (media)", f"{gql_b.mean():.0f} B", "#f1c40f"), unsafe_allow_html=True)
    col_c.markdown(card("Reducao", f"-{reducao_b:.1f}%", "#2ecc71"), unsafe_allow_html=True)

    st.markdown(f"""
    <p style="font-size:14px;color:#444;">
        <b>Teste:</b> {n_b} | p = {fmt_p(p_b)} | Rejeita H<sub>0</sub>: {"Sim" if p_b < 0.05 else "Nao"}
    </p>
    """, unsafe_allow_html=True)

    st.pyplot(plot_boxplot_bytes(df))

    st.markdown("""
    <div style="background:#eef2f7;border-radius:8px;padding:10px 12px;font-size:14px;color:#333;line-height:1.5;">
        A mediana do GraphQL e 82 bytes, a do REST e 6.277 bytes.
        O REST chega a devolver ate 6.822 bytes, enquanto o GraphQL
        no maximo entregou 87 bytes. A diferenca e enorme porque REST
        retorna o objeto completo do repositorio, GraphQL so os tres
        campos pedidos.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <hr style="margin:24px 0 16px 0;">
    <h2 style="font-size:24px;font-weight:600;">Visualizacoes Complementares</h2>
    <p style="font-size:15px;color:#555;margin:2px 0 12px 0;">
        Graficos extras que confirmam a consistencia dos resultados.
    </p>
    """, unsafe_allow_html=True)

    st.pyplot(plot_histograma(df))
    st.markdown("""
    <div style="background:#eef2f7;border-radius:8px;padding:10px 12px;font-size:14px;color:#333;line-height:1.5;">
        Quantas vezes cada tempo de resposta aconteceu. Barras mais altas = mais
        repeticoes. As barras azuis (GraphQL) concentram-se mais a esquerda
        (tempos menores). As laranjas (REST) espalham-se para a direita
        (tempos maiores). Confirma que GraphQL e mais rapido.
    </div>
    """, unsafe_allow_html=True)

    st.pyplot(plot_scatter(df))
    st.markdown("""
    <div style="background:#eef2f7;border-radius:8px;padding:10px 12px;font-size:14px;color:#333;line-height:1.5;">
        Cada ponto e uma requisicao. A posicao mostra a ordem em que foi feita
        e quanto tempo levou. Os pontos azuis (GraphQL) ficam quase sempre
        abaixo dos laranjas (REST) do inicio ao fim. A vantagem do GraphQL
        foi consistente.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <hr style="margin:24px 0 16px 0;">
    <h2 style="font-size:24px;font-weight:600;">Dados Brutos</h2>
    """, unsafe_allow_html=True)
    st.dataframe(df, use_container_width=True, hide_index=True)

    st.markdown("""
    <hr style="margin:24px 0 16px 0;">
    <h2 style="font-size:24px;font-weight:600;">Estatisticas Descritivas Completas</h2>
    """, unsafe_allow_html=True)
    desc = df.groupby("tratamento")[["tempo_ms", "bytes"]].describe().round(2)
    st.dataframe(desc, use_container_width=True)

    st.markdown("""
    <hr style="margin:24px 0 16px 0;">
    <h2 style="font-size:24px;font-weight:600;">Limitacoes do Experimento</h2>
    <div style="background:#fff3cd;border-radius:8px;padding:12px 16px;font-size:14px;color:#856404;line-height:1.5;">
        <ul style="margin:4px 0;padding-left:20px;">
            <li>Testamos apenas a API do GitHub. Outras APIs podem ter comportamentos diferentes.</li>
            <li>60 trials e um numero pequeno. Mais trials aumentariam a confianca nos resultados.</li>
            <li>Medimos somente consultas (GET/query), sem testar criacao ou alteracao de dados.</li>
            <li>O GraphQL pediu apenas 3 campos. Quanto mais campos, menor a economia de payload.</li>
            <li>A latencia da internet varia a cada requisicao e influencia os tempos medidos.</li>
            <li>Usamos 5 repositorios apenas. Mais repositorios dariam maior variedade de dados.</li>
            <li>O experimento foi executado uma unica vez, em horario especifico do dia.</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <hr style="margin:24px 0 16px 0;">
    <p style="font-size:13px;color:#999;text-align:center;">
        GraphQL vs REST - Experimento Controlado - API do GitHub - N=60 trials - 5 repositorios
    </p>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
