"""Laboratory Work No. 3 - polyalphabetic ciphers over the Romanian alphabet.

Task 3.1: Playfair cipher (5 x 6 matrix, J is merged into I).
Task 3.2: Vigenere cipher (c = (m + k) mod 31, m = (c - k) mod 31).
"""

# The 31 letters of the Romanian alphabet, in the order of the encoding table.
ALPHABET = "AĂÂBCDEFGHIÎJKLMNOPQRSȘTȚUVWXYZ"
N = len(ALPHABET)  # n = 31

# Encoding tables: letter -> code and code -> letter.
LETTER_TO_CODE = {letter: code for code, letter in enumerate(ALPHABET)}
CODE_TO_LETTER = {code: letter for code, letter in enumerate(ALPHABET)}

# Upper-casing table, built explicitly from the lower-case alphabet.
_LOWERCASE = "aăâbcdefghiîjklmnopqrsștțuvwxyz"
_TO_UPPER = {lower: upper for lower, upper in zip(_LOWERCASE, ALPHABET)}
_TO_UPPER.update({upper: upper for upper in ALPHABET})

# Cedilla variants are treated as the same letters.
_CEDILLA_VARIANTS = {"Ş": "Ș", "ş": "Ș", "Ţ": "Ț", "ţ": "Ț"}

MIN_KEY_LENGTH = 7

# Playfair parameters: 30 letters (J merged into I) -> 5 rows x 6 columns.
ROWS, COLS = 5, 6
MERGED = {"J": "I"}
FILLER, ALT_FILLER = "X", "Q"

ALLOWED_RANGE = ("only letters of the Romanian alphabet (A-Z, Ă, Â, Î, Ș, Ț, "
                 "upper or lower case) are allowed")


class CipherInputError(ValueError):
    """Base class of all input errors."""


class InvalidCharacterError(CipherInputError):
    pass


class InvalidKeyError(CipherInputError):
    pass


def _to_upper_letter(ch):
    """Return the upper-case Romanian letter for ch, or None if ch is not a letter."""
    ch = _CEDILLA_VARIANTS.get(ch, ch)
    return _TO_UPPER.get(ch)


def normalize_text(text, what="text"):
    """Remove spaces and convert to upper case; reject every other character."""
    result = []
    for position, ch in enumerate(text, start=1):
        if ch.isspace():
            continue
        letter = _to_upper_letter(ch)
        if letter is None:
            raise InvalidCharacterError(
                f"invalid character {ch!r} at position {position} of the {what}: "
                f"{ALLOWED_RANGE} (spaces are removed)")
        result.append(letter)
    if not result:
        raise InvalidCharacterError(f"the {what} must contain at least one letter")
    return "".join(result)


def normalize_key(key):
    """Validate a key: only letters (no spaces), at least MIN_KEY_LENGTH of them."""
    letters = []
    for position, ch in enumerate(key.strip(), start=1):
        letter = _to_upper_letter(ch)
        if letter is None:
            raise InvalidKeyError(
                f"invalid character {ch!r} at position {position} of the key: "
                f"{ALLOWED_RANGE}; spaces are not allowed in the key")
        letters.append(letter)
    if len(letters) < MIN_KEY_LENGTH:
        raise InvalidKeyError(
            f"the key must contain at least {MIN_KEY_LENGTH} letters "
            f"(got {len(letters)})")
    return "".join(letters)


# ---------------------------------------------------------------- Vigenere
def vigenere_encrypt(message, key):
    m, k = normalize_text(message, "message"), normalize_key(key)
    return "".join(
        CODE_TO_LETTER[(LETTER_TO_CODE[ch] + LETTER_TO_CODE[k[i % len(k)]]) % N]
        for i, ch in enumerate(m))


def vigenere_decrypt(cryptogram, key):
    c, k = normalize_text(cryptogram, "cryptogram"), normalize_key(key)
    return "".join(
        CODE_TO_LETTER[(LETTER_TO_CODE[ch] - LETTER_TO_CODE[k[i % len(k)]]) % N]
        for i, ch in enumerate(c))


# ---------------------------------------------------------------- Playfair
def _merge(text):
    """Replace J by I (the matrix has no J)."""
    return "".join(MERGED.get(ch, ch) for ch in text)


def build_matrix(key):
    """Playfair matrix (list of ROWS rows, each with COLS letters)."""
    key = _merge(normalize_key(key))
    cells = []
    for ch in key + _merge(ALPHABET):
        if ch not in cells:
            cells.append(ch)
    return [cells[r * COLS:(r + 1) * COLS] for r in range(ROWS)]


def _positions(matrix):
    return {ch: (r, c) for r, row in enumerate(matrix) for c, ch in enumerate(row)}


def prepare_text(message):
    """Split the message into digraphs: no double letters, even length."""
    text = _merge(normalize_text(message, "message"))
    pairs, i = [], 0
    while i < len(text):
        a = text[i]
        filler = ALT_FILLER if a == FILLER else FILLER
        if i + 1 < len(text) and text[i + 1] != a:
            pairs.append(a + text[i + 1])
            i += 2
        else:                       # double letter or last single letter
            pairs.append(a + filler)
            i += 1
    return pairs


def _transform(pairs, matrix, step):
    pos = _positions(matrix)
    out = []
    for a, b in pairs:
        (ra, ca), (rb, cb) = pos[a], pos[b]
        if ra == rb:                                  # same row
            out.append(matrix[ra][(ca + step) % COLS] + matrix[rb][(cb + step) % COLS])
        elif ca == cb:                                # same column
            out.append(matrix[(ra + step) % ROWS][ca] + matrix[(rb + step) % ROWS][cb])
        else:                                         # rectangle
            out.append(matrix[ra][cb] + matrix[rb][ca])
    return out


def playfair_encrypt(message, key):
    matrix = build_matrix(key)
    return "".join(_transform(prepare_text(message), matrix, +1))


def playfair_decrypt(cryptogram, key):
    matrix = build_matrix(key)
    text = _merge(normalize_text(cryptogram, "cryptogram"))
    if len(text) % 2:
        raise InvalidCharacterError(
            f"the cryptogram must have an even number of letters (got {len(text)})")
    pairs = [text[i:i + 2] for i in range(0, len(text), 2)]
    for a, b in pairs:
        if a == b:
            raise InvalidCharacterError(
                f"invalid cryptogram: the pair {a + b} contains two equal letters")
    return "".join(_transform(pairs, matrix, -1))


def encoding_table():
    letters = "Letter " + "".join(f"{ch:>3}" for ch in ALPHABET)
    codes = "Code   " + "".join(f"{i:>3}" for i in range(N))
    return letters + "\n" + codes


def matrix_text(matrix):
    return "\n".join("  " + " ".join(row) for row in matrix)
