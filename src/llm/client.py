from collections.abc import Iterator

from src.config import env


class LLMClient:
    def __init__(self, backend: str = env.LLM_BACKEND, model: str | None = None,
                 num_ctx: int | None = None) -> None:
        """Set the backend (ollama or gpt), resolve the model name, and the Ollama context window."""
        self.backend = backend
        if model is None:
            self.model = env.OPENAI_MODEL if backend == "gpt" else env.OLLAMA_MODEL
        else:
            self.model = model
        self.num_ctx = num_ctx if num_ctx is not None else env.OLLAMA_NUM_CTX

    def generate_stream(self, prompt: str) -> Iterator[str]:
        """Send prompt to the configured backend and yield response text chunks as they arrive."""
        if self.backend == "gpt":
            try:
                from openai import OpenAI
                client = OpenAI()
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
                    f"OpenAI request failed: check that OPENAI_API_KEY is set correctly. ({e})"
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
            raise ValueError(f"Unknown backend: '{self.backend}'. Choose 'ollama' or 'gpt'.")

    def generate(self, prompt: str) -> str:
        """Send prompt to the configured LLM backend and return the full response string."""
        return "".join(self.generate_stream(prompt))
