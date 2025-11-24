# receiver.py
import socket
from crypto_utils import generate_rsa_keys, rsa_decrypt, caesar_decrypt_msg

THIRD_HOST = "127.0.0.1"
THIRD_PORT = 4444

RECV_HOST = "127.0.0.1"
RECV_PORT = 3333

def register(name, n, e):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((THIRD_HOST, THIRD_PORT))
        s.sendall(f"REGISTER {name} {n} {e}\n".encode())
        print("[TPA]:", s.recv(1024).decode().strip())

def wait_message(n, d):
    print("[Receiver] Waiting on port", RECV_PORT)

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((RECV_HOST, RECV_PORT))
        s.listen()
        conn, addr = s.accept()

        with conn:
            data = conn.recv(2048).decode().strip().split("\n")
            enc_key = int(data[0])
            cipher = data[1]

            # decrypt Caesar key
            key_int = rsa_decrypt(enc_key, n, d)
            caesar_key = key_int % 26

            print("[Receiver] Decrypted Caesar Key:", caesar_key)

            plaintext = caesar_decrypt_msg(cipher, caesar_key)
            print("\n[Receiver] Final Message:")
            print(plaintext)

def main():
    print("=== RECEIVER ===")
    name = input("Enter identity: ")

    n, e, d = generate_rsa_keys()
    print("[Public Key]:", n, e)
    print("[Private Key]:", n, d)

    while True:
        print("\n1. Register")
        print("2. Receive message")
        print("3. Exit")
        ch = input("Choice: ")

        if ch == "1":
            register(name, n, e)
        elif ch == "2":
            wait_message(n, d)
        elif ch == "3":
            break

if __name__ == "__main__":
    main()
