"""Console program for Laboratory Work No. 3 (Playfair and Vigenere ciphers)."""
import polyalpha as pa
import sys

# Windows consoles/pipes often use cp1250/cp1252, which lack Ș and Ț
for stream in (sys.stdout, sys.stderr):
    if hasattr(stream, "reconfigure"):
        stream.reconfigure(encoding="utf-8")

LINE = "=" * 70


def ask_choice(prompt, options):
    while True:
        value = input(prompt).strip().upper()
        if value in options:
            return value
        print(f"  Invalid choice: enter one of {', '.join(options)}.")


def ask_key():
    while True:
        try:
            return pa.normalize_key(input(f"Enter the key (at least {pa.MIN_KEY_LENGTH} letters): "))
        except pa.CipherInputError as error:
            print(f"  Invalid key: {error}.")


def ask_text(label):
    while True:
        try:
            return pa.normalize_text(input(f"Enter the {label}: "), label)
        except pa.CipherInputError as error:
            print(f"  Invalid input: {error}.")


def main():
    print(LINE)
    print(" Laboratory Work No. 3 - Polyalphabetic ciphers (Romanian alphabet)")
    print(LINE)
    print(pa.encoding_table())
    print()
    task = ask_choice("Choose the task  [1] Playfair  [2] Vigenere: ", ("1", "2"))
    op = ask_choice("Choose the operation  [E] encrypt  [D] decrypt: ", ("E", "D"))
    key = ask_key()
    print(f"  Key (upper case):  {key}")
    if task == "1":
        print("  Playfair matrix (5 x 6, J merged into I):")
        print(pa.matrix_text(pa.build_matrix(key)))
    while True:
        try:
            if op == "E":
                text = input("Enter the message (plaintext): ")
                if task == "1":
                    pairs = pa.prepare_text(text)
                    print("  Digraphs:          " + " ".join(pairs))
                    result = pa.playfair_encrypt(text, key)
                else:
                    print("  Plaintext (normalised): " + pa.normalize_text(text, "message"))
                    result = pa.vigenere_encrypt(text, key)
                print(f"  Cryptogram:        {result}")
            else:
                text = input("Enter the cryptogram: ")
                if task == "1":
                    result = pa.playfair_decrypt(text, key)
                    print(f"  Decrypted message: {result}")
                    print("  (spaces and the filler letters X/Q are restored manually)")
                else:
                    result = pa.vigenere_decrypt(text, key)
                    print(f"  Decrypted message: {result}")
            return
        except pa.CipherInputError as error:
            print(f"  Invalid input: {error}.")


if __name__ == "__main__":
    main()
