import time

import requests


def fetch_rest(url: str, params: dict | None = None, headers: dict | None = None, timeout: int = 30) -> tuple:
    start = time.perf_counter()
    resp = requests.get(url, params=params, headers=headers, timeout=timeout)
    elapsed = (time.perf_counter() - start) * 1000
    return elapsed, len(resp.content), resp.status_code
