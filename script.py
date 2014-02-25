#!/usr/bin/python

import socket
import msgproxy

# make a new socket object
channel = socket.socket()
# make a new MsgProxy
msg = msgproxy.MsgProxy()
# request a connection from the gameserver passive socket
#HOST = 'stinking-cloud.cs.utexas.edu'
HOST = 'cuddlefish.cs.utexas.edu'
PORT = 1025
channel.connect((HOST, PORT))
# send a valid message to the server
msgbody = ('GAMES')
msg.send(channel, msgbody)
# try to read one message from the buffer, will block if empty
response = msg.recv(channel)
print response

# close the socket (cannot be re-opened)
channel.close()
