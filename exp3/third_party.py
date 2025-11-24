# third_party.py
import socket

HOST = "127.0.0.1"
PORT = 4444

def handle_request(cmd, key_store):
    parts = cmd.strip().split()
    if not parts:
        return "ERROR\n"

    if parts[0] == "REGISTER" and len(parts) == 4:
        # REGISTER name n e
        name = parts[1]
        n = parts[2]
        e = parts[3]
        key_store[name] = (n, e)
        print(f"[+] Registered {name} with n={n}, e={e}")
        return "OK\n"

    elif parts[0] == "GETKEY" and len(parts) == 2:
        name = parts[1]
        if name in key_store:
            n, e = key_store[name]
            return f"{n} {e}\n"
        else:
            return "NOTFOUND\n"

    return "ERROR\n"

def main():
    key_store = {}  # name -> (n, e)

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        print(f"[Third Party] Listening on {HOST}:{PORT}")

        while True:
            conn, addr = s.accept()
            with conn:
                data = conn.recv(1024).decode()
                if not data:
                    continue
                response = handle_request(data, key_store)
                conn.sendall(response.encode())

if __name__ == "__main__":
    main()
