# Shared image for both the API (uvicorn) and the dashboard (streamlit); the compose file
# picks the command per service.
FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# libgomp1 is the OpenMP runtime that faiss-cpu (and torch) need; slim does not ship it.
RUN apt-get update \
    && apt-get install -y --no-install-recommends libgomp1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install the CPU-only torch wheel before the rest so we don't pull the multi-GB CUDA build
# that sentence-transformers would otherwise drag in.
COPY requirements.txt .
RUN pip install --extra-index-url https://download.pytorch.org/whl/cpu torch \
    && pip install -r requirements.txt

# Bake the NLTK and tiktoken data so containers need no network for chunking at runtime.
RUN python -c "import nltk; nltk.download('punkt'); nltk.download('punkt_tab')" \
    && python -c "import tiktoken; tiktoken.get_encoding('cl100k_base')"

# App code (data/ ships as a default corpus; a bind mount can override it).
COPY . .

EXPOSE 8000 8501

# Default to the API; the dashboard service overrides this command in docker-compose.yml.
CMD ["uvicorn", "src.api.server:app", "--host", "0.0.0.0", "--port", "8000"]
