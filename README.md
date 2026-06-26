# GraphQL vs REST — Experimento Controlado

## Autores

- Gustavo Pimentel Carvalho Costa
- Érica Alves dos Santos

## Disciplina

Laboratório de Experimentação de Software

## Estrutura

```
src/                     # Scripts de coleta e análise
  api/                   # Clientes REST e GraphQL
  experiment/            # Runner e configuração
  analysis/              # Estatística e dashboard
data/                    # Resultados brutos e processados
  raw/                   # CSVs brutos do experimento
  processed/             # CSVs limpos e resultados dos testes
docs/relatorio/          # Relatório LaTeX e PDF final
  sections/              # Seções individuais do relatório
  figures/               # Gráficos gerados (PNG 300 DPI)
```

## Reprodução

```bash
# 1. Instalar dependências
pip install -r src/analysis/requirements.txt

# 2. Executar coleta (requer GH_TOKEN)
export GH_TOKEN=seu_token_github
python src/experiment/runner.py

# 3. Análise estatística
python src/analysis/stats.py

# 4. Dashboard de gráficos
python src/analysis/dashboard.py

# 5. Compilar relatório (requer LaTeX)
cd docs/relatorio
pdflatex main.tex && bibtex main && pdflatex main.tex && pdflatex main.tex
```

## Resultado

- **PDF final:** `docs/relatorio/relatorio_final.pdf`
- **Dados brutos:** `data/raw/results_*.csv`
- **Dados limpos:** `data/processed/results_clean.csv`
- **Testes estatísticos:** `data/processed/resultado_teste.csv`
- **Gráficos:** `docs/relatorio/figures/*.png`

## Perguntas de Pesquisa

- **RQ1:** GraphQL é mais rápido que REST?
- **RQ2:** GraphQL retorna payloads menores que REST?
