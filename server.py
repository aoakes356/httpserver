import socket
import select
import queue
import time
import sys
import os.path
import re

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

def is_request_type(req_type):
    if(req_type == "HEAD" or req_type == "GET"):
        return True
    else:
        return False

def is_valid_file(fname):
    print(fname, os.path.isfile(fname))
    return os.path.isfile(fname)

def is_valid_proto(protocol):
    if((protocol == "HTTP/1.1") or (protocol == "HTTP/1.0")):
        return True
    else:
        return False

def convert_file_name(fname):
    if(fname == "/"):
        return "./template/index.html"
    elif(fname == "/index.html"):
        return "./template/index.html"
    else:
        return "./template"+fname

def parse_request_string(req_str):
    # Return an HTTP_Request object
    req = HTTP_Request()
    components = re.split('\n|\r',req_str)
    req_line = components[0]
    req.headers = components[1:]
    parsed = req_line.split(" ")
    if(len(parsed) == 3):
        if(is_request_type(parsed[0]) and is_valid_file(convert_file_name(parsed[1])) and is_valid_proto(parsed[2])):
            req.type = parsed[0]
            req.req = convert_file_name(parsed[1])
            proto = parsed[2].split("/")
            req.proto = proto[0]
            req.protov = proto[1]
            req.valid = True
        else:
            print(is_request_type(parsed[0]) , is_valid_file(convert_file_name(parsed[1])) , is_valid_proto(parsed[2]))
            req.valid = False
            return req


    else:
        req.valid = False
        return req

    #print(str(components))
    return req

def request_parse_test(): # Unit test for parser
    assert parse_request_string("GET /index.html HTTP/1.1").valid, "#1 failed, should be true"
    assert (not (parse_request_string("GET /indox.html HTTP/1.1").valid)), "#2 failed, should be false: file name"
    assert (not parse_request_string("GET /index.html HTTP/").valid), "#3 failed, should be false: proto"
    assert (not parse_request_string("GET /index.html /").valid), "#4 failed, should be false: proto"
    assert (not parse_request_string("GOT /index.html HTTP/1.1").valid), "#5 failed, should be false: type"
    assert (parse_request_string("HEAD /index.html HTTP/1.0").valid), "#6 failed, should be true"
    assert (not parse_request_string("POST /index.html HTTP/1.1").valid),"#7 failed, should be false: type"
    assert (not parse_request_string("PUT /index.html HTTP/1.1").valid),"#8 failed, should be false: type"
    assert (not parse_request_string("DELETE /index.html HTTP/1.1").valid),"#9 failed, should be false: type"
    assert (not parse_request_string("/index.html HTTP/1.1").valid),"#10 failed, should be false: type"
    assert (not parse_request_string("GET HTTP/1.1").valid),"#11 failed, should be false: proto"
    assert (not parse_request_string("").valid),"#12 failed, should be false: null"
    return True

class HTTP_Request():
    """A class to contain information about a parsed request """
    def __init__(self):
        self.type = "GET"
        self.req = "/"
        self.proto = "HTTP"
        self.protov = "1.1"
        self.headers = []
        self.valid = True
        self.data = ""
    def generate_response(self):
        #read the data
        #get its length
        #generate response headers
        status_line = ""
        try:
            f = open(self.req,'r')
            self.data = (f.read())
            f.close()
            if(self.valid):
                status_line = self.proto+"/"+self.protov+" "+"200 OK\r\n"
                status_line = status_line+"Content-Length: "+str(len(self.data))+"\r\n"
                status_line = status_line+"Content-Type: text/html; charset=utf8\r\n"
                status_line = status_line+"Connection: close\r\n"
                status_line = status_line+"Cache-Control: no-store\r\n\r\n"
                status_line = status_line+self.data
            else:
                status_line = self.proto+"/"+self.protov+" "+"404 Not Found\r\n"


        except Exception as e:
            print("Error! "+str(e))
            status_line = self.proto+"/"+self.protov+" "+"300 Server Error\r\n"
            
        self.data = status_line
        return self.data
        
#if(request_parse_test()):
#    print("Yayy, unit test passed")
#else:
#    print("Didn't work")

while True:
    # Takes care of multiple connections at once by making them show in the read array
    # once they are readable.
    read, write, err = select.select(reading,writing,reading)# Monitor inputs.
    for opened in read:
        if not (opened is s):
            # A client is sending data
            print("Waiting to read!")
            read = buffered_read(opened)
            if read:
                req = parse_request_string(read)
                if(req.valid):
                    print("Received valid request!")
                    outgoing[opened].put(req.generate_response())# This echos, put generated response here once implemented.
                print("Read from the client: ",read)
                if not (opened in writing): 
                    # Add to the list of clients who we can respond to.
                    writing.append(opened)
            else:
                print("Didn't read anything!, closing client")
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
            temp = outgoing[writeable].get_nowait()
            print("@!@!$!#@#% Sending: \n"+temp+"\n\n\n")
            writeable.send((temp).encode("utf-8"))
            #writeable.send('\r\n'.encode("utf-8"))
        except queue.Empty:
            writing.remove(writeable)

