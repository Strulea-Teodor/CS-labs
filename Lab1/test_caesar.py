"""Unit tests for caesar.py  (run with:  python -m unittest -v)."""

import unittest

import caesar
from caesar import (
    InvalidCharacterError,
    InvalidKeyError,
    InvalidKeywordError,
    build_permuted_alphabet,
    decrypt,
    decrypt_with_keyword,
    encrypt,
    encrypt_with_keyword,
    normalize_text,
    validate_key,
)


class AlphabetTests(unittest.TestCase):
    def test_alphabet_has_31_letters(self):
        self.assertEqual(caesar.N, 31)
        self.assertEqual(len(set(caesar.ALPHABET)), 31)

    def test_table_2_encoding(self):
        self.assertEqual(caesar.LETTER_TO_CODE["A"], 0)
        self.assertEqual(caesar.LETTER_TO_CODE["Ă"], 1)
        self.assertEqual(caesar.LETTER_TO_CODE["Â"], 2)
        self.assertEqual(caesar.LETTER_TO_CODE["Î"], 11)
        self.assertEqual(caesar.LETTER_TO_CODE["Ș"], 22)
        self.assertEqual(caesar.LETTER_TO_CODE["Ț"], 24)
        self.assertEqual(caesar.LETTER_TO_CODE["Z"], 30)


class NormalisationTests(unittest.TestCase):
    def test_uppercase_and_spaces_removed(self):
        self.assertEqual(normalize_text("cifrul cezar"), "CIFRULCEZAR")

    def test_romanian_diacritics(self):
        self.assertEqual(normalize_text("ș ț ă â î"), "ȘȚĂÂÎ")

    def test_cedilla_variants_accepted(self):
        self.assertEqual(normalize_text("Şţ"), "ȘȚ")

    def test_invalid_character_reports_position(self):
        with self.assertRaises(InvalidCharacterError) as ctx:
            normalize_text("ab3c")
        self.assertEqual(ctx.exception.character, "3")
        self.assertEqual(ctx.exception.position, 3)


class KeyValidationTests(unittest.TestCase):
    def test_valid_keys(self):
        self.assertEqual(validate_key("1"), 1)
        self.assertEqual(validate_key(30), 30)

    def test_invalid_keys(self):
        for bad in ("0", "31", "-3", "abc", "", "2.5"):
            with self.assertRaises(InvalidKeyError):
                validate_key(bad)


class CaesarTests(unittest.TestCase):
    def test_handout_example_romanian_alphabet(self):
        # Hand check with Table 2 (n = 31, k = 3):
        # C(4)->F(7), I(10)->K(13), F(7)->I(10), R(20)->T(23), U(25)->X(28),
        # L(14)->O(17), C->F, E(6)->H(9), Z(30)->(33 mod 31 = 2)->Â, A->B, R->T
        self.assertEqual(encrypt("cifrul cezar", 3), "FKITXOFHÂBT")

    def test_round_trip_all_keys(self):
        message = "ȘTIINȚA CRIPTOGRAFIEI ÎN ROMÂNĂ"
        for key in range(1, 31):
            self.assertEqual(decrypt(encrypt(message, key), key),
                             normalize_text(message))

    def test_wrap_around(self):
        self.assertEqual(encrypt("Z", 1), "A")
        self.assertEqual(decrypt("A", 1), "Z")


class PermutedAlphabetTests(unittest.TestCase):
    def test_build_permuted_alphabet(self):
        self.assertEqual(build_permuted_alphabet("criptografie"),
                         "CRIPTOGAFEĂÂBDHÎJKLMNQSȘȚUVWXYZ")

    def test_permuted_alphabet_is_a_permutation(self):
        permuted = build_permuted_alphabet("ȘTIINȚAȘI")
        self.assertEqual(len(permuted), 31)
        self.assertEqual(sorted(permuted), sorted(caesar.ALPHABET))

    def test_keyword_too_short(self):
        with self.assertRaises(InvalidKeywordError):
            build_permuted_alphabet("abc")

    def test_keyword_invalid_character(self):
        with self.assertRaises(InvalidCharacterError):
            build_permuted_alphabet("parola123")

    def test_round_trip_two_keys(self):
        message = "CIFRUL CEZAR CU PERMUTARE"
        cipher = encrypt_with_keyword(message, 17, "criptografie")
        self.assertNotEqual(cipher, encrypt(message, 17))
        self.assertEqual(decrypt_with_keyword(cipher, 17, "criptografie"),
                         normalize_text(message))


if __name__ == "__main__":
    unittest.main()
