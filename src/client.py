import requests
import time
import socket
import threading

def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    ip = str(s.getsockname()[0])
    s.close()
    return ip


SERVER_HOST = get_local_ip()

class Peer:
    def __init__(self, port, ip, id):
        self.port = port
        self.ip = ip
    
def register():
    # Prompt user for port
    
    SERVER_PORT = input("Enter port: ")
    if int(SERVER_PORT) < 1234:
        print("This port is reserved - please enter a new port greater than 1234, a port between 49152–65535 is advised")
        register()
    # Send POST request to /reg until 200 OK response is received
    reg_url = f"http://localhost:5000/reg"
    payload = {'port': SERVER_PORT}
    connect_id = ""
    while True:
        try:
            response = requests.post(reg_url, json=payload)
            if response.status_code == 200:
                # Extract the 'id' from the response JSON
                connect_id = response.json().get('id')
                print(f"Received connection ID: {connect_id}")
                break  # Exit the loop when successful response is received
            else:
                print("Failed to register, retrying in 3 seconds...")
        except requests.RequestException as e:
            print(f"Error during registration: {e}. Retrying in 3 seconds...")

        time.sleep(3)
    setup_socket(int(SERVER_PORT))


def handle_client(client_socket, client_address):
    print(f"[INFO] New connection from {client_address}")
    
    try:
        while True:
            # Receive the message from the client
            message = client_socket.recv(1024)
            if not message:
                continue  
            
            print(f"[{client_address}] Message: {message.decode('utf-8')}")
            
            # Send a response back to the client
            response = "Message received!"
            client_socket.send(response.encode('utf-8'))
    
    except Exception as e:
        print(f"[ERROR] Error while handling client: {e}")
        client_socket.close()

def setup_socket(SERVER_PORT):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((SERVER_HOST, SERVER_PORT))
    server_socket.listen(5) 
    print(f"[INFO] Server listening on {SERVER_HOST}:{SERVER_PORT}") 
    while True:
        client_socket, client_address = server_socket.accept()
        client_thread = threading.Thread(target=handle_client, args=(client_socket, client_address))
        client_thread.start()


    

def status(connect_id):
     # Start the loop to check the status of the connection
    status_url = f"http://localhost:5000/status/{connect_id}"
    while True:
        try:
            response = requests.get(status_url)
            if response.status_code == 200:
                return(response.json())
            elif response.status_code == 204:
                print("Connection not ready, retrying in 3 seconds...")
            else:
                print(f"Unexpected status code {response.status_code}, retrying in 3 seconds...")
        except requests.RequestException as e:
            print(f"Error while checking connection status: {e}. Retrying in 3 seconds...")

        time.sleep(3)
    
def send_message(client_socket, message):
    client_socket.send(message)
    # print(f"[CLIENT] Sent message: {message}")


def convert_file_to_byte_code(message):
    with open(message, 'rb') as file:
        byte_code = file.read()  # Read the entire PDF as bytes
    return byte_code

def connect_to_client(connection_id):
    peer = status(connection_id)
    try:
        # Create a socket object and connect to the server
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((peer['ip'], int(peer['port'])))
        while True:
            print(">")
            message = input()
            if message == 'end':
                client_socket.close()
                break
            # with open(f'{message}', 'rb') as file:
                # byte_code = file.read()   
            # convert_file_to_byte_code(message) 
            send_message(client_socket, convert_file_to_byte_code(message) )
            response = client_socket.recv(1024).decode('utf-8')
            print(f"[CLIENT] Received response: {response}")
        
    except Exception as e:
        print(f"[ERROR] Error connecting to server: {e}")
        

def main_menu():
    menu = "Select 1 or 2\n> 1: Register\n> 2: Connect"
    print(menu)
    regOrConnect = input()
    if regOrConnect == '1':
        register()
    elif regOrConnect == '2':
        print("Enter connection id")
        connect_to_client(input())
    else: 
        print(f"You did not enter 1 or 2")
        main_menu()

main_menu()

