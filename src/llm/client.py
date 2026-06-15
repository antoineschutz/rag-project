import os
from collections.abc import Iterator

from src.config import env

# OpenAI-compatible backends: (base_url, api-key env var). gpt uses OpenAI's default endpoint.
_OPENAI_COMPATIBLE = {
    "gpt": (None, "OPENAI_API_KEY"),
    "groq": ("https://api.groq.com/openai/v1", "GROQ_API_KEY"),
}


class LLMClient:
    def __init__(self, backend: str = env.LLM_BACKEND, model: str | None = None,
                 num_ctx: int | None = None) -> None:
        """Set the backend (ollama, gpt, or groq), resolve the model name, and the Ollama context window."""
        self.backend = backend
        if model is not None:
            self.model = model
        elif backend == "gpt":
            self.model = env.OPENAI_MODEL
        elif backend == "groq":
            self.model = env.GROQ_MODEL
        else:
            self.model = env.OLLAMA_MODEL
        self.num_ctx = num_ctx if num_ctx is not None else env.OLLAMA_NUM_CTX

    def generate_stream(self, prompt: str) -> Iterator[str]:
        """Send prompt to the configured backend and yield response text chunks as they arrive."""
        if self.backend in _OPENAI_COMPATIBLE:
            base_url, key_var = _OPENAI_COMPATIBLE[self.backend]
            try:
                from openai import OpenAI
                client = OpenAI(base_url=base_url, api_key=os.environ.get(key_var))
                stream = client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": "You answer using context."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0,
                    stream=True,
                )
                for chunk in stream:
                    delta = chunk.choices[0].delta.content
                    if delta:
                        yield delta
            except Exception as e:
                raise RuntimeError(
                    f"{self.backend} request failed: check that {key_var} is set correctly. ({e})"
                ) from e

        elif self.backend == "ollama":
            try:
                import ollama
                stream = ollama.chat(
                    model=self.model,
                    messages=[{"role": "user", "content": prompt}],
                    options={"temperature": 0, "num_ctx": self.num_ctx},
                    stream=True,
                )
                for chunk in stream:
                    delta = chunk.message.content
                    if delta:
                        yield delta
            except Exception as e:
                raise RuntimeError(
                    f"Ollama request failed: is Ollama running with model '{self.model}' pulled? ({e})"
                ) from e

        else:
            raise ValueError(f"Unknown backend: '{self.backend}'. Choose 'ollama', 'gpt', or 'groq'.")

    def generate(self, prompt: str) -> str:
        """Send prompt to the configured LLM backend and return the full response string."""
        return "".join(self.generate_stream(prompt))
