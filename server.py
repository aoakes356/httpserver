import socket
import select
import queue
import time

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)   #IPv4, TCP 
s.bind(('localhost',8000))
s.listen(500)
reading = [s]
writing = []
outgoing = {}   # dictionary of queues, mapped to by their sockets.
waiting = {}    # dictionary of times mapped to by their sockets.
def buffered_read(sock):
    buff = ""
    delta = "ayy"
    while delta != "":
        delta = sock.recv(1024).decode("utf-8")
        buff += delta
        if(len(delta) < 1024):
            break
    return buff

while True:
    read, write, err = select.select(reading,writing,reading)# Monitor inputs.
    for opened in read:
        if not (opened is s):
            # A client is sending data
            # Later we will want to parse the buffered read, and generate a response.
            print("Waiting to read!")
            read = buffered_read(opened)
            if read:
                print("Read something!")
                print("Read from the client: ",read)
                outgoing[opened].put(read)# This echos, put generated response here.
                if not (opened in writing): 
                    # Add to the list of clients who we can respond to.
                    writing.append(opened)
            else:
                print("Didn't read anything!")
                # Nothing from that client
                opened.close()    
                if opened in writing:
                    writing.remove(opened)
                reading.remove(opened)
                del outgoing[opened]
        else:
            # New connection!
            print("Waiting on connection!")
            clientSocket, address = opened.accept()
            clientSocket.setblocking(0)
            outgoing[clientSocket] = queue.Queue()  # Give it a response queue.
            print(f"Connection from {address} has been established.")
            reading.append(clientSocket);   #Add the client socket for later reading.
    for writeable in write:
        try:
            writeable.send((outgoing[writeable].get_nowait()).encode("utf-8"))
        except queue.Empty:
            writing.remove(writeable)

