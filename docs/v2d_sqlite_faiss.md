# V2-D: SQLite + FAISS — Detailed Explanation

This document explains everything added in V2-D: why it was done, what each technology is, and how every line of new code works.

---

## Why this step exists

Before V2-D, the pipeline had two problems:

**Problem 1 — slow startup.** Every time you ran the pipeline, it re-embedded all your documents from scratch. Embedding is the slowest step. V1 already added a cache (`.npy` + `.json` files), but it was a blunt cache: one giant file for all embeddings, one giant file for all chunk text. If you added a new document, you had to throw everything away and rebuild from zero.

**Problem 2 — brute-force search.** The old `Retriever` used `sklearn.cosine_similarity`, which computes the similarity between your query and *every single chunk* in the corpus, then sorts the results. This works fine for hundreds of chunks, but at tens of thousands it becomes slow. FAISS is a library built specifically for fast vector search at scale.

V2-D adds a second backend (`--store faiss`) that uses:
- **FAISS** — a fast vector index, replacing the sklearn brute-force search
- **SQLite** — a proper database, replacing the JSON file for chunk text

The original numpy/JSON backend is kept untouched so both can be compared.

---

## What is SQLite?

SQLite is a relational database that lives in a single file on disk (e.g. `cache/chunks.db`). Unlike databases like PostgreSQL or MySQL, SQLite needs no server — you just open the file and query it. Python ships with it built-in via the `sqlite3` module.

A **relational database** stores data in **tables**, like spreadsheets. Each table has named **columns** with fixed types, and each **row** is one record.

For this project, the table looks like this:

```
┌────┬───────────────────────────────┬──────────────────────┐
│ id │ text                          │ source               │
├────┼───────────────────────────────┼──────────────────────┤
│  1 │ "Attention is a mechanism..." │ "rag_lewis2020.pdf"  │
│  2 │ "The transformer model..."    │ "rag_lewis2020.pdf"  │
│  3 │ ...                           │ ...                  │
└────┴───────────────────────────────┴──────────────────────┘
```

You interact with it using **SQL** (Structured Query Language). The key SQL commands used here:

| SQL | What it does |
|-----|-------------|
| `CREATE TABLE chunks (id INTEGER PRIMARY KEY, text TEXT, source TEXT)` | Creates the table with 3 columns |
| `DROP TABLE IF EXISTS chunks` | Deletes the table if it already exists (used before recreating) |
| `INSERT INTO chunks (text, source) VALUES (?, ?)` | Adds a row; `?` is a placeholder filled at runtime |
| `SELECT text, source FROM chunks ORDER BY id` | Reads all rows, in insertion order |
| `SELECT 1 FROM chunks LIMIT 1` | Tries to read one row — used just to check the table exists |

**Why SQLite instead of JSON?**

With JSON, every time you add or delete a document you have to:
1. Load the entire JSON file into memory
2. Modify the Python list
3. Write the whole file back to disk

With SQLite you can insert or delete individual rows without touching anything else. For a future step where documents are added incrementally, this matters a lot.

---

## `src/store/sqlite_store.py` — line by line

```python
import sqlite3
```
The built-in Python module for SQLite. No install needed.

---

```python
class ChunkStore:
    def __init__(self, db_path: str) -> None:
        self.db_path = db_path
```
Just stores the path to the `.db` file. The connection is not opened here — it's opened and closed inside each method. This is intentional: SQLite connections are cheap to open, and keeping them short-lived avoids locking issues.

---

```python
def exists(self) -> bool:
    try:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("SELECT 1 FROM chunks LIMIT 1")
        return True
    except sqlite3.OperationalError:
        return False
```
Checks whether the `chunks` table exists and has data. `sqlite3.connect()` creates the file if it doesn't exist yet, so we can't just check for the file — we have to try to query the table. If the table doesn't exist, SQLite raises `OperationalError`, which we catch and turn into `False`.

The `with` statement is a **context manager**: it automatically commits the transaction and closes the connection when the block exits, even if an error occurs.

---

