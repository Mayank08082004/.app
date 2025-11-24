def mod_inverse(a, b):
    r1, r2 = a, b
    s1, s2 = 1, 0
    print("\nq   r1   r2   r   t1  t2  t")
    while r2 != 0:
        q = r1 // r2
        r = r1 % r2
        s = s1 - q * s2

        print(q, r1, r2, r, s1, s2, s)

        r1, r2 = r2, r
        s1, s2 = s2, s

    if r1 != 1:
        return None
    
    return s1 % b


# ----------------- MAIN CRT FUNCTIONS ------------------

def to_residues(x, mods):
    return [x % m for m in mods]


def crt_reconstruct(c, mods):
    M = 1
    for m in mods:
        M *= m

    result = 0
    for i in range(len(mods)):
        mi = mods[i]
        Mi = M // mi
        Mi_inv = mod_inverse(Mi, mi)
        result += c[i] * Mi * Mi_inv
    
    return result % M


# ----------------- MENU PROGRAM ------------------

mods = [3, 5, 7]    # You can change these; assume given at initialization
print("Using moduli:", mods)

while True:
    print("\n----- CRT MENU -----")
    print("1. Addition")
    print("2. Subtraction")
    print("3. Multiplication")
    print("4. Division")
    print("5. Exit")

    ch = int(input("Enter choice: "))

    if ch == 5:
        break

    A = int(input("Enter A: "))
    B = int(input("Enter B: "))

    a = to_residues(A, mods)
    b = to_residues(B, mods)

    print("A mod mi =", a)
    print("B mod mi =", b)

    c = []

    if ch == 1:
        c = [(a[i] + b[i]) % mods[i] for i in range(len(mods))]
    elif ch == 2:
        c = [(a[i] - b[i]) % mods[i] for i in range(len(mods))]
    elif ch == 3:
        c = [(a[i] * b[i]) % mods[i] for i in range(len(mods))]
    elif ch == 4:
        # Division = A * inverse(B)
        c = []
        for i in range(len(mods)):
            inv = mod_inverse(b[i], mods[i])
            if inv is None:
                print("Division not possible modulo", mods[i])
                break
            c.append((a[i] * inv) % mods[i])
    else:
        print("Invalid choice!")
        continue

    print("Residue result c =", c)

    final_C = crt_reconstruct(c, mods)
    print("Final answer C =", final_C)
