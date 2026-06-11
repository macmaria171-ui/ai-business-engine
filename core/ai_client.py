import os, json, time, requests, random
from typing import Optional

class AIClient:
    PROVIDERS = [
        {
            "name": "groq",
            "base": "https://api.groq.com/openai/v1/chat/completions",
            "model": "llama-3.3-70b-versatile",
            "key_env": "GROQ_API_KEY",
            "weight": 3,
        },
        {
            "name": "openrouter",
            "base": "https://openrouter.ai/api/v1/chat/completions",
            "model": "openai/gpt-oss-120b:free",
            "key_env": "OPENROUTER_API_KEY",
            "weight": 2,
        },
        {
            "name": "deepseek",
            "base": "https://api.deepseek.com/v1/chat/completions",
            "model": "deepseek-chat",
            "key_env": "DEEPSEEK_API_KEY",
            "weight": 1,
        },
        {
            "name": "cloudflare",
            "base": "https://api.cloudflare.com/client/v4/accounts/.../ai/run/@cf/meta/llama-3.3-70b-instruct-fp8-fast",
            "model": "llama-3.3-70b",
            "key_env": "CLOUDFLARE_API_KEY",
            "weight": 1,
        },
    ]

    def __init__(self):
        self.fallback_log = []
        for p in self.PROVIDERS:
            key = os.environ.get(p["key_env"], "")
            p["available"] = bool(key) and len(key) > 10

    def _call_provider(self, provider: dict, messages: list, temperature: float = 0.7, max_tokens: int = 4096) -> Optional[str]:
        key = os.environ.get(provider["key_env"], "")
        if not key:
            return None
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {key}",
        }
        if provider["name"] == "openrouter":
            headers["HTTP-Referer"] = "https://github.com/macmaria171-ui/ai-business-engine"
        payload = {
            "model": provider["model"],
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        try:
            resp = requests.post(provider["base"], headers=headers, json=payload, timeout=60)
            if resp.status_code == 200:
                data = resp.json()
                content = data["choices"][0]["message"]["content"]
                self.fallback_log.append({"provider": provider["name"], "status": "ok"})
                return content
            elif resp.status_code == 429:
                time.sleep(5)
                return None
            else:
                self.fallback_log.append({"provider": provider["name"], "status": f"error_{resp.status_code}"})
                return None
        except Exception as e:
            self.fallback_log.append({"provider": provider["name"], "status": f"exception_{str(e)[:30]}"})
            return None

    def generate(self, system_prompt: str, user_prompt: str, temperature: float = 0.7, max_tokens: int = 4096) -> str:
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]
        providers = sorted(self.PROVIDERS, key=lambda p: p["weight"], reverse=True)
        random.shuffle(providers[:2])
        for provider in providers:
            if not provider["available"]:
                continue
            result = self._call_provider(provider, messages, temperature, max_tokens)
            if result:
                return result
        return json.dumps({"error": "All providers failed", "fallback_log": self.fallback_log[-5:]})

    def generate_json(self, system_prompt: str, user_prompt: str, temperature: float = 0.3) -> dict:
        result = self.generate(
            system_prompt + "\n\nRespond ONLY with valid JSON. No markdown. No explanation.",
            user_prompt,
            temperature=temperature,
        )
        result = result.strip()
        if result.startswith("```"):
            result = result.split("\n", 1)[-1]
            result = result.rsplit("```", 1)[0]
        try:
            return json.loads(result)
        except json.JSONDecodeError:
            return {"raw": result, "error": "failed to parse json"}
