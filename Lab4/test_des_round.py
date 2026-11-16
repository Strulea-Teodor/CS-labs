"""Unit tests for task 2.10.  A complete reference DES is included only to
check that compute_r gives the right R_i in every one of the 16 rounds."""
import unittest

from des_round import (P_TABLE, DesInputError, compute_r, group, parse_block,
                       parse_round, permute, random_block, to_hex, xor_bits)

# ----------------------------------------------------- reference DES tables
IP = [58, 50, 42, 34, 26, 18, 10, 2, 60, 52, 44, 36, 28, 20, 12, 4,
      62, 54, 46, 38, 30, 22, 14, 6, 64, 56, 48, 40, 32, 24, 16, 8,
      57, 49, 41, 33, 25, 17, 9, 1, 59, 51, 43, 35, 27, 19, 11, 3,
      61, 53, 45, 37, 29, 21, 13, 5, 63, 55, 47, 39, 31, 23, 15, 7]
FP = [40, 8, 48, 16, 56, 24, 64, 32, 39, 7, 47, 15, 55, 23, 63, 31,
      38, 6, 46, 14, 54, 22, 62, 30, 37, 5, 45, 13, 53, 21, 61, 29,
      36, 4, 44, 12, 52, 20, 60, 28, 35, 3, 43, 11, 51, 19, 59, 27,
      34, 2, 42, 10, 50, 18, 58, 26, 33, 1, 41, 9, 49, 17, 57, 25]
E = [32, 1, 2, 3, 4, 5, 4, 5, 6, 7, 8, 9, 8, 9, 10, 11, 12, 13,
     12, 13, 14, 15, 16, 17, 16, 17, 18, 19, 20, 21, 20, 21, 22, 23, 24, 25,
     24, 25, 26, 27, 28, 29, 28, 29, 30, 31, 32, 1]
PC1 = [57, 49, 41, 33, 25, 17, 9, 1, 58, 50, 42, 34, 26, 18,
       10, 2, 59, 51, 43, 35, 27, 19, 11, 3, 60, 52, 44, 36,
       63, 55, 47, 39, 31, 23, 15, 7, 62, 54, 46, 38, 30, 22,
       14, 6, 61, 53, 45, 37, 29, 21, 13, 5, 28, 20, 12, 4]
PC2 = [14, 17, 11, 24, 1, 5, 3, 28, 15, 6, 21, 10, 23, 19, 12, 4,
       26, 8, 16, 7, 27, 20, 13, 2, 41, 52, 31, 37, 47, 55, 30, 40,
       51, 45, 33, 48, 44, 49, 39, 56, 34, 53, 46, 42, 50, 36, 29, 32]
SHIFTS = [1, 1, 2, 2, 2, 2, 2, 2, 1, 2, 2, 2, 2, 2, 2, 1]
S = [
    [[14, 4, 13, 1, 2, 15, 11, 8, 3, 10, 6, 12, 5, 9, 0, 7],
     [0, 15, 7, 4, 14, 2, 13, 1, 10, 6, 12, 11, 9, 5, 3, 8],
     [4, 1, 14, 8, 13, 6, 2, 11, 15, 12, 9, 7, 3, 10, 5, 0],
     [15, 12, 8, 2, 4, 9, 1, 7, 5, 11, 3, 14, 10, 0, 6, 13]],
    [[15, 1, 8, 14, 6, 11, 3, 4, 9, 7, 2, 13, 12, 0, 5, 10],
     [3, 13, 4, 7, 15, 2, 8, 14, 12, 0, 1, 10, 6, 9, 11, 5],
     [0, 14, 7, 11, 10, 4, 13, 1, 5, 8, 12, 6, 9, 3, 2, 15],
     [13, 8, 10, 1, 3, 15, 4, 2, 11, 6, 7, 12, 0, 5, 14, 9]],
    [[10, 0, 9, 14, 6, 3, 15, 5, 1, 13, 12, 7, 11, 4, 2, 8],
     [13, 7, 0, 9, 3, 4, 6, 10, 2, 8, 5, 14, 12, 11, 15, 1],
     [13, 6, 4, 9, 8, 15, 3, 0, 11, 1, 2, 12, 5, 10, 14, 7],
     [1, 10, 13, 0, 6, 9, 8, 7, 4, 15, 14, 3, 11, 5, 2, 12]],
    [[7, 13, 14, 3, 0, 6, 9, 10, 1, 2, 8, 5, 11, 12, 4, 15],
     [13, 8, 11, 5, 6, 15, 0, 3, 4, 7, 2, 12, 1, 10, 14, 9],
     [10, 6, 9, 0, 12, 11, 7, 13, 15, 1, 3, 14, 5, 2, 8, 4],
     [3, 15, 0, 6, 10, 1, 13, 8, 9, 4, 5, 11, 12, 7, 2, 14]],
    [[2, 12, 4, 1, 7, 10, 11, 6, 8, 5, 3, 15, 13, 0, 14, 9],
     [14, 11, 2, 12, 4, 7, 13, 1, 5, 0, 15, 10, 3, 9, 8, 6],
     [4, 2, 1, 11, 10, 13, 7, 8, 15, 9, 12, 5, 6, 3, 0, 14],
     [11, 8, 12, 7, 1, 14, 2, 13, 6, 15, 0, 9, 10, 4, 5, 3]],
    [[12, 1, 10, 15, 9, 2, 6, 8, 0, 13, 3, 4, 14, 7, 5, 11],
     [10, 15, 4, 2, 7, 12, 9, 5, 6, 1, 13, 14, 0, 11, 3, 8],
     [9, 14, 15, 5, 2, 8, 12, 3, 7, 0, 4, 10, 1, 13, 11, 6],
     [4, 3, 2, 12, 9, 5, 15, 10, 11, 14, 1, 7, 6, 0, 8, 13]],
    [[4, 11, 2, 14, 15, 0, 8, 13, 3, 12, 9, 7, 5, 10, 6, 1],
     [13, 0, 11, 7, 4, 9, 1, 10, 14, 3, 5, 12, 2, 15, 8, 6],
     [1, 4, 11, 13, 12, 3, 7, 14, 10, 15, 6, 8, 0, 5, 9, 2],
     [6, 11, 13, 8, 1, 4, 10, 7, 9, 5, 0, 15, 14, 2, 3, 12]],
    [[13, 2, 8, 4, 6, 15, 11, 1, 10, 9, 3, 14, 5, 0, 12, 7],
     [1, 15, 13, 8, 10, 3, 7, 4, 12, 5, 6, 11, 0, 14, 9, 2],
     [7, 11, 4, 1, 9, 12, 14, 2, 0, 6, 10, 13, 15, 3, 5, 8],
     [2, 1, 14, 7, 4, 10, 8, 13, 15, 12, 9, 0, 3, 5, 6, 11]],
]


