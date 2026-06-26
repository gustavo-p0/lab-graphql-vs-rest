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
    fig, (ax_topo, ax_base) = plt.subplots(
        2, 1, figsize=(8, 5), sharex=True,
        gridspec_kw={"height_ratios": [1, 3]}
    )
    for ax in (ax_topo, ax_base):
        sns.boxplot(data=df, x="tratamento", y="bytes", ax=ax, width=0.5)

    ax_topo.set_ylim(6000, 6900)
    ax_base.set_ylim(0, 200)

    ax_topo.spines.bottom.set_visible(False)
    ax_base.spines.top.set_visible(False)
    ax_topo.xaxis.tick_top()
    ax_topo.tick_params(labeltop=False, length=0)
    ax_base.xaxis.tick_bottom()

    d = 6
    kwargs = dict(marker=[(-1, -d), (1, d)], markersize=8,
                  linestyle="none", color="dimgray", mec="dimgray", mew=1.2, clip_on=False)
    ax_topo.plot([0, 1], [0, 0], transform=ax_topo.transAxes, **kwargs)
    ax_base.plot([0, 1], [1, 1], transform=ax_base.transAxes, **kwargs)

    medians = df.groupby("tratamento")["bytes"].median()
    ax_base.text(0, medians["REST"] + 50, f"{int(medians['REST'])}",
                 ha="center", va="bottom", fontweight="bold", fontsize=12)
    ax_base.text(1, medians["GraphQL"] + 8, f"{int(medians['GraphQL'])}",
                 ha="center", va="bottom", fontweight="bold", fontsize=12)

    fig.suptitle("Tamanho da Resposta por Tratamento", fontweight="bold", y=0.94)
    ax_base.set_ylabel("Bytes")
    ax_topo.set_ylabel("Bytes (zoom)")
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
