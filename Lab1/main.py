"""
Interactive console program for Laboratory Work No. 1.

  Task 1.1 - Caesar cipher (one key)   over the Romanian alphabet
  Task 1.2 - Caesar cipher (two keys)  over the Romanian alphabet

Every input is validated; on invalid input the program prints a clear
message with the allowed values and asks for the value again.
"""

import textwrap

import caesar
from caesar import (
    InvalidCharacterError,
    InvalidKeyError,
    InvalidKeywordError,
)


def warn(message: str) -> None:
    """Print an error message, wrapped so that it fits in the console."""
    print(textwrap.fill(message, width=88, initial_indent="  ", subsequent_indent="      "))


def ask(prompt: str) -> str:
    """Read one line from the user (stops the program cleanly on EOF)."""
    try:
        return input(prompt)
    except EOFError:
        print()
        raise SystemExit(0)


def ask_task() -> str:
    while True:
        choice = ask("Choose the task  [1] Caesar cipher  [2] Caesar cipher with permutation: ").strip()
        if choice in ("1", "2"):
            return choice
        warn("Invalid choice: enter 1 or 2.")


def ask_operation() -> str:
    while True:
        choice = ask("Choose the operation  [E] encrypt  [D] decrypt: ").strip().upper()
        if choice in ("E", "D"):
            return choice
        warn("Invalid choice: enter E (encrypt) or D (decrypt).")


def ask_key() -> int:
    while True:
        try:
            return caesar.validate_key(ask(f"Enter key 1 (integer {caesar.MIN_KEY}-{caesar.MAX_KEY}): "))
        except InvalidKeyError as error:
            warn(f"Invalid key: {error}.")


def ask_keyword() -> str:
    while True:
        try:
            return caesar.validate_keyword(
                ask(f"Enter key 2 (keyword, at least {caesar.MIN_KEYWORD_LENGTH} Romanian letters): ")
            )
        except InvalidCharacterError as error:
            warn(f"Invalid keyword: {error}.")
        except InvalidKeywordError as error:
            warn(f"Invalid keyword: {error}.")


def ask_text(what: str) -> str:
    while True:
        try:
            return caesar.normalize_text(ask(f"Enter the {what}: "))
        except InvalidCharacterError as error:
            warn(f"Invalid text: {error}.")


def main() -> None:
    print("=" * 70)
    print(" Laboratory Work No. 1 - Caesar cipher over the Romanian alphabet")
    print("=" * 70)
    print(caesar.encoding_table())
    print()

    task = ask_task()
    operation = ask_operation()
    key = ask_key()

    alphabet = caesar.ALPHABET
    if task == "2":
        keyword = ask_keyword()
        alphabet = caesar.build_permuted_alphabet(keyword)
        print(f"  Keyword (upper case):   {keyword}")
        print(f"  Permuted alphabet:      {alphabet}")
        print(caesar.encoding_table(alphabet))

    if operation == "E":
        text = ask_text("message (plaintext)")
        print(f"  Plaintext (normalised): {text}")
        print(f"  Ciphertext:             {caesar.encrypt(text, key, alphabet)}")
    else:
        text = ask_text("ciphertext")
        print(f"  Ciphertext (normalised): {text}")
        print(f"  Decrypted message:       {caesar.decrypt(text, key, alphabet)}")


if __name__ == "__main__":
    main()
