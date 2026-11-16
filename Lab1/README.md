# Laboratory Work No. 1 — Caesar Cipher (Romanian alphabet)

Implementation of the two tasks from the handout, in Python 3 (no external dependencies).

| File | Purpose |
|---|---|
| `caesar.py` | Library: Table-2 letter encoding, input validation, permuted alphabet, `encrypt` / `decrypt` |
| `main.py` | Interactive console program (choose task, operation, key(s), text) |
| `test_caesar.py` | Unit tests (`python -m unittest -v`) |

## Tasks

* **Task 1.1** — Caesar cipher over the Romanian alphabet (n = 31), key k ∈ {1, …, 30}.
  `c = (x + k) mod 31`, `m = (y − k) mod 31`, using only the encoding from Table 2 (A = 0 … Z = 30).
* **Task 1.2** — Caesar cipher with two keys: the numeric shift k₁ and a keyword k₂ (≥ 7 Romanian letters)
  that permutes the alphabet (keyword letters first, without repetitions, then the remaining letters in natural order).
  The permuted alphabet is printed so the result can be checked by hand.

Input rules: only Romanian letters (upper or lower case, `Ş`/`Ţ` with cedilla are accepted and treated as `Ș`/`Ț`)
and spaces; spaces are removed and the text is upper-cased before processing. Invalid keys, keywords or
characters produce a clear message with the allowed values, and the value is asked again.

## Run

```bash
python3 main.py          # interactive program
python3 -m unittest -v   # tests
```

Example (Task 1.2, k₁ = 3, k₂ = `criptografie`):

```
Permuted alphabet: CRIPTOGAFEĂÂBDHÎJKLMNQSȘȚUVWXYZ
cifrul cezar  ->  POÂTXQPBIĂT
```
