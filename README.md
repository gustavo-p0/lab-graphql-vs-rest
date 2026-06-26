# GraphQL vs REST — Experimento Controlado

Comparação entre APIs GraphQL e REST quanto a tempo de resposta e tamanho de payload.
Disciplina: **Laboratório de Experimentação de Software**.

## Autores

- Gustavo Pimentel Carvalho Costa
- Érica Alves dos Santos

## Resultados

| Métrica | REST | GraphQL | Diferença |
|---|---|---|---|---|
| Tempo médio | 651,58 ms | 462,76 ms | GraphQL **29% mais rápido** |
| Payload médio | 6337 B | 83 B | GraphQL **98,7% menor** |

**RQ1 (Tempo):** GraphQL foi significativamente mais rápido (Wilcoxon-Mann-Whitney, p < 0,001).  
**RQ2 (Payload):** GraphQL retorna significativamente menos dados (Wilcoxon-Mann-Whitney, p < 0,001).

## Estrutura

```
src/
  api/             Clientes REST (rest_client.py) e GraphQL (graphql_client.py)
  experiment/      Runner (runner.py) e configuração (config.yaml)
  analysis/        Estatística (stats.py), dashboard (dashboard.py), requirements.txt
data/
  raw/             CSVs brutos do experimento + log de execução
  processed/       CSVs limpos e resultado dos testes
docs/relatorio/
  sections/        9 seções LaTeX
  figures/         4 gráficos PNG 300 DPI
  main.tex         Documento principal
  relatorio_final.pdf  PDF compilado
```

## Reprodução

```bash
# 1. Instalar dependências
pip install -r src/analysis/requirements.txt

# 2. Coleta de dados (requer token GitHub com acesso a repositórios públicos)
export GH_TOKEN=seu_token_github
PYTHONPATH=. python3 src/experiment/runner.py

# 3. Análise estatística
PYTHONPATH=. python3 src/analysis/stats.py

# 4. Dashboard (4 gráficos)
PYTHONPATH=. python3 src/analysis/dashboard.py

# 5. Dashboard interativo Streamlit
PYTHONPATH=. streamlit run src/analysis/dashboard_app.py

# 6. Compilar PDF (requer LaTeX com pdflatex e bibtex)
cd docs/relatorio
pdflatex main.tex && bibtex main && pdflatex main.tex && pdflatex main.tex
```

> Nota: `PYTHONPATH=.` é necessário no Python 3.9 para resolver imports relativos ao projeto.

## Artefatos

| Arquivo | Descrição |
|---|---|
| `data/raw/results_*.csv` | Dados brutos (30 REST + 30 GraphQL) |
| `data/raw/execution_*.log` | Log de execução do runner |
| `data/processed/results_clean.csv` | Dados limpos (sem trials inválidos) |
| `data/processed/resultado_teste.csv` | p-valor, estatística e decisão |
| `docs/relatorio/figures/*.png` | Boxplots, histograma e scatter |
| `docs/relatorio/relatorio_final.pdf` | Relatório final (9 páginas) |
| `src/analysis/dashboard_app.py` | Dashboard interativo Streamlit |

## Tags

- `v1.0-entrega` — Versão final entregue
