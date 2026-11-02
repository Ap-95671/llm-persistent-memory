from __future__ import annotations

from time import perf_counter

import requests


class OllamaLLM:
    def __init__(self, base_url: str, model: str, system_prompt: str, options: dict):
        self.base_url, self.model, self.system_prompt, self.options = base_url.rstrip("/"), model, system_prompt, options

    def check(self) -> dict:
        response = requests.get(f"{self.base_url}/api/tags", timeout=10)
        response.raise_for_status()
        return response.json()

    def generate(self, prompt: str) -> tuple[str, float, dict]:
        start = perf_counter()
        response = requests.post(f"{self.base_url}/api/generate", json={"model":self.model,"system":self.system_prompt,"prompt":prompt,"stream":False,"options":self.options,"keep_alive":"30m"}, timeout=600)
        response.raise_for_status(); payload = response.json()
        return payload.get("response", "").strip(), (perf_counter()-start)*1000, payload