```python
def save(self, chunks: list[dict[str, str]]) -> None:
    with sqlite3.connect(self.db_path) as conn:
        conn.execute("DROP TABLE IF EXISTS chunks")
        conn.execute(
            "CREATE TABLE chunks (id INTEGER PRIMARY KEY, text TEXT, source TEXT)"
        )
        conn.executemany(
            "INSERT INTO chunks (text, source) VALUES (?, ?)",
            [(c["text"], c["source"]) for c in chunks],
        )
```
Drops and recreates the table, then inserts all chunks in one batch.

- `INTEGER PRIMARY KEY` — SQLite auto-assigns an incrementing integer ID to each row. This ID is used later to match chunks to their FAISS vector positions (FAISS stores vectors at positions 0, 1, 2, ... and the SQLite row IDs start at 1, but the `ORDER BY id` in `load()` guarantees the same order).
- `executemany` — inserts many rows in one call, much faster than calling `execute` in a loop.
- `?` placeholders — never use f-strings to build SQL queries. Placeholders tell SQLite to treat the values as data, not as SQL code. This prevents SQL injection.

---

```python
def load(self) -> list[dict[str, str]]:
    with sqlite3.connect(self.db_path) as conn:
        rows = conn.execute(
            "SELECT text, source FROM chunks ORDER BY id"
        ).fetchall()
    return [{"text": text, "source": source} for text, source in rows]
```
Reads all rows back as a list of dicts — the same format the rest of the pipeline expects. `ORDER BY id` is critical: it guarantees the chunks come back in the same order they were inserted, which must match the order of vectors in the FAISS index (vector at position 0 must correspond to chunk at index 0).

---

## What is FAISS?

FAISS (Facebook AI Similarity Search) is a library for searching through large collections of vectors efficiently. Its core abstraction is an **index**: a data structure that stores vectors and can answer "find the top-k vectors most similar to this query vector" very quickly.

### Why faster than sklearn?

`sklearn.cosine_similarity` computes the similarity between the query and every single stored vector, then sorts. This is O(n) in the number of chunks — it scales linearly.

FAISS uses specialised data structures and low-level optimisations (SIMD instructions, batching) that make even brute-force search much faster. More importantly, FAISS offers approximate nearest neighbour (ANN) indexes (like `IndexIVFFlat`) that can search a fraction of the vectors and still return near-perfect results — making it O(log n) or even O(1) at scale.

In V2-D we use `IndexFlatIP`, which is still exact (checks all vectors) but much faster in practice than sklearn due to FAISS's low-level optimisations.

### What is cosine similarity, and what is inner product?

**Cosine similarity** measures the angle between two vectors. Two vectors pointing in the same direction have cosine similarity 1.0; perpendicular vectors have 0; opposite vectors have -1.

**Inner product** (also called dot product) of two vectors `a` and `b` is:
```
a · b = a[0]*b[0] + a[1]*b[1] + ... + a[n]*b[n]
```

The relationship between them is:
```
cosine_similarity(a, b) = (a · b) / (|a| × |b|)
```

Where `|a|` is the **L2 norm** (length) of vector `a`: `sqrt(a[0]² + a[1]² + ... + a[n]²)`.

If both vectors are **L2-normalised** (their length is forced to 1.0), the denominator becomes `1 × 1 = 1`, and inner product equals cosine similarity exactly:
```
if |a| == 1 and |b| == 1:
    a · b  ==  cosine_similarity(a, b)
```

This is why `faiss.normalize_L2()` is called before building the index and before each query: it rescales every vector to unit length, making `IndexFlatIP` (inner product) produce the same ranking as cosine similarity.

---

## `src/retrieval/retriever_faiss.py` — line by line

```python
class RetrieverFAISS:
    def __init__(self, chunked_docs: list[dict[str, str]], doc_embeddings: np.ndarray) -> None:
        self.docs = chunked_docs
        vectors = doc_embeddings.astype("float32")
        faiss.normalize_L2(vectors)
        self.index = faiss.IndexFlatIP(vectors.shape[1])
        self.index.add(vectors)
```

- `.astype("float32")` — FAISS requires 32-bit floats. The embeddings from `sentence-transformers` are 32-bit by default, but this is a safety cast.
- `faiss.normalize_L2(vectors)` — rescales every row to unit length **in-place**. After this, each vector has `|v| = 1.0`, so inner product = cosine similarity.
- `faiss.IndexFlatIP(vectors.shape[1])` — creates a flat (no compression, exact search) inner-product index. `vectors.shape[1]` is the embedding dimension (384 for `all-MiniLM-L6-v2`).
- `self.index.add(vectors)` — loads all vectors into the index. FAISS assigns them positions 0, 1, 2, ... in the order they are added. This order must match the order of `chunked_docs`.

