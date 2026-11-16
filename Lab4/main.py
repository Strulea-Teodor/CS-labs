"""Console program for Laboratory Work No. 4, task 2.10 (DES: computing R_i)."""
import sys

import des_round as des

# Windows consoles and pipes may use a legacy code page.
for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        _stream.reconfigure(encoding="utf-8")

LINE = "=" * 72


def ask_choice(prompt, options):
    while True:
        value = input(prompt).strip().upper()
        if value in options:
            return value
        print(f"  Invalid choice: enter one of {', '.join(options)}.")


def ask_round():
    while True:
        try:
            return des.parse_round(input("Enter the round number i (1-16): "))
        except des.DesInputError as error:
            print(f"  Invalid round: {error}.")


def ask_block(label, what):
    while True:
        try:
            return des.parse_block(
                input(f"Enter {label} (32 bits or 8 hex digits): "), what)
        except des.DesInputError as error:
            print(f"  Invalid input: {error}.")


def main():
    print(LINE)
    print(" Laboratory Work No. 4 - DES, task 2.10: R(i) = L(i-1) XOR P(S(B))")
    print(LINE)
    i = ask_round()
    mode = ask_choice("Input data  [M] enter manually  [R] generate randomly: ",
                      ("M", "R"))
    if mode == "M":
        s_output = ask_block("S1(B1)...S8(B8)", "S-box output")
        l_prev = ask_block(f"L{i - 1}", f"value of L{i - 1}")
    else:
        s_output, l_prev = des.random_block(), des.random_block()
        print("  The input data were generated randomly.")

    print()
    print("Step 1. Input data")
    print(f"  S1(B1)...S8(B8) = {des.group(s_output)}  (hex {des.to_hex(s_output)})")
    print(f"  L{i - 1:<2}             = {des.group(l_prev)}  (hex {des.to_hex(l_prev)})")
    print(des.s_boxes_text(s_output))

    print()
    print("Step 2. Table of the permutation P (bit j of f = bit P[j] of S)")
    print(des.p_table_text())

    f, r = des.compute_r(s_output, l_prev)
    print()
    print("Step 3. Applying the permutation P to the S-box output")
    print(des.permutation_steps_text(s_output))
    print(f"  f(R{i - 1}, K{i}) = P(S) = {des.group(f)}  (hex {des.to_hex(f)})")

    print()
    print(f"Step 4. R{i} = L{i - 1} XOR f(R{i - 1}, K{i})")
    print(f"  L{i - 1:<2}  = {des.group(l_prev)}")
    print(f"  f    = {des.group(f)}")
    print("         " + "-" * 39)
    print(f"  R{i:<2}  = {des.group(r)}")

    print()
    print(f"Result: R{i} = {des.group(r)}  (hex {des.to_hex(r)})")


if __name__ == "__main__":
    main()
