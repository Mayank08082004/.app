# crypto_utils.py
import random

def egcd(a, b):
    if b == 0:
        return a, 1, 0
    g, x1, y1 = egcd(b, a % b)
    return g, y1, x1 - (a // b) * y1

def modinv(a, m):
    g, x, _ = egcd(a, m)
    if g != 1:
        return None
    return x % m

def generate_rsa_keys():
    primes = [11, 13, 17, 19, 23, 29, 31]
    p = random.choice(primes)
    q = random.choice([x for x in primes if x != p])
    n = p * q
    phi = (p - 1) * (q - 1)

    e = 3
    while egcd(e, phi)[0] != 1:
        e += 2

    d = modinv(e, phi)
    return (n, e), (n, d)

def rsa_encrypt(m, pub):
    n, e = pub
    return pow(m, e, n)

def rsa_decrypt(c, priv):
    n, d = priv
    return pow(c, d, n)
