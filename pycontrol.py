import socket
import subprocess
import os
import time

blacklist = [
    'rm -rf', 'reboot', 'shutdown', 'poweroff', ':(){', 'mkfs', 'dd if=', '>:',
    'killall', 'kill -9', 'init 0', 'init 6', 'halt', 'chown /', 'chmod 777 /',
    '>', '<', 'wget http', 'curl http', 'scp ', 'nc -e', 'telnet'
]

def run_server():
    HOST = '0.0.0.0'
    PORT = 9999

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen(1)
    print(f"[+] Waiting for connection on port {PORT}...")

    client_socket, addr = server.accept()
    ip = addr[0]
    print(f"[+] Incoming connection from {ip}")

    allow = input(f"Allow connection from {ip}? (Y/n): ").strip().lower()
    if allow != 'y' and allow != '':
        client_socket.send(b"[ACCESS DENIED]")
        client_socket.close()
        print("[!] Connection denied.")
        server.close()
        return
    else:
        client_socket.send(b"[ACCESS GRANTED]")
        time.sleep(0.5)
        print(f"[+] Connection accepted from {ip}")

    current_dir = os.getcwd()

    while True:
        try:
            command = client_socket.recv(1024).decode().strip()
            print(f"[Client] {command}")

            if command.lower() == 'exit':
                break

            if any(bad in command for bad in blacklist):
                client_socket.send(b"[!] Command blocked for security reasons.")
                continue

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
    HOST = input("Enter server IP: ").strip()
    PORT = 9999

    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client.connect((HOST, PORT))
        response = client.recv(1024).decode()
        if "[ACCESS DENIED]" in response:
            print("[!] Access denied by server.")
            client.close()
            return
        elif "[ACCESS GRANTED]" in response:
            print(f"[+] Connected to {HOST}:{PORT}")
        else:
            print("[!] Unknown server response.")
            client.close()
            return
    except Exception as e:
        print(f"[!] Failed to connect: {str(e)}")
        return

    while True:
        command = input("Shell> ").strip()
        if not command:
            continue
        client.send(command.encode())
        if command.lower() == "exit":
            break
        response = client.recv(8192).decode()
        print(response)

    client.close()

if __name__ == "__main__":
    try:
        mode = input("Run as [server/client]: ").strip().lower()
        if mode == 'server':
            run_server()
        elif mode == 'client':
            run_client()
        else:
            print("Invalid mode. Use 'server' or 'client'.")
            input("Press ENTER to exit.")
    except Exception as e:
        print(f"[!] Unexpected error: {e}")
        input("Press ENTER to exit.")