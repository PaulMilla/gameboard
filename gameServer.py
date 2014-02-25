#!/usr/bin/python
import re
import socket
import threading
import gamebases
import connect4
import msgproxy
from Queue import Queue
#from connect4 import *

games = ["connect4"]

class player():
    def __init__(self, id, socket, name):
	self.id = id
	self.socket = socket
	self.name = name

port = 1025 
host = socket.gethostname()
msg  = msgproxy.MsgProxy() 

#Set up server
mainsock = socket.socket()
mainsock.bind((host,port))
mainsock.listen(100) #allow up to 100 pending connections on this socket

#Stored with key = gameID and value =
#(gameID, player1, player2, gameName)
waitingGames = {}
gameLists = {}
gameID = 0

#Wait for incomming connection(s)..
try:
    while True:
	print "waiting for connection..."
	
	#waiting for a client to connect (BLOCKING)
	client, addr = mainsock.accept()
	# client.setdefaulttimeout(5)
	print "created server socket on", client.getsockname()
	print "got connection from", addr
	print "waiting for message..."
	
	#waiting for a client to send a meesage(BLOCKING)
	command = msg.recv(client)
	print "received:", command, "from connection:", addr
	
	#if client asks for a lists of games
	if isinstance(command, tuple) and command[0] == 'GAMES':
	    print "sending: "+str(games)
	    msg.send(client, games)
	    client.close()
	
	#if client asks for a list of opponents
	elif isinstance(command, tuple) and command[0] == 'OPPONENTS':
	    msgbody = waitingGames.values()
	    print "sending: "+str(msgbody)
	    msg.send(client, msgbody)
	    client.close()
	
	#if client reqests to start/join a game
	elif isinstance(command, tuple) and command[0] == 'REQUEST':
	    #Requests a match with an existing game
	    #('REQUEST', int(game_id), int(player_id:1 or 2), str(player_name))
	    if isinstance(command[1], int):
			waitingGames.pop(command[1])
			playerB = player(command[2], client, command[3])
			print "sending: (True,)"
			msg.send(client,(True,))
			gameLists.pop(command[1]).send(playerB)
	    
	    #Requests a new game to be made
	    #('REQUEST', str(game_Name), int(player_id:1 or 2), str(player_name))
	    else:
			key = gameID
			gameID += 1
			playerA = player(command[2], client, command[3])
			newGame = connect4.Connect4()
			gameLists[key] = newGame
			if playerA.id == 1:
			    value = (key, playerA.name, None, command[1])
			if playerA.id == 2:
			    value = (key, None, playerA.name, command[1])
			waitingGames[key] = value
			
			print "sending: (True,)"
			msg.send(client,(True,))
			# gameLists[key].settimeout(None)
			gameLists[key].start()
			gameLists[key].send(playerA)
	else:
	    msgbody = """After connect returns, you have 5 seconds to send one of these message tuples:
('REQUEST', str(game_name), int(player_id:1 or 2), str(player_name))
('REQUEST', int(game_id), int(player_id:1 or 2), str(player_name))
('GAMES',)
('OPPONENTS',)
via and instance of MsgProxy"""
	    msg.send(client,msgbody)

except KeyboardInterrupt:
    print 'User terminated server'
    client.close()

except BaseException as e:
    print 'An unexpected error has occurred'
    exceptionName = e.__class__.__name__
    exceptionData = "exceptionData"
    print exceptionName
    msgbody = ('ERROR', exceptionName, (exceptionData,))
    print "sending: "+str(msgbody)
    msg.send(mainsock, msgbody)

finally:
    print "shutting server down"
    mainsock.close()
