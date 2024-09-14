import socket
import os
import subprocess

# Define the server's IP address and port
HOST = '127.0.0.1'  # Loopback address for localhost
PORT = 2728

# Define the root directory where your web files are located
DOCUMENT_ROOT = 'htdocs'

def phpObj(data):

    php_string = "$data = array(\n"

    for v in data:
        php_string += f"    '{v[0]}' => '{v[1]}',\n"

    php_string += ");"

    return php_string



def add_global_variables(php_file_path, phpObj, x):
    try:
        # Read the PHP file
        with open(php_file_path, 'r') as reader:
            content = []
            found_php_tag = False

            for line in reader:
                content.append(line)

                # Check for the "<?php" statement
                if line.strip() == "<?php":
                    # Add the desired key-value pairs after "<?php" with line breaks
                    if len(x) > 1:
                        content.append(phpObj+ "\n $_GET = $data;")
                    else:
                        content.append(phpObj+ "\n $_POST = $data;")    
                    found_php_tag = True

        # Write the modified content back to the file
        with open(php_file_path, 'w') as writer:
            writer.writelines(content)

        print("Modified PHP file:", php_file_path)

    except IOError as e:
        print(e)

# Function to handle incoming client requests
def handle_request(client_socket):
    # Receive data from the client
    request_data = client_socket.recv(4096).decode('utf-8')

    # Parse the HTTP request
    request_lines = request_data.split('\r\n')
    if len(request_lines) < 1:
        return

    # Extract the requested file path from the HTTP request
    request_line = request_lines[0]
    request_parts = request_line.split()
    post_data = request_data.split('\r\n\r\n', 1)[1]
    post_data = post_data.split('&')
    post_data = [x.split('=') for x in post_data]
    print(f"POST data: {post_data}")
    if len(request_parts) != 3:
        return

    method, path, protocol = request_parts
    print(f"Method: {method}, Path: {path}, File Path: {path}")
    

    # Create the full file path to the requested resource
    if path == '/':
        path = '/index.php'
    file_path = os.path.join(DOCUMENT_ROOT, path[1:])

    GorP = path.split('?')

    if method == 'GET' and len(GorP)>1:
        method = 'POST'
        path = GorP[0] 
        if path == '/':
            path = '/index.php'
        file_path = os.path.join(DOCUMENT_ROOT, path[1:])
            # print(f"Method: {method}, Path: {path}, File Path: {path}")
        post_data = GorP[1].split('&')
        post_data = [x.split('=') for x in post_data]

    # Check if the requested file exists
    if not os.path.exists(file_path):
        response = "HTTP/1.1 404 Not Found\r\n\r\n"
        client_socket.send(response.encode('utf-8'))
        return

    # Handle PHP files by executing them using subprocess
    if method == 'GET':
        
        if file_path.endswith('.php'):
            try:
                php_output = subprocess.check_output(['php', file_path], stderr=subprocess.STDOUT, timeout=5)
                response = f"HTTP/1.1 200 OK\r\nContent-Length: {len(php_output)}\r\n\r\n{php_output.decode('utf-8')}"
                client_socket.send(response.encode('utf-8'))
            except subprocess.CalledProcessError as e:
                response = f"HTTP/1.1 500 Internal Server Error\r\n\r\n{e.output.decode('utf-8')}"
                client_socket.send(response.encode('utf-8'))
            except subprocess.TimeoutExpired:
                response = "HTTP/1.1 500 Internal Server Error\r\n\r\nExecution Timeout"
                client_socket.send(response.encode('utf-8'))
        else:
            # Serve other static files
            with open(file_path, 'rb') as file:
                content = file.read()
                response = f"HTTP/1.1 200 OK\r\nContent-Length: {len(content)}\r\n\r\n"
                client_socket.send(response.encode('utf-8'))
                client_socket.send(content)


    elif method == 'POST':
    # Create a URL-encoded string from POST data
    
        add_global_variables(file_path,phpObj(post_data), GorP)
        
        if file_path.endswith('.php'):
            try:
                php_output = subprocess.check_output(['php', file_path], stderr=subprocess.STDOUT, timeout=5)
                print(f"PHP output: {php_output}")
                response = f"HTTP/1.1 200 OK\r\nContent-Length: {len(php_output)}\r\n\r\n{php_output.decode('utf-8')}"
                client_socket.send(response.encode('utf-8'))
            except subprocess.CalledProcessError as e:
                response = f"HTTP/1.1 500 Internal Server Error\r\n\r\n{e.output.decode('utf-8')}"
                client_socket.send(response.encode('utf-8'))
            except subprocess.TimeoutExpired:
                response = "HTTP/1.1 500 Internal Server Error\r\n\r\nExecution Timeout"
                client_socket.send(response.encode('utf-8'))
        else:
            # Serve other static files
            with open(file_path, 'rb') as file:
                content = file.read()
                response = f"HTTP/1.1 200 OK\r\nContent-Length: {len(content)}\r\n\r\n"
                client_socket.send(response.encode('utf-8'))
                client_socket.send(content)

# Create and configure the server socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST, PORT))
server_socket.listen(5)

print(f"Server listening on {HOST}:{PORT}")

# Main server loop
while True:
    client_socket, client_addr = server_socket.accept()
    print(f"Accepted connection from {client_addr}")
    
    # Handle the client request in a new thread or process to support multiple connections
    handle_request(client_socket)
    
    # Close the client socket
    client_socket.close()
