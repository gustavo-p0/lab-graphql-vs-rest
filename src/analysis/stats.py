import os

import pandas as pd
from scipy import stats

CLEAN_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "data", "processed", "results_clean.csv")
OUTPUT_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "data", "processed", "resultado_teste.csv")


def load_data(path: str) -> pd.DataFrame:
    return pd.read_csv(path)


def descritivas(df: pd.DataFrame) -> pd.DataFrame:
    return df.groupby("tratamento")["tempo_ms"].describe().round(2)


def testar_normalidade(grupo: pd.Series) -> tuple:
    stat, p = stats.shapiro(grupo)
    return stat, p


def testar_hipotese(grupo_rest: pd.Series, grupo_gql: pd.Series) -> dict:
    _, p_rest = testar_normalidade(grupo_rest)
    _, p_gql = testar_normalidade(grupo_gql)
    normal = p_rest > 0.05 and p_gql > 0.05

    if normal:
        t_stat, p_val = stats.ttest_ind(grupo_gql, grupo_rest, alternative="less")
        teste = "t de Student (bicaudal)"
    else:
        t_stat, p_val = stats.mannwhitneyu(grupo_gql, grupo_rest, alternative="less")
        teste = "Wilcoxon-Mann-Whitney"

    return {
        "teste": teste,
        "estatistica": round(t_stat, 4),
        "p_valor": round(p_val, 6),
        "significativo": p_val < 0.05,
        "shapiro_p_rest": round(p_rest, 6),
        "shapiro_p_gql": round(p_gql, 6),
        "normal": normal,
    }


def main():
    df = load_data(CLEAN_PATH)

    desc = descritivas(df)
    print("=== Estatísticas Descritivas (tempo_ms) ===")
    print(desc)

    rest_tempo = df[df["tratamento"] == "REST"]["tempo_ms"]
    gql_tempo = df[df["tratamento"] == "GraphQL"]["tempo_ms"]

    resultado_rq1 = testar_hipotese(rest_tempo, gql_tempo)
    print(f"\n=== RQ1 - Teste: {resultado_rq1['teste']} ===")
    print(f"Estatística: {resultado_rq1['estatistica']}")
    print(f"p-valor: {resultado_rq1['p_valor']}")
    print(f"Significativo (α=0.05): {resultado_rq1['significativo']}")

    rest_bytes = df[df["tratamento"] == "REST"]["bytes"]
    gql_bytes = df[df["tratamento"] == "GraphQL"]["bytes"]

    resultado_rq2 = testar_hipotese(rest_bytes, gql_bytes)
    print(f"\n=== RQ2 - Teste: {resultado_rq2['teste']} ===")
    print(f"Estatística: {resultado_rq2['estatistica']}")
    print(f"p-valor: {resultado_rq2['p_valor']}")
    print(f"Significativo (α=0.05): {resultado_rq2['significativo']}")

    pd.DataFrame([resultado_rq1, resultado_rq2]).to_csv(OUTPUT_PATH, index=False)
    print(f"\nResultados salvos em {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
