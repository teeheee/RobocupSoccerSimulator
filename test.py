import socket
import sys

# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect the socket to the port where the server is listening
server_address = ('localhost', 9996)
print >>sys.stderr, 'connecting to %s port %s' % server_address
sock.connect(server_address)
while True:
    message = "1,0,1,0,-1\r\n"
    sock.sendall(message)
    sock.recv()
