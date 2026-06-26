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
    plt.figure(figsize=(8, 5))
    sns.boxplot(data=df, x="tratamento", y="bytes")
    plt.title("Tamanho da Resposta por Tratamento")
    plt.ylabel("Bytes")
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