def reference_des(message_hex, key_hex):
    """Full DES. Returns (ciphertext_hex, [(L_prev, S_output, R_i) per round])."""
    bits = lambda h: format(int(h, 16), "064b")
    key = permute(bits(key_hex), PC1)
    c, d = key[:28], key[28:]
    block = permute(bits(message_hex), IP)
    left, right = block[:32], block[32:]
    trace = []
    for shift in SHIFTS:
        c, d = c[shift:] + c[:shift], d[shift:] + d[:shift]
        round_key = permute(c + d, PC2)
        b = xor_bits(permute(right, E), round_key)
        s_output = ""
        for j in range(8):
            six = b[j * 6:j * 6 + 6]
            row, col = int(six[0] + six[5], 2), int(six[1:5], 2)
            s_output += format(S[j][row][col], "04b")
        new_right = xor_bits(left, permute(s_output, P_TABLE))
        trace.append((left, s_output, new_right))
        left, right = right, new_right
    return to_hex(permute(right + left, FP)), trace


class ParsingTests(unittest.TestCase):
    def test_binary_and_hex_are_equivalent(self):
        bits = "01011100100000101011010110010111"
        self.assertEqual(parse_block(bits), bits)
        self.assertEqual(parse_block("0101 1100 1000 0010 1011 0101 1001 0111"), bits)
        self.assertEqual(parse_block("5C82B597"), bits)
        self.assertEqual(parse_block("0x5c82b597"), bits)

    def test_hex_made_of_zeros_and_ones(self):
        self.assertEqual(parse_block("10010110"), "0001000000000001" "0000000100010000")

    def test_wrong_length(self):
        for bad in ("101", "5C82B5", "5C82B5971", "0" * 31, "0" * 33):
            with self.assertRaises(DesInputError):
                parse_block(bad)

    def test_invalid_characters(self):
        for bad in ("5C82B59G", "hello!!!", "0101 1100 1000 0010 1011 0101 1001 012", ""):
            with self.assertRaises(DesInputError):
                parse_block(bad)

    def test_error_names_position(self):
        with self.assertRaises(DesInputError) as ctx:
            parse_block("5C82B59G")
        self.assertIn("position 8", str(ctx.exception))

    def test_round_number(self):
        self.assertEqual(parse_round(" 16 "), 16)
        for bad in ("0", "17", "abc", "", "1.5"):
            with self.assertRaises(DesInputError):
                parse_round(bad)


class RoundTests(unittest.TestCase):
    def test_p_table_is_a_permutation(self):
        self.assertEqual(sorted(P_TABLE), list(range(1, 33)))

    def test_permutation_moves_single_bits(self):
        # a single 1 on position 16 of S must arrive on position 1 of f
        s = "0" * 15 + "1" + "0" * 16
        self.assertEqual(permute(s, P_TABLE), "1" + "0" * 31)

    def test_xor(self):
        self.assertEqual(xor_bits("0011", "0101"), "0110")

    def test_known_example(self):
        # round 1 of the classic example M = 0123456789ABCDEF, K = 133457799BBCDFF1
        f, r = compute_r(parse_block("5C82B597"), parse_block("CC00CCFF"))
        self.assertEqual(to_hex(f), "234AA9BB")
        self.assertEqual(to_hex(r), "EF4A6544")
        self.assertEqual(group(r), "1110 1111 0100 1010 0110 0101 0100 0100")

    def test_zero_s_output_leaves_l_unchanged(self):
        l_prev = parse_block("89ABCDEF")
        self.assertEqual(compute_r("0" * 32, l_prev)[1], l_prev)

    def test_xor_is_its_own_inverse(self):
        for _ in range(50):
            s, l_prev = random_block(), random_block()
            f, r = compute_r(s, l_prev)
            self.assertEqual(xor_bits(r, f), l_prev)

    def test_random_block_format(self):
        block = random_block()
        self.assertEqual(len(block), 32)
        self.assertLessEqual(set(block), {"0", "1"})


class ReferenceDesTests(unittest.TestCase):
    VECTORS = [("0123456789ABCDEF", "133457799BBCDFF1", "85E813540F0AB405"),
               ("4E6F772069732074", "0123456789ABCDEF", "3FA40E8A984D4815")]

    def test_reference_des_is_correct(self):
        for message, key, cipher in self.VECTORS:
            self.assertEqual(reference_des(message, key)[0], cipher)

    def test_compute_r_in_all_16_rounds(self):
        for message, key, _ in self.VECTORS:
            for l_prev, s_output, expected_r in reference_des(message, key)[1]:
                self.assertEqual(compute_r(s_output, l_prev)[1], expected_r)


if __name__ == "__main__":
    unittest.main()
