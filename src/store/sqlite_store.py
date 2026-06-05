import sqlite3


class ChunkStore:
    def __init__(self, db_path: str) -> None:
        """Set the SQLite database path."""
        self.db_path = db_path

    def exists(self) -> bool:
        """Return True if the chunks table exists and contains at least one row."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("SELECT 1 FROM chunks LIMIT 1")
            return True
        except sqlite3.OperationalError:
            return False

    def save(self, chunks: list[dict[str, str]]) -> None:
        """Drop and recreate the chunks table, then insert all chunks."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DROP TABLE IF EXISTS chunks")
            conn.execute(
                "CREATE TABLE chunks (id INTEGER PRIMARY KEY, text TEXT, source TEXT)"
            )
            conn.executemany(
                "INSERT INTO chunks (text, source) VALUES (?, ?)",
                [(c["text"], c["source"]) for c in chunks],
            )

    def load(self) -> list[dict[str, str]]:
        """Load all chunks from SQLite ordered by insertion id."""
        with sqlite3.connect(self.db_path) as conn:
            rows = conn.execute(
                "SELECT text, source FROM chunks ORDER BY id"
            ).fetchall()
        return [{"text": text, "source": source} for text, source in rows]
