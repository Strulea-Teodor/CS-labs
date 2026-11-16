import unittest

from polyalpha import (ALPHABET, N, LETTER_TO_CODE, CODE_TO_LETTER,
                       InvalidCharacterError, InvalidKeyError, normalize_text,
                       normalize_key, vigenere_encrypt, vigenere_decrypt,
                       build_matrix, prepare_text, playfair_encrypt,
                       playfair_decrypt)


class EncodingTests(unittest.TestCase):
    def test_alphabet_size_and_codes(self):
        self.assertEqual(N, 31)
        self.assertEqual(LETTER_TO_CODE["A"], 0)
        self.assertEqual(LETTER_TO_CODE["Ș"], 22)
        self.assertEqual(LETTER_TO_CODE["Z"], 30)
        self.assertEqual(CODE_TO_LETTER[11], "Î")


class ValidationTests(unittest.TestCase):
    def test_normalisation(self):
        self.assertEqual(normalize_text("Per aspera ad astra"), "PERASPERAADASTRA")
        self.assertEqual(normalize_text("Şi Ţara"), "ȘIȚARA")

    def test_invalid_characters(self):
        for bad in ("Hello, world!", "parola 123", "ab-c"):
            with self.assertRaises(InvalidCharacterError):
                normalize_text(bad)

    def test_error_names_position(self):
        with self.assertRaises(InvalidCharacterError) as ctx:
            normalize_text("abc1")
        self.assertIn("position 4", str(ctx.exception))

    def test_empty_text(self):
        with self.assertRaises(InvalidCharacterError):
            normalize_text("   ")

    def test_key_length_and_characters(self):
        for bad in ("cheie", "Ștefan", "parola1", "doua cuvinte"):
            with self.assertRaises(InvalidKeyError):
                normalize_key(bad)
        self.assertEqual(normalize_key("securitate"), "SECURITATE")


class VigenereTests(unittest.TestCase):
    def test_known_value(self):
        # computed by hand with the codes A=0, Ă=1, ..., Z=30 (n = 31)
        self.assertEqual(vigenere_encrypt("Per aspera ad astra", "superman"),
                         "GAFEIÂEDSUTEIFRN")

    def test_wrap_around(self):
        # Z (30) + B (3) = 33 mod 31 = 2 -> Â ;  and first key letter A leaves text
        self.assertEqual(vigenere_encrypt("Z", "BBBBBBB"), "Â")
        self.assertEqual(vigenere_encrypt("cifru", "AAAAAAA"), "CIFRU")

    def test_round_trip(self):
        message = "ȘTIINȚA CRIPTOGRAFIEI ÎN ROMÂNĂ"
        for key in ("criptare", "ȘtefanCelMare", "AAAAAAB"):
            self.assertEqual(vigenere_decrypt(vigenere_encrypt(message, key), key),
                             normalize_text(message))

    def test_key_is_repeated(self):
        text = "A" * 20
        self.assertEqual(vigenere_encrypt(text, "BCDEFGH"),
                         ("BCDEFGH" * 3)[:20])


class PlayfairTests(unittest.TestCase):
    def test_matrix(self):
        self.assertEqual(["".join(r) for r in build_matrix("criptografie")],
                         ["CRIPTO", "GAFEĂÂ", "BDHÎKL", "MNQSȘȚ", "UVWXYZ"])

    def test_matrix_contains_all_letters_once(self):
        cells = "".join("".join(r) for r in build_matrix("ȘtefanCelMare"))
        self.assertEqual(len(cells), 30)
        self.assertEqual(set(cells), set(ALPHABET) - {"J"})

    def test_digraphs_split_double_letters(self):
        self.assertEqual(prepare_text("Congress shall"),
                         ["CO", "NG", "RE", "SX", "SX", "SH", "AL", "LX"])

    def test_digraphs_odd_length_and_x(self):
        self.assertEqual(prepare_text("abc"), ["AB", "CX"])
        self.assertEqual(prepare_text("xx"), ["XQ", "XQ"])

    def test_three_rules(self):
        key = "criptografie"          # matrix of test_matrix
        # same row: C R -> R I ; last letter wraps to first: O C -> C R
        self.assertEqual(playfair_encrypt("CR", key), "RI")
        self.assertEqual(playfair_encrypt("OC", key), "CR")
        # same column: C(0,0) G(1,0) -> G B ; bottom wraps: U(4,0) C(0,0) -> C G
        self.assertEqual(playfair_encrypt("CG", key), "GB")
        self.assertEqual(playfair_encrypt("UC", key), "CG")
        # rectangle: C(0,0) and A(1,1) -> R(0,1) and G(1,0)
        self.assertEqual(playfair_encrypt("CA", key), "RG")

    def test_round_trip(self):
        message = "Ștefan cel Mare și Sfânt"
        for key in ("securitate", "criptografie", "ȘtefanCelMare"):
            decrypted = playfair_decrypt(playfair_encrypt(message, key), key)
            self.assertTrue(decrypted.startswith("ȘTEFANCELMARE"))
            self.assertEqual(len(decrypted) % 2, 0)

    def test_invalid_cryptogram(self):
        with self.assertRaises(InvalidCharacterError):
            playfair_decrypt("ABC", "securitate")      # odd length
        with self.assertRaises(InvalidCharacterError):
            playfair_decrypt("AAB C", "securitate")


if __name__ == "__main__":
    unittest.main()
