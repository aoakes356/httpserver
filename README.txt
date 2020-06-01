Project 1
by Andrew Oakes
A simple HTTP server that can accept multiple connections
HTTP/1.1 and 1.0 compliant (hopefully).


Made with Python 3.6.8

to start the server type:

    python3 MultiThreadedHttpServer.py
    (sorry for long name, assignment said to call it that??)

I have it using port 8000, but the constant that is used is at the very top of the file

NOTES

Chrome seems to ignore the "Connection: Keep-Alive" and "Keep-Alive: timeout=10, max=10000" Headers and do whatever the heck it wants, not sure if I was supposed to find a different solution, but I'm out of time to find out. Firefox, however, does what I want.
