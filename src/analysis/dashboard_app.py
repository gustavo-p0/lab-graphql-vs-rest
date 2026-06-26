import os
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import scipy.stats as stats
import seaborn as sns
import streamlit as st

sns.set_theme(style="whitegrid", palette="colorblind")

CLEAN_PATH = Path(__file__).resolve().parents[2] / "data" / "processed" / "results_clean.csv"
RESULTADO_TESTE_PATH = Path(__file__).resolve().parents[2] / "data" / "processed" / "resultado_teste.csv"


@st.cache_data
def load_data():
    return pd.read_csv(CLEAN_PATH)


@st.cache_data
def load_resultados():
    return pd.read_csv(RESULTADO_TESTE_PATH)


def calc_metricas(df):
    return df.groupby("tratamento")[["tempo_ms", "bytes"]].describe().round(2)


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
        return nome, t_stat, p_val

    rest_t = df[df["tratamento"] == "REST"]["tempo_ms"]
    gql_t = df[df["tratamento"] == "GraphQL"]["tempo_ms"]
    rest_b = df[df["tratamento"] == "REST"]["bytes"]
    gql_b = df[df["tratamento"] == "GraphQL"]["bytes"]

    return {
        "RQ1 (tempo)": testar(rest_t, gql_t),
        "RQ2 (bytes)": testar(rest_b, gql_b),
    }


def plot_boxplot_tempo(df):
    fig, ax = plt.subplots(figsize=(8, 5))
    sns.boxplot(data=df, x="tratamento", y="tempo_ms", ax=ax)
    medians = df.groupby("tratamento")["tempo_ms"].median()
    for i, t in enumerate(["REST", "GraphQL"]):
        ax.text(i, medians[t], f"{medians[t]:.0f}", ha="center", va="bottom", fontweight="bold")
    ax.set_title("Tempo de Resposta por Tratamento")
    ax.set_ylabel("Tempo (ms)")
    return fig


def plot_boxplot_bytes(df):
    fig, ax = plt.subplots(figsize=(8, 5))
    sns.boxplot(data=df, x="tratamento", y="bytes", ax=ax)
    medians = df.groupby("tratamento")["bytes"].median()
    for i, t in enumerate(["REST", "GraphQL"]):
        ax.text(i, medians[t], f"{int(medians[t])}", ha="center", va="bottom", fontweight="bold")
    ax.set_title("Tamanho da Resposta por Tratamento")
    ax.set_ylabel("Bytes")
    return fig


def plot_scatter(df):
    fig, ax = plt.subplots(figsize=(8, 5))
    sns.scatterplot(data=df, x="trial_id", y="tempo_ms", hue="tratamento", style="tratamento", ax=ax)
    ax.set_title("Tempo de Resposta por Trial")
    ax.set_xlabel("Trial ID")
    ax.set_ylabel("Tempo (ms)")
    return fig


def plot_histograma(df):
    fig, ax = plt.subplots(figsize=(8, 5))
    for t in ["REST", "GraphQL"]:
        subset = df[df["tratamento"] == t]
        sns.histplot(subset["tempo_ms"], label=t, alpha=0.5, bins=10, ax=ax)
    ax.set_title("Distribuição do Tempo de Resposta")
    ax.set_xlabel("Tempo (ms)")
    ax.legend()
    return fig


def main():
    st.set_page_config(
        page_title="GraphQL vs REST — Dashboard",
        layout="wide",
    )
    st.title("⚡ GraphQL vs REST")
    st.markdown("Dashboard interativo do experimento controlado — API do GitHub")

    df = load_data()
    metricas = calc_metricas(df)
    testes = calc_teste(df)

    rest_mean_t = df[df["tratamento"] == "REST"]["tempo_ms"].mean()
    gql_mean_t = df[df["tratamento"] == "GraphQL"]["tempo_ms"].mean()
    reducao_t = (rest_mean_t - gql_mean_t) / rest_mean_t * 100

    rest_mean_b = df[df["tratamento"] == "REST"]["bytes"].mean()
    gql_mean_b = df[df["tratamento"] == "GraphQL"]["bytes"].mean()
    reducao_b = (rest_mean_b - gql_mean_b) / rest_mean_b * 100

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("REST — Tempo médio", f"{rest_mean_t:.0f} ms")
    col2.metric("GraphQL — Tempo médio", f"{gql_mean_t:.0f} ms", delta=f"-{reducao_t:.0f}%")
    col3.metric("REST — Payload médio", f"{rest_mean_b:.0f} B")
    col4.metric("GraphQL — Payload médio", f"{gql_mean_b:.0f} B", delta=f"-{reducao_b:.1f}%")

    st.divider()

    col_a, col_b = st.columns([1, 1])

    with col_a:
        nome_t, stat_t, p_t = testes["RQ1 (tempo)"]
        st.subheader("📊 RQ1 — Tempo de Resposta")
        st.markdown(
            f"""
            **Teste:** {nome_t}  
            **Estatística:** {stat_t:.1f}  
            **p-valor:** {p_t:.6f}  
            **Rejeita H₀:** {"✅ Sim" if p_t < 0.05 else "❌ Não"}
            """
        )

    with col_b:
        nome_b, stat_b, p_b = testes["RQ2 (bytes)"]
        st.subheader("📦 RQ2 — Tamanho do Payload")
        st.markdown(
            f"""
            **Teste:** {nome_b}  
            **Estatística:** {stat_b:.1f}  
            **p-valor:** {p_b:.6f}  
            **Rejeita H₀:** {"✅ Sim" if p_b < 0.05 else "❌ Não"}
            """
        )

    st.divider()

    aba1, aba2, aba3, aba4 = st.tabs(["Boxplot — Tempo", "Boxplot — Bytes", "Distribuição", "Série Temporal"])

    with aba1:
        st.pyplot(plot_boxplot_tempo(df))

    with aba2:
        st.pyplot(plot_boxplot_bytes(df))

    with aba3:
        st.pyplot(plot_histograma(df))

    with aba4:
        st.pyplot(plot_scatter(df))

    st.divider()

    with st.expander("📋 Dados Brutos"):
        st.dataframe(df, use_container_width=True)

    with st.expander("📈 Estatísticas Descritivas"):
        st.dataframe(metricas, use_container_width=True)


if __name__ == "__main__":
    main()
