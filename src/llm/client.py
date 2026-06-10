from src.config import config


class LLMClient:
    def __init__(self, backend: str = config.LLM_BACKEND, model: str | None = None) -> None:
        """Set the LLM backend (ollama or gpt) and resolve the model name from config if not given."""
        self.backend = backend
        if model is None:
            self.model = config.OPENAI_MODEL if backend == "gpt" else config.OLLAMA_MODEL
        else:
            self.model = model

    def generate(self, prompt: str) -> str:
        """Send prompt to the configured LLM backend and return the response string."""
        if self.backend == "gpt":
            try:
                from openai import OpenAI
                client = OpenAI()
                response = client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": "You answer using context."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0
                )
                return response.choices[0].message.content or ""
            except Exception as e:
                raise RuntimeError(
                    f"OpenAI request failed — check that OPENAI_API_KEY is set correctly. ({e})"
                ) from e

        elif self.backend == "ollama":
            try:
                import ollama
                response = ollama.chat(
                    model=self.model,
                    messages=[{"role": "user", "content": prompt}],
                    options={"temperature": 0},
                )
                return response.message.content or ""
            except Exception as e:
                raise RuntimeError(
                    f"Ollama request failed — is Ollama running with model '{self.model}' pulled? ({e})"
                ) from e

        else:
            raise ValueError(f"Unknown backend: '{self.backend}'. Choose 'ollama' or 'gpt'.")