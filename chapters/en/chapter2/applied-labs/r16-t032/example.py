"""A tiny lexical retriever over three local documents.

This is a lexical test double, NOT a production vector search. It only counts
shared lowercase words, so it knows nothing about meaning or embeddings.
"""
DOCUMENTS = {"A": "red apple", "B": "green apple", "C": "blue sky"}


def words(text):
    if not isinstance(text, str):
        raise TypeError("text must be a string")
    return set(text.lower().split())


def retrieve(query, documents=DOCUMENTS):
    """Return [(doc_id, score)], best first.

    score = number of words shared by the query and the document.
    Ties are broken by document id. Boundary decision: a document with score 0
    is not a match, so it is never returned.
    """
    query_words = words(query)
    scored = []
    for doc_id, text in documents.items():
        score = len(query_words & words(text))
        if score > 0:
            scored.append((doc_id, score))
    return sorted(scored, key=lambda item: (-item[1], item[0]))


def main():
    print("Lexical test double (word overlap), not a production vector search.")
    print("Documents:", DOCUMENTS)
    for query in ["red apple", "apple", "RED", "ocean", ""]:
        print(f"{repr(query)} -> {retrieve(query)}")
    try:
        retrieve(42)
    except TypeError as err:
        print(f"42 -> TypeError: {err}")


if __name__ == "__main__":
    main()
