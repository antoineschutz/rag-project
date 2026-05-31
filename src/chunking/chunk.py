def naive_chunk_text(text, chunk_size=500, overlap=20):

    chunks = []

    start = 0

    while start < len(text):

        end = start + chunk_size

        chunks.append(text[start:end])

        start += chunk_size - overlap

    return chunks

import nltk
nltk.download("punkt", quiet=True)
nltk.download("punkt_tab", quiet=True)

from nltk.tokenize import sent_tokenize

def chunk_text(text, chunk_size=500, min_chunk_size=300):
    sentences = sent_tokenize(text)

    chunks = []
    current = []
    current_len = 0

    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:
            continue

        if current_len + len(sentence) > chunk_size:

            if current_len >= min_chunk_size:
                chunks.append(" ".join(current))
                current = [sentence]
                current_len = len(sentence)
            else:
                current.append(sentence)
                current_len += len(sentence)

        else:
            current.append(sentence)
            current_len += len(sentence)

    if current:
        chunks.append(" ".join(current))

    return chunks

####################################################################### TIKTOKEN VERSION ##########################################################################################
from src.config import config


def chunk_text_tiktoken(
    text,
    max_tokens=config.CHUNK_MAX_TOKENS,
    overlap_tokens=config.CHUNK_OVERLAP
):


    import nltk
    import tiktoken
    from nltk.tokenize import sent_tokenize
    enc = tiktoken.get_encoding("cl100k_base")
    def token_len(text):
        """
        Converts text → tokens → returns token count.

        WHY THIS MATTERS:
        - Embedding models have a maximum token window
        - Token count ≠ character count
        - Token-aware chunking avoids hidden truncation
        """
        return len(enc.encode(text))
    

    sentences = sent_tokenize(text)

    chunks = []
    current_chunk = []
    current_tokens = 0

    for sentence in sentences:
        sentence_tokens = token_len(sentence)

        if sentence_tokens > max_tokens:
            if current_chunk:
                chunks.append(" ".join(current_chunk))
                current_chunk = []
                current_tokens = 0

            tokens = enc.encode(sentence)

            for i in range(0, len(tokens), max_tokens):
                chunk_tokens = tokens[i:i + max_tokens]
                chunk_text = enc.decode(chunk_tokens)
                chunks.append(chunk_text)

            continue


        if current_tokens + sentence_tokens > max_tokens:
            chunks.append(" ".join(current_chunk))

            if overlap_tokens > 0:
                flat_tokens = enc.encode(" ".join(current_chunk))
                overlap = flat_tokens[-overlap_tokens:]
                current_chunk = [enc.decode(overlap), sentence]
                current_tokens = len(overlap) + sentence_tokens
            else:
                current_chunk = [sentence]
                current_tokens = sentence_tokens

        else:
            current_chunk.append(sentence)
            current_tokens += sentence_tokens

    # final flush
    if current_chunk:
        chunks.append(" ".join(current_chunk))

    return chunks














####################################################################### TIKTOKEN VERSION ##########################################################################################


def chunk_documents(docs):
    chunked_docs = []

    for doc in docs:
        chunks = chunk_text_tiktoken(doc["text"])
        for chunk in chunks:
            chunked_docs.append({
                "text": chunk,
                "source": doc["source"]
            })

    return chunked_docs