# receiver.py
import socket
from crypto_utils import rsa_decrypt, generate_rsa_keys

HOST = "127.0.0.1"
PORT = 4444

def main():
    print("=== RECEIVER ===")

    pub, priv = generate_rsa_keys()
    print("[Receiver Public Key]:", pub)
    print("[Receiver Private Key]:", priv)
    print("\nGive the public key to sender.")

    with socket.socket() as s:
        s.bind((HOST, PORT))
        s.listen()
        print(f"\n[Receiver] Listening on {HOST}:{PORT}...")

        conn, addr = s.accept()
        with conn:
            print("[Receiver] Connected:", addr)

            data = conn.recv(4096).decode().strip()
            cipher_list = []
            parts = data.split()

            for item in parts:
                cipher_list.append(int(item))

            decrypted_msg = ""
            for c in cipher_list:
                m = rsa_decrypt(c, priv)
                decrypted_msg += chr(m)

            print("\n[Receiver] Decrypted Message:", decrypted_msg)

if __name__ == "__main__":
    main()
