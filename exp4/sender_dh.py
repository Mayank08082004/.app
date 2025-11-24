# sender_dh.py
import socket
import random

HOST = "127.0.0.1"
PORT = 5000

# shared prime & generator
p = 23
g = 5

def main():
    print("=== SENDER (Diffie–Hellman) ===")
    print(f"Using p={p}, g={g}")

    b = random.randint(2, p-2)   # private key
    B = pow(g, b, p)             # public key

    print("\n[Sender] Private key b:", b)
    print("[Sender] Public key B:", B)

    with socket.socket() as s:
        s.connect((HOST, PORT))
        
        # send our public key to receiver
        s.sendall(str(B).encode())
        print("[Sender] Sent public key B.")

        # receive receiver's public key A
        A = int(s.recv(1024).decode().strip())
        print("[Sender] Received Receiver’s public key A:", A)

        # compute shared key
        shared_key = pow(A, b, p)
        print("\n[Sender] Shared key computed:", shared_key)

if __name__ == "__main__":
    main()