---

```python
@classmethod
def from_index(cls, chunked_docs: list[dict[str, str]], index: faiss.IndexFlatIP) -> "RetrieverFAISS":
    obj = cls.__new__(cls)
    obj.docs = chunked_docs
    obj.index = index
    return obj
```

A **classmethod** is a factory: it creates an instance without going through `__init__`. This is needed for the cache-load path where the FAISS index is read from disk — we already have a built index, we don't want to rebuild it from raw embeddings.

`cls.__new__(cls)` allocates a blank instance without calling `__init__`. We then manually set the two attributes `__init__` would have set, giving us a fully functioning object.

---

```python
def retrieve(self, query_embedding: np.ndarray, top_k: int = config.TOP_K) -> list[dict[str, Any]]:
    query = np.array(query_embedding, dtype="float32")
    if query.ndim == 1:
        query = query.reshape(1, -1)
    faiss.normalize_L2(query)
    scores, indices = self.index.search(query, top_k)
```

- `query.ndim == 1` check — `embed_query` returns a 1D array `[384]`. FAISS expects a 2D array `[[384]]` (a batch of 1 query). `reshape(1, -1)` adds that outer dimension.
- `faiss.normalize_L2(query)` — same normalisation as at index time, so the inner product gives cosine similarity.
- `self.index.search(query, top_k)` — returns two arrays of shape `(1, top_k)`:
  - `scores` — the inner product scores (≈ cosine similarities) for the top-k results
  - `indices` — the positions in the index of those top-k results

```python
    results = []
    for score, idx in zip(scores[0], indices[0]):
        results.append({
            "text": self.docs[idx]["text"],
            "source": self.docs[idx]["source"],
            "score": float(score),
        })
```

`scores[0]` and `indices[0]` are the results for the first (only) query. `idx` is the position in the FAISS index, which matches the position in `self.docs` because both were built in the same order.

---

## How both backends are wired together in `main.py`

A `--store` argument controls which backend is used:

```
python main.py --query "..." --store numpy   # original path (default)
python main.py --query "..." --store faiss   # new FAISS + SQLite path
```

### numpy path (unchanged)

```python
if args.store == "numpy":
    # check for cache/embeddings.npy + cache/chunks.json
    # if present: load from files
    # if not: embed, save to files
    retriever = Retriever(chunked_docs, doc_embeddings)
```

### faiss path (new)

```python
else:  # faiss
    store = ChunkStore(config.SQLITE_DB_PATH)
    if os.path.exists(config.FAISS_INDEX_PATH) and store.exists():
        # cache hit: load index from disk, load chunks from SQLite
        chunked_docs = store.load()
        index = faiss.read_index(config.FAISS_INDEX_PATH)
        retriever = RetrieverFAISS.from_index(chunked_docs, index)
    else:
        # cache miss: embed everything, save index + SQLite
        ...
        store.save(chunked_docs)
        retriever = RetrieverFAISS(chunked_docs, doc_embeddings)
        faiss.write_index(retriever.index, config.FAISS_INDEX_PATH)
```

`faiss.write_index` / `faiss.read_index` — FAISS's built-in serialisation. Saves the entire index (all vectors + their structure) to a binary file. On load, the index is ready to search immediately without rebuilding.

After this branching block, both paths have a `retriever` object with the same `.retrieve()` interface, so the rest of `main.py` is identical regardless of which backend was used.

---

## Files added/modified

| File | What changed |
|------|-------------|
| `src/store/sqlite_store.py` | New — `ChunkStore` class wrapping SQLite |
| `src/store/__init__.py` | New — empty, makes `src/store` a Python package |
| `src/retrieval/retriever_faiss.py` | New — `RetrieverFAISS` using FAISS IndexFlatIP |
| `src/config.py` | Added `FAISS_INDEX_PATH` and `SQLITE_DB_PATH` |
| `main.py` | Added `--store` flag, branched cache logic |
| `requirements.txt` | Added `faiss-cpu` |

### Cache files produced

