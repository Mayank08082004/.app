# crypto_utils.py
import random

def egcd(a, b):
    r1, r2 = a, b
    s1, s2 = 1, 0
    
    while r2 != 0:
        q = r1 // r2
        r = r1 % r2
        s = s1 - q * s2

        r1, r2 = r2, r
        s1, s2 = s2, s

    return r1, s1%b

def modinv(a, m):
    g, x = egcd(a, m)
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
