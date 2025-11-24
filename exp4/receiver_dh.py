# receiver_dh.py
import socket
import random

HOST = "127.0.0.1"
PORT = 5000

# shared prime & generator (small for demo)
p = 23
g = 5

def main():
    print("=== RECEIVER (Diffie–Hellman) ===")
    print(f"Using p={p}, g={g}")

    a = random.randint(2, p-2)  # private key
    A = pow(g, a, p)            # public key

    print("\n[Receiver] Private key a:", a)
    print("[Receiver] Public key A:", A)

    with socket.socket() as s:
        s.bind((HOST, PORT))
        s.listen()
        print(f"\n[Receiver] Waiting on {HOST}:{PORT} ...")
        
        conn, addr = s.accept()
        with conn:
            print("[Receiver] Connected from", addr)

            sender_B = int(conn.recv(1024).decode().strip())
            print("[Receiver] Received Sender’s public key B:", sender_B)

            # Send receiver public key A
            conn.sendall(str(A).encode())

            # Compute shared key
            shared_key = pow(sender_B, a, p)
            print("\n[Receiver] Shared key computed:", shared_key)

if __name__ == "__main__":
    main()