| Backend | Vector file | Text/metadata file |
|---------|------------|-------------------|
| numpy | `cache/embeddings.npy` | `cache/chunks.json` |
| faiss | `cache/faiss.index` | `cache/chunks.db` |

Both sets of cache files coexist — switching backends doesn't invalidate the other's cache.

---

## FAISS index alternatives to `IndexFlatIP`

`IndexFlatIP` is the simplest possible index: it stores all vectors as-is and checks every single one at query time. It is **exact** (always finds the true top-k) but brute-force. Here are the main alternatives:

### `IndexFlatL2`
The same flat/exact/brute-force approach, but using **L2 (Euclidean) distance** instead of inner product. For L2, smaller score = more similar (vs. IP where larger = more similar).

For **normalised vectors**, `IndexFlatL2` and `IndexFlatIP` produce identical rankings — mathematically, `L2(a, b)² = 2 - 2·(a·b)` when both are unit vectors, so the order is the same. The only reason to prefer one over the other is which metric you want to expose in your scores.

**When to use:** When your embeddings are not normalised and you want true Euclidean distance.

---

### `IndexIVFFlat` — Inverted File Index
This is where FAISS starts to be genuinely faster than brute-force. It works in two phases:

1. **Training** — clusters all vectors into `nlist` groups (Voronoi cells) using k-means
2. **Search** — at query time, only searches the `nprobe` nearest clusters instead of all vectors

Instead of checking 10,000 vectors, it might only check 500 (if `nprobe=5` and `nlist=100`). This makes it **approximate** — it can miss a true nearest neighbour that lives in an unsearched cluster — but in practice recall stays above 95% with sensible settings.

```python
# Example setup
nlist = 100  # number of clusters — rule of thumb: sqrt(n_vectors)
index = faiss.IndexIVFFlat(faiss.IndexFlatIP(dim), dim, nlist, faiss.METRIC_INNER_PRODUCT)
index.train(vectors)   # required — learns the cluster centroids
index.add(vectors)
index.nprobe = 10      # how many clusters to search at query time
```

**When to use:** 10,000+ vectors. The standard go-to for medium-scale RAG.

---

### `IndexHNSWFlat` — Hierarchical Navigable Small World
A graph-based index. During construction, each vector is connected to its nearest neighbours in a multi-layer graph. At query time, the search navigates the graph rather than scanning vectors — like a GPS taking roads instead of walking in a straight line through fields.

- **No training step required** (unlike IVF)
- Very fast queries even at millions of vectors
- High memory usage (stores the graph edges)
- Does not support `faiss.normalize_L2` in-place — you normalise the vectors before adding

```python
M = 32  # number of neighbours per node — higher = better recall, more memory
index = faiss.IndexHNSWFlat(dim, M, faiss.METRIC_INNER_PRODUCT)
index.add(vectors)  # no .train() needed
```

**When to use:** Production systems, millions of vectors, latency-sensitive. The most popular ANN index in practice alongside IVF.

---

### `IndexIVFPQ` — IVF + Product Quantization
Combines IVF clustering with **Product Quantization (PQ)**: each vector is compressed into a compact code (e.g. 64 bytes instead of 1536 bytes for a full float32 vector). Dramatically reduces memory at the cost of some accuracy.

**When to use:** Very large corpora (millions of vectors) where RAM is the bottleneck.

---

### Summary table

| Index | Exact? | Training? | Speed | Memory | Good for |
|-------|--------|-----------|-------|--------|---------|
| `IndexFlatIP` ← **we use this** | Yes | No | Slow at scale | Normal | < 50k vectors |
| `IndexFlatL2` | Yes | No | Slow at scale | Normal | < 50k vectors, unnormalised vectors |
| `IndexIVFFlat` | ~95%+ | Yes | Fast | Normal | 10k–1M vectors |
| `IndexHNSWFlat` | ~99% | No | Very fast | High | Production, low latency |
| `IndexIVFPQ` | ~90% | Yes | Very fast | Very low | Millions of vectors, limited RAM |

**For this project**, `IndexFlatIP` is the right choice. With a few hundred to a few thousand chunks from PDFs, brute-force is instantaneous. `IndexIVFFlat` becomes worthwhile above ~10k vectors; `HNSW` is overkill unless building a production service. The natural upgrade path in this roadmap is `IndexIVFFlat` when the corpus grows.
