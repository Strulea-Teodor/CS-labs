"""Laboratory Work No. 4 - Block ciphers. The DES algorithm.

Task 2.10 (variant 10): in round i of DES the output of the S-boxes
S1(B1)S2(B2)...S8(B8) (32 bits) and the left half L(i-1) (32 bits) are known.
The right half R(i) has to be computed:

    f    = P( S1(B1)S2(B2)...S8(B8) )
    R(i) = L(i-1) XOR f
"""
import secrets

BLOCK_BITS = 32
ROUNDS = 16

# Permutation P of the DES round function (FIPS 46-3), positions counted from 1:
# bit j of the result is bit P_TABLE[j - 1] of the S-box output.
P_TABLE = [
    16,  7, 20, 21,
    29, 12, 28, 17,
     1, 15, 23, 26,
     5, 18, 31, 10,
     2,  8, 24, 14,
    32, 27,  3,  9,
    19, 13, 30,  6,
    22, 11,  4, 25,
]

HEX_DIGITS = "0123456789ABCDEF"
ALLOWED = ("enter 32 binary digits (0 or 1) or 8 hexadecimal digits "
           "(0-9, A-F); spaces are ignored")


class DesInputError(ValueError):
    """Raised when a value typed by the user is not valid."""


def parse_block(text, what="value"):
    """Convert user input (32 binary digits or 8 hex digits) to a 32-bit string."""
    cleaned = "".join(ch for ch in text if not ch.isspace() and ch != "_")
    if cleaned[:2] in ("0x", "0X"):
        cleaned = cleaned[2:]
    if not cleaned:
        raise DesInputError(f"the {what} is empty: {ALLOWED}")
    upper = cleaned.upper()
    for position, ch in enumerate(upper, start=1):
        if ch not in HEX_DIGITS:
            raise DesInputError(
                f"invalid character {cleaned[position - 1]!r} at position "
                f"{position} of the {what}: {ALLOWED}")
    if len(upper) == BLOCK_BITS:
        for position, ch in enumerate(upper, start=1):
            if ch not in "01":
                raise DesInputError(
                    f"invalid binary digit {ch!r} at position {position} of the "
                    f"{what}: {ALLOWED}")
        return upper
    if len(upper) == BLOCK_BITS // 4:
        return "".join(format(HEX_DIGITS.index(ch), "04b") for ch in upper)
    raise DesInputError(
        f"the {what} must have exactly 32 bits (got {len(upper)} digits): {ALLOWED}")


def parse_round(text):
    """Validate the round number i (1..16)."""
    try:
        number = int(text.strip())
    except ValueError:
        raise DesInputError(
            f"the round must be an integer between 1 and {ROUNDS} "
            f"(got {text.strip()!r})") from None
    if not 1 <= number <= ROUNDS:
        raise DesInputError(
            f"the round must be an integer between 1 and {ROUNDS} (got {number})")
    return number


def random_block():
    """A random 32-bit value as a string of bits."""
    return format(secrets.randbits(BLOCK_BITS), "032b")


def permute(bits, table):
    """Bit j of the result is bit table[j-1] of the input (positions from 1)."""
    return "".join(bits[source - 1] for source in table)


def xor_bits(a, b):
    """Bitwise addition modulo 2 of two bit strings of equal length."""
    return "".join("1" if x != y else "0" for x, y in zip(a, b))


def compute_r(s_output, l_prev):
    """Return (f, R_i): f = P(S-box output), R_i = L_(i-1) XOR f."""
    if len(s_output) != BLOCK_BITS or len(l_prev) != BLOCK_BITS:
        raise DesInputError("both values must have exactly 32 bits")
    f = permute(s_output, P_TABLE)
    return f, xor_bits(l_prev, f)


def group(bits, size=4):
    """'01011100' -> '0101 1100'."""
    return " ".join(bits[i:i + size] for i in range(0, len(bits), size))


def to_hex(bits):
    return "".join(HEX_DIGITS[int(bits[i:i + 4], 2)] for i in range(0, len(bits), 4))


# ------------------------------------------------------------- text output
def p_table_text():
    rows = ["       " + "".join(f"{P_TABLE[r * 4 + c]:>4}" for c in range(4))
            for r in range(8)]
    return "\n".join(rows)


def s_boxes_text(s_output):
    """The 8 groups S1(B1) ... S8(B8) with their bit positions and values."""
    lines = []
    for j in range(8):
        nibble = s_output[j * 4:j * 4 + 4]
        lines.append(f"  S{j + 1}(B{j + 1}) = {nibble}  (decimal {int(nibble, 2):>2}, "
                     f"hex {to_hex(nibble)})   bits {j * 4 + 1:>2}-{j * 4 + 4:>2}")
    return "\n".join(lines)


def permutation_steps_text(s_output):
    """For every bit of f: its position, the source position in S and its value."""
    lines = []
    for start in (0, 16):
        cols = range(start, start + 16)
        lines.append("  bit of f   " + "".join(f"{j + 1:>3}" for j in cols))
        lines.append("  bit of S   " + "".join(f"{P_TABLE[j]:>3}" for j in cols))
        lines.append("  value      " + "".join(f"{s_output[P_TABLE[j] - 1]:>3}" for j in cols))
        if start == 0:
            lines.append("")
    return "\n".join(lines)
