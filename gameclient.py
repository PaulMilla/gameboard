#!/usr/bin/python

import socket
import msgproxy
import sys

playerID = 0
PORT = 1025
HOST = socket.gethostname() if len(sys.argv) < 2 else sys.argv[1]
msg = msgproxy.MsgProxy()

#Ask for input until valid
def validateChoice(string, isValid, errorMsg):
    while True:
	userInput = raw_input(string)
	if isValid(userInput):
	    return userInput
	print errorMsg

#Enter game mode
def gameMode(channel):
    disconnected = AssertionError('Lost communications with the Gameserver.')
    isError = lambda x: x is ''
    isValid = lambda x: 'INVALID MOVE' not in x 
    isOver = lambda x: 'GAME OVER' in x
    
    response = msg.recv(channel)
    print response
    while isError(response) is False:
	#Receive player1 move
	if playerID == 2:
	    print "Waiting for your opponent to move...."
	    response = msg.recv(channel)
	    if isOver(response): return response
	    elif isError(response): raise(disconnected)
	    print response
	
	#Send move
	while True: 
	    msgbody = raw_input("Enter your move: ")
	    msg.send(channel, msgbody)
	    response = msg.recv(channel)
	    if isOver(response): return response
	    elif isValid(response): print response; break
	    print response

	#Receive player2 move
	if playerID == 1:
	    print "Waiting for your opponent to move...."
	    response = msg.recv(channel)
	    if isOver(response): return response
	    elif isError(response): raise(disconnected)
	    print response
    return Exception

#############################Start Game Loop#####################################################


#Ask/validate userName
isValid = lambda x: bool(x)
errorMsg = "Name cannot be blank."
userName = validateChoice("Enter your name: ", isValid, errorMsg)

try:
    while True:
	userChoice = "r"
	while userChoice is "r":
	    #Start a new connection
	    channel = socket.socket()
	    channel.connect((HOST, PORT))

	    #Ask server for a list of opponents 
	    msgbody = ('OPPONENTS',)
	    msg.send(channel, msgbody)
	    response = msg.recv(channel)
	
	    #Print Menu
	    i = 0
	    for opponent in response:
	        print "("+str(i)+"): "+str(opponent[3])+", "+str(opponent[1])+" VS "+str(opponent[2])
	        i += 1
	    if len(response) is 0:
	        print "No games are awaiting players"
	    print "(r): refresh the list of games awaiting players"
	    print "(n): start a new game"
	    print "(q): quit"
	    channel.close()

	    #Ask/validate userChoice 
	    isValid = lambda x: x in ['r','n','q']+[str(x) for x in range(len(response))]
	    errorMsg = "You must enter one of the numbers or letters in paren." 
	    userChoice = validateChoice("Enter your choice: ", isValid, errorMsg)

        if userChoice is "n":
	    #Start a new connection
	    channel = socket.socket()
	    channel.connect((HOST,PORT))

	    #Ask server for a list of games
	    msgbody = ("GAMES",)
	    msg.send(channel, msgbody)
	    response = msg.recv(channel)
	    i = 0
	    for game in response:
	        print "("+str(i)+"): "+game
	        i += 1
	    channel.close()

	    #Ask/validate gameChoice
	    isValid = lambda x: x in [str(x) for x in range(len(response))]
	    errorMsg = "You must enter one of the numbers in paren."
	    gameChoice = validateChoice("Which game would you like to play? ", isValid, errorMsg)
	    gameName = response[int(gameChoice)]

	    #Ask/validate playerID
	    isValid = lambda x: x in ["1","2"]
	    errorMsg = "You must enter 1 or 2."
	    playerID = int(validateChoice("Choose player(1) or player(2): ", isValid, errorMsg))

	    #("REQUEST", str(game_name), int(player_id:1 or 2), str(player_name))
	    msgbody = ('REQUEST', gameName, playerID, userName)
	    print "Waiting for an opponent to join the game...." 
	elif userChoice is "q": break 
        else:
	    opponent = response[int(userChoice)]

	    if bool(opponent[2]):
	        playerID = 1
	    else:
	        playerID = 2
	
	    #("REQUEST", int(game_id), int(player_id:1 or 2), str(player_name))
	    msgbody = ('REQUEST', int(opponent[0]), playerID, str(userName))
   
        #Start a new connection
        channel = socket.socket()
        channel.connect((HOST,PORT))

        #Send a request to join/start a game
        msg.send(channel, msgbody)
        response = msg.recv(channel)

        #If accepted start game loop
        if response is not '':
            print gameMode(channel)
        else:
            print "Server response was false!"

except BaseException as e:
    print "\nAn Unexpected error has occurred:"
    print e.__class__.__name__ + " " + str(e.args)
finally:
    print "Exiting Game Client Program."
    print "Goodbye."
    channel.close()
