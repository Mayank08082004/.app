import numpy as np

ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
PLAYFAIR_ALPHABET = "ABCDEFGHIKLMNOPQRSTUVWXYZ" 
# ----------------- Utility: Modular Inverse -----------------
def mod_inverse(a, b):
    r1, r2 = a, b
    s1, s2 = 1, 0
    print("\nq   r1   r2   r   t1  t2  t")
    while r2 != 0:
        q = r1 // r2
        r = r1 % r2
        s = s1 - q * s2

        r1, r2 = r2, r
        s1, s2 = s2, s

    if r1 != 1:
        return None
    
    return s1 % b


# ================= CAESAR CIPHER =================
def caesar_encrypt(text, key):
    res = ""
    for ch in text.upper():
        if ch.isalpha():
            res += ALPHABET[(ALPHABET.index(ch) + key) % 26]
        else:
            res += ch
    return res

def caesar_decrypt(text, key):
    return caesar_encrypt(text, -key)

def caesar_attack(cipher):
    print("\n--- Brute Force Caesar Attack ---")
    for k in range(26):
        print(k, ":", caesar_decrypt(cipher, k))


# ================= MONOALPHABETIC CIPHER =================
def mono_encrypt(text, key_map):
    res = ""
    for ch in text.upper():
        res += key_map.get(ch, ch)
    return res

def mono_decrypt(text, key_map):
    rev = {v: k for k, v in key_map.items()}
    return mono_encrypt(text, rev)


# ================= PLAYFAIR CIPHER =================
def playfair_matrix(key):
    key = key.upper().replace("J", "I")

    clean_key = ""
    for ch in key:
        if ch not in clean_key and ch in PLAYFAIR_ALPHABET:
            clean_key += ch

    for ch in PLAYFAIR_ALPHABET:
        if ch not in clean_key:
            clean_key += ch

    matrix = []
    idx = 0
    for r in range(5):
        row = []
        for c in range(5):
            row.append(clean_key[idx])
            idx += 1
        matrix.append(row)

    return matrix


def find_position(matrix, ch):
    for r in range(5):
        for c in range(5):
            if matrix[r][c] == ch:
                return r, c
    return None


def prepare_text(text):
    text = text.upper().replace("J", "I")
    cleaned = ""
    i = 0

    while i < len(text):
        a = text[i]

        if i + 1 < len(text):
            b = text[i+1]
        else:
            b = "X"

        if a == b:
            cleaned += a + "X"
            i += 1
        else:
            cleaned += a + b
            i += 2

    if len(cleaned) % 2 != 0:
        cleaned += "X"

    return cleaned


def playfair_encrypt(text, key):
    matrix = playfair_matrix(key)
    prepared = prepare_text(text)
    res = ""

    for i in range(0, len(prepared), 2):
        a = prepared[i]
        b = prepared[i+1]

        r1, c1 = find_position(matrix, a)
        r2, c2 = find_position(matrix, b)

        if r1 == r2:
            res += matrix[r1][(c1 + 1) % 5]
            res += matrix[r2][(c2 + 1) % 5]

        elif c1 == c2:
            res += matrix[(r1 + 1) % 5][c1]
            res += matrix[(r2 + 1) % 5][c2]

        else:
            res += matrix[r1][c2]
            res += matrix[r2][c1]

    return res


def playfair_decrypt(cipher, key):
    matrix = playfair_matrix(key)
    res = ""

    for i in range(0, len(cipher), 2):
        a = cipher[i]
        b = cipher[i+1]

        r1, c1 = find_position(matrix, a)
        r2, c2 = find_position(matrix, b)

        if r1 == r2:
            res += matrix[r1][(c1 - 1) % 5]
            res += matrix[r2][(c2 - 1) % 5]

        elif c1 == c2:
            res += matrix[(r1 - 1) % 5][c1]
            res += matrix[(r2 - 1) % 5][c2]

        else:
            res += matrix[r1][c2]
            res += matrix[r2][c1]

    return res


# ================= HILL CIPHER (2x2 and 3x3) =================
def hill_encrypt(text, key_matrix):
    text = text.replace(" ", "").upper()
    n = len(key_matrix)

    while len(text) % n != 0:
        text += "X"

    nums = [ALPHABET.index(c) for c in text]
    cipher = ""

    for i in range(0, len(nums), n):
        block = np.array(nums[i:i+n])
        enc = key_matrix.dot(block) % 26
        cipher += ''.join(ALPHABET[val] for val in enc)
    return cipher


def hill_decrypt(cipher, key_matrix):
    det = int(round(np.linalg.det(key_matrix))) % 26
    det_inv = mod_inverse(det, 26)
    if det_inv is None:
        return "Matrix not invertible!"

    adj = np.round(det * np.linalg.inv(key_matrix)).astype(int) % 26
    inv_matrix = (det_inv * adj) % 26

    nums = [ALPHABET.index(c) for c in cipher]
    n = len(key_matrix)
    plain = ""

    for i in range(0, len(nums), n):
        block = np.array(nums[i:i+n])
        dec = inv_matrix.dot(block) % 26
        plain += ''.join(ALPHABET[val] for val in dec)
    return plain


