import socket
import subprocess
import os

def run_server():
    HOST = '0.0.0.0'
    PORT = 9999

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen(1)
    print(f"[+] Waiting for connection on port {PORT}...")

    client_socket, addr = server.accept()
    print(f"[+] Connected with {addr[0]}:{addr[1]}")

    current_dir = os.getcwd()

    while True:
        try:
            command = client_socket.recv(1024).decode().strip()
            print(f"[Client] {command}")  # Log incoming command

            if command.lower() == 'exit':
                break

            if command.startswith("cd "):
                path = command[3:].strip()
                try:
                    os.chdir(path)
                    current_dir = os.getcwd()
                    client_socket.send(f"[+] Changed directory to {current_dir}".encode())
                except Exception as e:
                    client_socket.send(f"[Error] {str(e)}".encode())
            else:
                output = subprocess.getoutput(command)
                client_socket.send(output.encode() or b"[+] Command executed with no output.")
        except Exception as e:
            client_socket.send(f"[Error] {str(e)}".encode())

    client_socket.close()
    server.close()

def run_client():
    HOST = input("Enter host IP address: ").strip()
    PORT = 9999

    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((HOST, PORT))
    print(f"[+] Connected to {HOST}:{PORT}")

    while True:
        command = input("Shell> ").strip()
        if command.lower() == 'exit':
            client.send(b'exit')
            break

        client.send(command.encode())
        output = client.recv(4096).decode()
        print(output)

    client.close()

if __name__ == "__main__":
    mode = input("Run as [server/client]: ").strip().lower()
    if mode == 'server':
        run_server()
    elif mode == 'client':
        run_client()
    else:
        print("Invalid mode. Use 'server' or 'client'.")