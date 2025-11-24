# tpe_server.py
import socket
import threading

HOST = "127.0.0.1"
PORT = 4000

# Stores: name -> (n, e)
public_keys = {}

def handle_client(conn, addr):
    with conn:
        data = conn.recv(4096).decode().strip()
        if not data:
            return
        parts = data.split()
        cmd = parts[0].upper()

        if cmd == "REGISTER" and len(parts) == 4:
            # REGISTER <name> <n> <e>
            name = parts[1]
            n = int(parts[2])
            e = int(parts[3])
            public_keys[name] = (n, e)
            print(f"[TPE] Registered {name} -> (n={n}, e={e})")
            conn.sendall(b"OK\n")

        elif cmd == "GETKEY" and len(parts) == 2:
            # GETKEY <name>
            name = parts[1]
            if name in public_keys:
                n, e = public_keys[name]
                resp = f"KEY {name} {n} {e}\n".encode()
                conn.sendall(resp)
            else:
                conn.sendall(b"NOTFOUND\n")

        else:
            conn.sendall(b"ERROR\n")

def main():
    print(f"[TPE] Server listening on {HOST}:{PORT}")
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        while True:
            conn, addr = s.accept()
            threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()

if __name__ == "__main__":
    main()
