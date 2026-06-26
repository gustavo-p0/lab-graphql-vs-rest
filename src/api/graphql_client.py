import time
from typing import Optional

import requests


def fetch_graphql(url: str, query: str, variables: Optional[dict] = None, headers: Optional[dict] = None, timeout: int = 30) -> tuple:
    start = time.perf_counter()
    resp = requests.post(url, json={"query": query, "variables": variables}, headers=headers, timeout=timeout)
    elapsed = (time.perf_counter() - start) * 1000
    return elapsed, len(resp.content), resp.status_code
