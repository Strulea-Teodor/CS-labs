"""
Laboratory Work No. 1 - Caesar cipher over the Romanian alphabet.

This module implements:
  * Task 1.1 - the classic Caesar cipher (one numeric key) and
  * Task 1.2 - the Caesar cipher with two keys (numeric shift + keyword
    that permutes the alphabet)

for the Romanian alphabet of n = 31 letters.

The letter encoding is the one from Table 2 of the laboratory handout
(A = 0, Ă = 1, Â = 2, ..., Z = 30).  The built-in character codes of
Python (ord / chr, i.e. Unicode code points) are deliberately NOT used to
compute the shift: every conversion letter <-> number goes through the
look-up tables defined below.
"""

# ---------------------------------------------------------------------------
# 1. Alphabet and letter encoding (Table 2)
# ---------------------------------------------------------------------------

# The 31 letters of the Romanian alphabet, in the order of Table 2.
# Ș and Ț are written with comma below (U+0218 / U+021A).
ALPHABET = "AĂÂBCDEFGHIÎJKLMNOPQRSȘTȚUVWXYZ"
N = len(ALPHABET)  # n = 31

# Lower-case form of every letter, in the same order as ALPHABET.
_LOWERCASE = "aăâbcdefghiîjklmnopqrsștțuvwxyz"

# Encoding tables: letter -> code and code -> letter.
LETTER_TO_CODE = {letter: code for code, letter in enumerate(ALPHABET)}
CODE_TO_LETTER = {code: letter for code, letter in enumerate(ALPHABET)}

# Upper-casing table (built explicitly, so that we never rely on the
# language's own notion of character codes / case mapping).
_TO_UPPER = {lower: upper for lower, upper in zip(_LOWERCASE, ALPHABET)}
_TO_UPPER.update({upper: upper for upper in ALPHABET})

# Letters that are sometimes typed with a cedilla instead of a comma below.
# They are treated as the same letters (implementation tip in the handout).
_CEDILLA_VARIANTS = {
    "Ş": "Ș", "ş": "Ș",   # S with cedilla  -> Ș
    "Ţ": "Ț", "ţ": "Ț",   # T with cedilla  -> Ț
}

MIN_KEY, MAX_KEY = 1, N - 1          # key k ∈ {1, 2, ..., 30}
MIN_KEYWORD_LENGTH = 7               # Task 1.2, requirement 3


# ---------------------------------------------------------------------------
# 2. Errors raised on invalid input
# ---------------------------------------------------------------------------

class InvalidKeyError(ValueError):
    """The numeric key is not an integer in the range 1..30."""


class InvalidCharacterError(ValueError):
    """The text (or keyword) contains a character outside the alphabet."""

    def __init__(self, character: str, position: int):
        self.character = character
        self.position = position
        super().__init__(
            f"invalid character {character!r} at position {position}: "
            f"only letters of the Romanian alphabet "
            f"(A-Z, Ă, Â, Î, Ș, Ț, upper or lower case) and spaces are allowed"
        )


class InvalidKeywordError(ValueError):
    """The keyword is shorter than the minimum allowed length."""


# ---------------------------------------------------------------------------
# 3. Input validation and normalisation
# ---------------------------------------------------------------------------

def validate_key(value) -> int:
    """
    Convert *value* (string or int) to an integer key and check that it is
    in the range 1..30.  Raises InvalidKeyError otherwise.
    """
    try:
        key = int(str(value).strip())
    except ValueError:
        raise InvalidKeyError(
            f"the key must be an integer between {MIN_KEY} and {MAX_KEY} "
            f"inclusive (got {value!r})"
        ) from None
    if not MIN_KEY <= key <= MAX_KEY:
        raise InvalidKeyError(
            f"the key must be an integer between {MIN_KEY} and {MAX_KEY} "
            f"inclusive (got {key})"
        )
    return key


def normalize_text(text: str) -> str:
    """
    Prepare a text for encryption/decryption:
      * cedilla variants Ş/Ţ are replaced by Ș/Ț,
      * spaces are removed,
      * letters are converted to upper case using the explicit table.
    Any other character raises InvalidCharacterError (with its position).
    """
    result = []
    for position, char in enumerate(text, start=1):
        if char == " ":
            continue
        char = _CEDILLA_VARIANTS.get(char, char)
        upper = _TO_UPPER.get(char)
        if upper is None:
            raise InvalidCharacterError(char, position)
        result.append(upper)
    return "".join(result)


