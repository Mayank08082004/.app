# sender.py
import socket
from crypto_utils import generate_rsa_keys, rsa_encrypt, caesar_encrypt_msg

THIRD_HOST = "127.0.0.1"
THIRD_PORT = 4444

RECV_HOST = "127.0.0.1"
RECV_PORT = 3333

def register(name, n, e):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((THIRD_HOST, THIRD_PORT))
        s.sendall(f"REGISTER {name} {n} {e}\n".encode())
        print("[TPA]:", s.recv(1024).decode().strip())

def get_key(name):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((THIRD_HOST, THIRD_PORT))
        s.sendall(f"GETKEY {name}\n".encode())
        resp = s.recv(1024).decode().strip()

        if resp == "NOTFOUND":
            print("Receiver not registered.")
            return None, None

        n, e = resp.split()
        return int(n), int(e)

def send_message(receiver_name):
    n_r, e_r = get_key(receiver_name)
    if not n_r:
        return

    plaintext = input("Enter message: ")
    key = int(input("Enter Caesar key (0-25): ")) % 26

    cipher = caesar_encrypt_msg(plaintext, key)

    # encrypt Caesar key
    enc_key = rsa_encrypt(key, n_r, e_r)

    payload = f"{enc_key}\n{cipher}\n"

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((RECV_HOST, RECV_PORT))
        s.sendall(payload.encode())
        print("Message sent.")

def main():
    print("=== SENDER ===")
    name = input("Enter identity: ")

    n, e, d = generate_rsa_keys()
    print("[Public Key]:", n, e)
    print("[Private Key]:", n, d)

    while True:
        print("\n1. Register")
        print("2. Send message")
        print("3. Exit")
        ch = input("Choice: ")

        if ch == "1":
            register(name, n, e)
        elif ch == "2":
            recv = input("Receiver name: ")
            send_message(recv)
        elif ch == "3":
            break

if __name__ == "__main__":
    main()