# ================= VIGENERE CIPHER =================
def vigenere_encrypt(text, key):
    res, j = "", 0
    key = key.upper()
    for ch in text.upper():
        if ch.isalpha():
            k = ALPHABET.index(key[j % len(key)])
            res += ALPHABET[(ALPHABET.index(ch)+k) % 26]
            j += 1
        else:
            res += ch
    return res

def vigenere_decrypt(text, key):
    res, j = "", 0
    key = key.upper()
    for ch in text.upper():
        if ch.isalpha():
            k = ALPHABET.index(key[j % len(key)])
            res += ALPHABET[(ALPHABET.index(ch)-k) % 26]
            j += 1
        else:
            res += ch
    return res


# ================= VERNAM CIPHER =================
def vernam_encrypt(text, key):
    res = ""
    for a, b in zip(text.upper(), key.upper()):
        res += ALPHABET[(ALPHABET.index(a) ^ ALPHABET.index(b)) % 26]
    return res

def vernam_decrypt(cipher, key):
    return vernam_encrypt(cipher, key)


# ================= RAIL FENCE CIPHER =================
def rail_fence_encrypt(text, depth):
    rails = ['' for _ in range(depth)]
    row, step = 0, 1

    for ch in text.replace(" ", ""):
        rails[row] += ch
        if row == 0:
            step = 1
        elif row == depth - 1:
            step = -1
        row += step
    return ''.join(rails)

def rail_fence_decrypt(cipher, depth):
    pattern = [[] for _ in range(depth)]
    row, step = 0, 1

    for i in range(len(cipher)):
        pattern[row].append(i)
        if row == 0:
            step = 1
        elif row == depth - 1:
            step = -1
        row += step

    result = [""] * len(cipher)
    index = 0

    for r in range(depth):
        for pos in pattern[r]:
            result[pos] = cipher[index]
            index += 1

    return ''.join(result)


# ================= MENU =================
while True:
    print("\n===== SUBSTITUTION CIPHERS MENU =====")
    print("1. Caesar Cipher")
    print("2. Monoalphabetic Cipher")
    print("3. Playfair Cipher")
    print("4. Hill Cipher (2x2 or 3x3)")
    print("5. Polyalphabetic (Vigenere / Vernam)")
    print("6. Rail Fence Cipher")
    print("7. Attacks")
    print("8. Exit")

    ch = int(input("Enter choice: "))

    if ch == 8:
        break

    # ---------------- Caesar ----------------
    if ch == 1:
        text = input("Enter text: ")
        key = int(input("Enter key: "))
        enc = caesar_encrypt(text, key)
        dec = caesar_decrypt(enc, key)
        print("Encrypted:", enc)
        print("Decrypted:", dec)

    # ---------------- Monoalphabetic ----------------
    elif ch == 2:
        text = input("Enter text: ")
        mapping = input("Enter 26-letter key (A-Z perm): ").upper()
        key_map = {ALPHABET[i]: mapping[i] for i in range(26)}
        enc = mono_encrypt(text, key_map)
        dec = mono_decrypt(enc, key_map)
        print("Encrypted:", enc)
        print("Decrypted:", dec)

    # ---------------- Playfair ----------------
    elif ch == 3:
        text = input("Enter text: ")
        key = input("Enter key: ")
        enc = playfair_encrypt(text, key)
        dec = playfair_decrypt(enc, key)
        print("Encrypted:", enc)
        print("Decrypted:", dec)

    # ---------------- Hill (2x2, 3x3) ----------------
    elif ch == 4:
        text = input("Enter text: ").upper()
        n = int(input("Enter matrix size (2 or 3): "))

        print(f"Enter {n}x{n} key matrix row-wise:")
        mat = [list(map(int, input().split())) for _ in range(n)]
        key_matrix = np.array(mat)

        enc = hill_encrypt(text, key_matrix)
        dec = hill_decrypt(enc, key_matrix)

        print("Encrypted:", enc)
        print("Decrypted:", dec)

    # ---------------- Polyalphabetic ----------------
    elif ch == 5:
        text = input("Enter text: ")
        print("1. Vigenere\n2. Vernam")
        t = int(input("Choose method: "))
        key = input("Enter key: ")

        if t == 1:
            enc = vigenere_encrypt(text, key)
            dec = vigenere_decrypt(enc, key)
        else:
            enc = vernam_encrypt(text, key)
            dec = vernam_decrypt(enc, key)

        print("Encrypted:", enc)
        print("Decrypted:", dec)

    # ---------------- Rail Fence ----------------
    elif ch == 6:
        text = input("Enter text: ")
        depth = int(input("Enter depth: "))
        enc = rail_fence_encrypt(text, depth)
        dec = rail_fence_decrypt(enc, depth)
        print("Encrypted:", enc)
        print("Decrypted:", dec)

    # ---------------- Attacks ----------------
    elif ch == 7:
        cipher = input("Enter cipher text: ")

        print("\n1. Caesar Attack\n2. Monoalphabetic Attack\n3. Playfair Attack\n4. Hill Attack\n5. Vigenere Attack\n6. Vernam Attack\n7. Rail Fence Attack")
        a = int(input("Choose attack type: "))

        if a == 1:
            caesar_attack(cipher)
        else:
            print("Brute force attack NOT possible for this cipher.")
