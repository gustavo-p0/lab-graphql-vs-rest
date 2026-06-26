import csv
import os
import random
import time
from datetime import datetime, timezone

import yaml

from src.api.graphql_client import fetch_graphql
from src.api.rest_client import fetch_rest

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config.yaml")
RAW_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "data", "raw")


def load_config(path: str) -> dict:
    with open(path) as f:
        return yaml.safe_load(f)


def build_rest_url(owner: str, name: str) -> str:
    return f"https://api.github.com/repos/{owner}/{name}"


def build_graphql_query(owner: str, name: str) -> str:
    return f'{{ repository(owner: "{owner}", name: "{name}") {{ name stargazerCount forkCount }} }}'


def run_trials(config: dict) -> list[dict]:
    n = config["n_trials"]
    interval = config["interval_sec"]
    gh_token = os.environ.get("GH_TOKEN")
    if not gh_token:
        raise ValueError("GH_TOKEN environment variable not set")

    results = []

    for i in range(n):
        repo = random.choice(config["repos"])
        owner, name = repo.split("/")

        if i % 2 == 0:
            tratamento = "REST"
            tempo_ms, tamanho_bytes, status = fetch_rest(
                build_rest_url(owner, name),
                headers={"Authorization": f"token {gh_token}"},
            )
        else:
            tratamento = "GraphQL"
            tempo_ms, tamanho_bytes, status = fetch_graphql(
                config["graphql_url"],
                build_graphql_query(owner, name),
                headers={"Authorization": f"token {gh_token}"},
            )
        trial_id = i + 1

        results.append({
            "trial_id": trial_id,
            "tratamento": tratamento,
            "tempo_ms": round(tempo_ms, 2),
            "bytes": tamanho_bytes,
            "status_code": status,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })

        time.sleep(interval)

    return results


def save_results(results: list[dict], output_dir: str) -> str:
    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    path = os.path.join(output_dir, f"results_{timestamp}.csv")
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=results[0].keys())
        writer.writeheader()
        writer.writerows(results)
    return path


def main():
    config = load_config(CONFIG_PATH)
    print(f"Running {config['n_trials']} trials...")
    results = run_trials(config)
    path = save_results(results, RAW_DIR)
    print(f"Results saved to {path}")


if __name__ == "__main__":
    main()
