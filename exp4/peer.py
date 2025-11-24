# peer.py
import socket
import threading
import json
import random
import sys
import os
from math import gcd

TPE_HOST = "127.0.0.1"
TPE_PORT = 4000

# Fixed ports for 4 peers
PEER_PORTS = {
    "Alice": 5001,
    "Bob": 5002,
    "Charlie": 5003,
    "David": 5004,
}

# ---------- Math helpers (for RSA) ----------

def egcd(a, b):
    if b == 0:
        return a, 1, 0
    g, x1, y1 = egcd(b, a % b)
    return g, y1, x1 - (a // b) * y1

def modinv(a, m):
    g, x, _ = egcd(a, m)
    if g != 1:
        raise ValueError("No inverse")
    return x % m

# ---------- RSA (simple, NOT secure) ----------

def generate_rsa_keys():
    # Small primes for simplicity
    primes = [101, 103, 107, 109, 113, 127, 131, 137, 139]
    p = random.choice(primes)
    q = random.choice([x for x in primes if x != p])
    n = p * q
    phi = (p - 1) * (q - 1)
    e = 17
    while gcd(e, phi) != 1:
        e += 2
    d = modinv(e, phi)
    return (n, e), (n, d)   # (public, private)

def rsa_encrypt(m, pub):
    n, e = pub
    return pow(m, e, n)

def rsa_decrypt(c, priv):
    n, d = priv
    return pow(c, d, n)

# ---------- Symmetric: Caesar ("teaser") cipher ----------

def caesar_encrypt(text, shift):
    res = ""
    shift = shift % 26
    for ch in text:
        if 'a' <= ch <= 'z':
            res += chr((ord(ch) - ord('a') + shift) % 26 + ord('a'))
        elif 'A' <= ch <= 'Z':
            res += chr((ord(ch) - ord('A') + shift) % 26 + ord('A'))
        else:
            res += ch
    return res

def caesar_decrypt(text, shift):
    return caesar_encrypt(text, -shift)

# ---------- Keyring helpers ----------

def load_keyring(name):
    fname = f"keyring_{name}.json"
    if os.path.exists(fname):
        with open(fname, "r") as f:
            return json.load(f)
    return {}

def save_keyring(name, keyring):
    fname = f"keyring_{name}.json"
    with open(fname, "w") as f:
        json.dump(keyring, f)

# ---------- Talk to TPE ----------

def register_with_tpe(identity, pub):
    n, e = pub
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((TPE_HOST, TPE_PORT))
        msg = f"REGISTER {identity} {n} {e}\n"
        s.sendall(msg.encode())
        resp = s.recv(1024).decode().strip()
        print("TPE response:", resp)

def get_key_from_tpe(identity):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((TPE_HOST, TPE_PORT))
        msg = f"GETKEY {identity}\n"
        s.sendall(msg.encode())
        resp = s.recv(1024).decode().strip().split()
        if resp[0] == "KEY":
            name = resp[1]
            n = int(resp[2])
            e = int(resp[3])
            return (n, e)
        else:
            print("Key not found for", identity)
            return None

# ---------- Peer class ----------

class Peer:
    def __init__(self, name):
        self.name = name
        if name not in PEER_PORTS:
            print("Unknown peer name. Use one of:", list(PEER_PORTS.keys()))
            sys.exit(1)

        self.port = PEER_PORTS[name]
        self.pub, self.priv = generate_rsa_keys()
        print(f"{name} RSA public key (n, e):", self.pub)

        # keyring[other_name] = [n, e]
        self.keyring = load_keyring(name)
        self.shared_secret = None   # integer secret from handshake
        self.symmetric_key = None   # Caesar shift

    # Store/get other peers' keys
    def ensure_key(self, other_name):
        if other_name in self.keyring:
            n, e = self.keyring[other_name]
            return (n, e)
        pub = get_key_from_tpe(other_name)
        if pub:
            self.keyring[other_name] = pub
            save_keyring(self.name, self.keyring)
        return pub

    # Digital signature on a number
    def sign_number(self, num):
        # sig = num^d mod n
        _, d = self.priv
        return pow(num, d, self.priv[0])

    def verify_number(self, num, sig, other_pub):
        n, e = other_pub
        return pow(sig, e, n) == num

    # ---------- Server side (receiver) ----------

    def start_server(self):
        def run_server():
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(("127.0.0.1", self.port))
                s.listen()
                print(f"{self.name} listening on 127.0.0.1:{self.port}")
                while True:
                    conn, addr = s.accept()
                    threading.Thread(target=self.handle_connection,
                                     args=(conn, addr), daemon=True).start()
        threading.Thread(target=run_server, daemon=True).start()

    def handle_connection(self, conn, addr):
        with conn:
            role = conn.recv(1024).decode().strip()
            if role == "HANDSHAKE":
                self.handle_handshake(conn)
            elif role == "DATA":
                self.handle_data(conn)

    def handle_handshake(self, conn):
        # Receive: sender_name, cipher_secret, cipher_sig
        sender_name = conn.recv(1024).decode().strip()
        parts = conn.recv(1024).decode().strip().split()
        cipher_sec = int(parts[0])
        cipher_sig = int(parts[1])

        sender_pub = self.ensure_key(sender_name)
        if not sender_pub:
            print("Cannot verify sender, missing public key.")
            return

        # Decrypt using own private key
        secret = rsa_decrypt(cipher_sec, self.priv)
        sig = rsa_decrypt(cipher_sig, self.priv)

        # Verify signature using sender's public key
        if self.verify_number(secret, sig, sender_pub):
            print(f"[{self.name}] Handshake OK with {sender_name}, secret =", secret)
            self.shared_secret = secret
            self.symmetric_key = secret % 26   # make Caesar shift
            conn.sendall(b"HS_OK\n")
        else:
            print(f"[{self.name}] Handshake FAILED with {sender_name}")
            conn.sendall(b"HS_FAIL\n")

    def handle_data(self, conn):
        # Receive: sender_name, cipher_text, sig
        sender_name = conn.recv(1024).decode().strip()
        cipher_text = conn.recv(4096).decode().rstrip("\n")
        sig_str = conn.recv(1024).decode().strip()
        sig = int(sig_str)

        if self.symmetric_key is None:
            print("No symmetric key established. Cannot decrypt.")
            return

        sender_pub = self.ensure_key(sender_name)
        if not sender_pub:
            print("Missing sender public key, cannot verify signature.")
            return

        # Decrypt message with Caesar
        plain = caesar_decrypt(cipher_text, self.symmetric_key)

        # Verify signature on sum of ords of ciphertext
        msg_num = sum(ord(c) for c in cipher_text)

        if self.verify_number(msg_num, sig, sender_pub):
            print(f"[{self.name}] Received secure message from {sender_name}")
            print(f"  Ciphertext: {cipher_text}")
            print(f"  Plaintext : {plain}")
            print("  Signature verified.")
        else:
            print(f"[{self.name}] Signature verification FAILED for message from {sender_name}")

    # ---------- Client side (sender) ----------

    def do_handshake_as_sender(self, receiver_name):
        receiver_pub = self.ensure_key(receiver_name)
        if not receiver_pub:
            print("Cannot get receiver public key.")
            return

        # "Diffie-Hellman secret" simplified: just a random secret integer
        secret = random.randint(2, 50)

        # Digital signature: sign secret with own private key
        sig = self.sign_number(secret)

        # Encrypt secret & signature with receiver's public key
        cipher_sec = rsa_encrypt(secret, receiver_pub)
        cipher_sig = rsa_encrypt(sig, receiver_pub)

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect(("127.0.0.1", PEER_PORTS[receiver_name]))
            s.sendall(b"HANDSHAKE\n")
            s.sendall((self.name + "\n").encode())
            s.sendall(f"{cipher_sec} {cipher_sig}\n".encode())

            resp = s.recv(1024).decode().strip()
            if resp == "HS_OK":
                print(f"[{self.name}] Handshake success with {receiver_name}. Secret =", secret)
                self.shared_secret = secret
                self.symmetric_key = secret % 26
            else:
                print(f"[{self.name}] Handshake failed with {receiver_name}")

    def send_secure_message(self, receiver_name, message):
        if self.symmetric_key is None:
            print("No symmetric key. Run handshake first.")
            return

        # Encrypt with Caesar cipher (symmetric key)
        cipher_text = caesar_encrypt(message, self.symmetric_key)

        # Sign numeric representation of ciphertext
        msg_num = sum(ord(c) for c in cipher_text)
        sig = self.sign_number(msg_num)

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect(("127.0.0.1", PEER_PORTS[receiver_name]))
            s.sendall(b"DATA\n")
            s.sendall((self.name + "\n").encode())
            s.sendall((cipher_text + "\n").encode())
            s.sendall((str(sig) + "\n").encode())

        print(f"[{self.name}] Sent secure message to {receiver_name}")

# ---------- Main menu ----------

def main():
    if len(sys.argv) != 2:
        print("Usage: python peer.py <Name>")
        print("Name should be one of:", list(PEER_PORTS.keys()))
        return

    name = sys.argv[1]
    peer = Peer(name)
    peer.start_server()

    while True:
        print("\n--- Menu for", name, "---")
        print("1. Register my public key with TPE")
        print("2. Perform SSL-1 style handshake with another peer")
        print("3. Send secure encrypted + signed message to another peer")
        print("4. Exit")
        choice = input("Enter choice: ").strip()

        if choice == "1":
            register_with_tpe(name, peer.pub)
        elif choice == "2":
            other = input("Enter receiver name (Alice/Bob/Charlie/David): ").strip()
            peer.do_handshake_as_sender(other)
        elif choice == "3":
            other = input("Enter receiver name (Alice/Bob/Charlie/David): ").strip()
            msg = input("Enter message: ")
            peer.send_secure_message(other, msg)
        elif choice == "4":
            print("Exiting...")
            break
        else:
            print("Invalid choice.")

if __name__ == "__main__":
    main()
