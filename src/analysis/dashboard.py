import os

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

sns.set_theme(style="whitegrid", palette="colorblind")
palette = sns.color_palette("colorblind")
assert len(palette) >= 4, f"Paleta colorblind possui {len(palette)} cores, necessario >= 4"

CLEAN_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "data", "processed", "results_clean.csv")
FIGURES_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "docs", "relatorio", "figures")


def load_data(path: str) -> pd.DataFrame:
    return pd.read_csv(path)


def save_fig(name: str):
    os.makedirs(FIGURES_DIR, exist_ok=True)
    path = os.path.join(FIGURES_DIR, name)
    plt.savefig(path, dpi=300, bbox_inches="tight")
    print(f"Saved {path}")
    plt.close()


def boxplot_tempo(df: pd.DataFrame):
    plt.figure(figsize=(8, 5))
    sns.boxplot(data=df, x="tratamento", y="tempo_ms")
    plt.title("Tempo de Resposta por Tratamento")
    plt.ylabel("Tempo (ms)")
    save_fig("boxplot_tempo.png")


def boxplot_bytes(df: pd.DataFrame):
    fig, (ax_rest, ax_gql) = plt.subplots(1, 2, figsize=(8, 4), gridspec_kw={"wspace": 0.4})
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
    ax_rest.text(0, ax_rest.get_ylim()[1] * 0.88, f"{int(med_rest)}",
                 ha="center", va="top", fontweight="bold", fontsize=12, color="#333")
    ax_gql.text(0, ax_gql.get_ylim()[1] * 0.88, f"{int(med_gql)}",
                ha="center", va="top", fontweight="bold", fontsize=12, color="#333")
    fig.suptitle("Tamanho da Resposta por Tratamento", fontweight="bold", y=1.02)
    save_fig("boxplot_bytes.png")


def histograma_tempo(df: pd.DataFrame):
    plt.figure(figsize=(8, 5))
    for tratamento in ["REST", "GraphQL"]:
        subset = df[df["tratamento"] == tratamento]
        sns.histplot(subset["tempo_ms"], label=tratamento, alpha=0.5, bins=10)
    plt.title("Distribuição do Tempo de Resposta")
    plt.xlabel("Tempo (ms)")
    plt.legend()
    save_fig("histograma_tempo.png")


def scatter_tempo(df: pd.DataFrame):
    plt.figure(figsize=(8, 5))
    sns.scatterplot(data=df, x="trial_id", y="tempo_ms", hue="tratamento", style="tratamento")
    plt.title("Tempo de Resposta por Trial")
    plt.xlabel("Trial ID")
    plt.ylabel("Tempo (ms)")
    save_fig("scatter_tempo.png")


def main():
    df = load_data(CLEAN_PATH)
    boxplot_tempo(df)
    boxplot_bytes(df)
    histograma_tempo(df)
    scatter_tempo(df)
    print("All figures generated.")


if __name__ == "__main__":
    main()
