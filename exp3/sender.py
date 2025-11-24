# sender.py
import socket
from crypto_utils import rsa_encrypt

RECV_HOST = "127.0.0.1"
RECV_PORT = 4444

def main():
    print("=== SENDER ===")

    n = int(input("Enter Receiver's public key n: "))
    e = int(input("Enter Receiver's public key e: "))
    receiver_pub = (n, e)

    msg = input("Enter message: ")

    cipher_list = []
    for ch in msg:
        m = ord(ch)     # Convert char → ASCII int
        c = rsa_encrypt(m, receiver_pub)
        cipher_list.append(c)

    payload = " ".join(str(x) for x in cipher_list)

    with socket.socket() as s:
        s.connect((RECV_HOST, RECV_PORT))
        s.sendall(payload.encode())
        print("[Sender] Encrypted list sent:", cipher_list)

if __name__ == "__main__":
    main()
