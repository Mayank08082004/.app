# crypto_utils.py
import random

# ---------- GCD & Modular Inverse (for RSA) ----------
def egcd(a, b):
    if b == 0:
        return a, 1, 0
    g, x1, y1 = egcd(b, a % b)
    x = y1
    y = x1 - (a // b) * y1
    return g, x, y

def modinv(a, m):
    g, x, _ = egcd(a, m)
    if g != 1:
        return None
    return x % m

# ---------- Simple RSA Key Generation ----------
def generate_rsa_keys():
    primes = [11, 13, 17, 19, 23, 29, 31]
    p = random.choice(primes)
    q = random.choice([x for x in primes if x != p])
    n = p * q
    phi = (p - 1) * (q - 1)

    e = 3
    while e < phi:
        g, _, _ = egcd(e, phi)
        if g == 1:
            break
        e += 2

    d = modinv(e, phi)
    return (n, e, d)

def rsa_encrypt(m_int, n, e):
    return pow(m_int, e, n)

def rsa_decrypt(c_int, n, d):
    return pow(c_int, d, n)

# ---------- CAESAR CIPHER (Symmetric Encryption) ----------
ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

def caesar_encrypt_msg(text, key):
    res = ""
    for ch in text.upper():
        if ch.isalpha():
            res += ALPHABET[(ALPHABET.index(ch) + key) % 26]
        else:
            res += ch
    return res

def caesar_decrypt_msg(cipher, key):
    return caesar_encrypt_msg(cipher, -key)
