import socket

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)   #IPv4, TCP 
s.bind((socket.gethostname(),8000))
s.listen(500)

while True:
    clientSocket, address = s.accept()
    print(f"Connection from {address} has been established.")
    clientSocket.send("Die in a fire".encode("utf-8"))