def validate_keyword(keyword: str) -> str:
    """
    Normalise the keyword (Task 1.2) and check that it has at least
    MIN_KEYWORD_LENGTH letters.  Returns the upper-case keyword.
    """
    normalized = normalize_text(keyword)      # may raise InvalidCharacterError
    if len(normalized) < MIN_KEYWORD_LENGTH:
        raise InvalidKeywordError(
            f"the keyword must contain at least {MIN_KEYWORD_LENGTH} letters "
            f"of the Romanian alphabet (got {len(normalized)})"
        )
    return normalized


# ---------------------------------------------------------------------------
# 4. Permuted alphabet (Task 1.2)
# ---------------------------------------------------------------------------

def build_permuted_alphabet(keyword: str) -> str:
    """
    Build the permuted alphabet from a keyword: the distinct letters of the
    keyword come first (first occurrence kept, duplicates dropped), followed
    by the remaining letters of the alphabet in their natural order.

    >>> build_permuted_alphabet("CRIPTOGRAFIE")
    'CRIPTOGAFEĂÂBDHÎJKLMNQSȘȚUVWXYZ'
    """
    keyword = validate_keyword(keyword)
    permuted = []
    for letter in keyword + ALPHABET:
        if letter not in permuted:
            permuted.append(letter)
    return "".join(permuted)


# ---------------------------------------------------------------------------
# 5. Encryption and decryption
# ---------------------------------------------------------------------------

def _encoding_tables(alphabet: str):
    """Return (letter->code, code->letter) tables for the given alphabet."""
    if alphabet == ALPHABET:
        return LETTER_TO_CODE, CODE_TO_LETTER
    letter_to_code = {letter: code for code, letter in enumerate(alphabet)}
    code_to_letter = {code: letter for code, letter in enumerate(alphabet)}
    return letter_to_code, code_to_letter


def encrypt(plaintext: str, key, alphabet: str = ALPHABET) -> str:
    """
    Caesar encryption:  c = e_k(x) = (x + k) mod n.
    *alphabet* is the (possibly permuted) alphabet that defines the codes.
    """
    key = validate_key(key)
    text = normalize_text(plaintext)
    letter_to_code, code_to_letter = _encoding_tables(alphabet)
    ciphertext = []
    for letter in text:
        x = letter_to_code[letter]
        c = (x + key) % N
        ciphertext.append(code_to_letter[c])
    return "".join(ciphertext)


def decrypt(ciphertext: str, key, alphabet: str = ALPHABET) -> str:
    """
    Caesar decryption:  m = d_k(y) = (y - k) mod n.
    Python's % operator always returns a non-negative remainder for a
    positive modulus, so a negative y - k is automatically brought back
    into the range 0..n-1 (e.g. (1 - 3) % 31 == 29).
    """
    key = validate_key(key)
    text = normalize_text(ciphertext)
    letter_to_code, code_to_letter = _encoding_tables(alphabet)
    plaintext = []
    for letter in text:
        y = letter_to_code[letter]
        m = (y - key) % N
        plaintext.append(code_to_letter[m])
    return "".join(plaintext)


# Convenience wrappers for Task 1.2 (two keys).

def encrypt_with_keyword(plaintext: str, key, keyword: str) -> str:
    """Task 1.2: Caesar encryption over the keyword-permuted alphabet."""
    return encrypt(plaintext, key, build_permuted_alphabet(keyword))


def decrypt_with_keyword(ciphertext: str, key, keyword: str) -> str:
    """Task 1.2: Caesar decryption over the keyword-permuted alphabet."""
    return decrypt(ciphertext, key, build_permuted_alphabet(keyword))


def encoding_table(alphabet: str = ALPHABET) -> str:
    """Return a printable two-row table  letter / code  for *alphabet*."""
    letters = "  ".join(f"{letter:>2}" for letter in alphabet)
    codes = "  ".join(f"{code:>2}" for code in range(len(alphabet)))
    return f"Letter  {letters}\nCode    {codes}"
