import socket
import threading
import os

HOST = '0.0.0.0'
PORT = int(os.environ.get('PORT', 5555))

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen()

clients = {}  # {username: client_socket}

def handle_client(client, username):
    while True:
        try:
            message = client.recv(1024).decode('utf-8')
            if message.startswith("/msg"):
                parts = message.split(" ", 2)
                if len(parts) < 3:
                    client.send("Invalid command. Use /msg <user> <message>".encode('utf-8'))
                    continue
                target_user, private_message = parts[1], parts[2]
                if target_user in clients:
                    target_socket = clients[target_user]
                    full_msg = f"[Private] {username} ➤ {target_user}: {private_message}"
                    target_socket.send(full_msg.encode('utf-8'))
                    client.send(f"[You ➤ {target_user}]: {private_message}".encode('utf-8'))
                else:
                    client.send(f"User '{target_user}' not found.".encode('utf-8'))
            elif message == "/users":
                users_list = "Online users:\n" + "\n".join(clients.keys())
                client.send(users_list.encode('utf-8'))
            else:
                client.send("Invalid command. Use /msg <user> <message> or /users".encode('utf-8'))
        except:
            print(f"{username} disconnected.")
            del clients[username]
            client.close()
            break

def receive_connections():
    print(f"Server is running on {HOST}:{PORT}...")
    while True:
        client, address = server.accept()
        print(f"Connected with {address}")

        client.send("USERNAME".encode('utf-8'))
        username = client.recv(1024).decode('utf-8')

        if username in clients:
            client.send("Username already taken. Disconnecting.".encode('utf-8'))
            client.close()
            continue

        clients[username] = client
        print(f"Username '{username}' connected.")

        client.send(f"Welcome, {username}! Use /msg <user> <message> to chat privately.\nUse /users to see online users.".encode('utf-8'))

        thread = threading.Thread(target=handle_client, args=(client, username))
        thread.start()

receive_connections()
