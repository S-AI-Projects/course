# R16-T032: retrieval with source attribution

Applied example for the lesson "Behind the pipeline" (`chapters/en/chapter2/2.mdx`).

Task type: Boundary-case lesson extension.

## What it shows

A tiny lexical retriever over three local documents. It scores word overlap on lowercase word sets, breaks ties by document id and returns document ids with the results. The boundary decision is that a score of 0 is not a match.

## Run it

Python 3 standard library only.

```bash
python3 example.py
python3 -m unittest discover -s chapters/en/chapter2/applied-labs/r16-t032 -p "test_*.py"
```

## Output of `python3 example.py`

```text
Lexical test double (word overlap), not a production vector search.
Documents: {'A': 'red apple', 'B': 'green apple', 'C': 'blue sky'}
'red apple' -> [('A', 2), ('B', 1)]
'apple' -> [('A', 1), ('B', 1)]
'RED' -> [('A', 1)]
'ocean' -> []
'' -> []
42 -> TypeError: text must be a string
```

## Scope and limits

It matches words only and knows nothing about meaning. It is not a vector search and says nothing about real retrieval quality.
