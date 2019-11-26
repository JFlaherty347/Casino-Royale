#implements a game of liar's dice
#---RULES OF LIAR'S DICE---
#>each player starts with a "hand" of 5 dice which they roll at the start of each round(players only know what their hand is)
#>the first player begins by placing a "bid" on the quantity(number of seperate dice) of a certain dice face(1-6) that exists between all the players' hands
#>a bid in essence means "I think that there are more than x number of ys between us" where x is quantity and y is face
#>in addition, 1s are counted as a wildcard, meaning that for any given bid, the actual quantity is (number of 1s + number of face) assuming a non-1 value
#	-increment the bid by increasing the quantity and/or the face of the bid
#	-"challenge" the previous bidder calling them a liar
#>the round continues until a challenge is called
#>when a challenge is called, all dice a revealed, and if there are strictly less than(or equal to) the quanity of the face bid by the last bidder, the bidder loses a die (equal is not more!)
#>alternatively, if there are more than the bid suggests, the challenger loses a die
#>thus marks the end of the round and gameplay continues until there is only one player remaining who is the overall winner
#>In each new round the first bidder is the loser of the previous round(The first bidder of the first round is arbitrary)
#---GENERAL PLAY---
#>The key to winning is making statistically sound bids, and bluffing safely
#>Having more dice is better than having less dice since you have access to more information about your dice as they now make up a greater proportion of the total pool of dice
import numpy as np
#import tensorflow as tf
import argparse
import bid
import player


def play():
	#setup
	gameCount = 0
	roundCount = 0

	#begin playing
	moreGames = True
	while(moreGames):
		#reset game(until one player remains)
		dicePool = NUM_PLAYERS * 5
		activePlayers = [1] * len(players) #1 = active, 0 = out of dice

		#output to keep track of game
		gameCount += 1
		print("************\n[GAME %d]\n************\n" %(gameCount))

		#setup loop variables to start playing rounds
		currentPlayer = 0
		moreRounds = True
		while(moreRounds):
			#reset round(until one player loses a die)
			rollAll()
			currentBid = setInitialBid(currentPlayer)

			#output to keep track of rounds and hands
			roundCount += 1
			print("--->Round %d\n" %(roundCount))
			printAllplayers()
			print("(initial) " + currentBid.toString())

			increaseBid = True
			while(increaseBid):
				#increment players and bid(continues until a player challenges)
				previousPlayer = currentPlayer
				currentPlayer = safelySelectNextBidder((currentPlayer + 1) % NUM_PLAYERS, activePlayers) #change player turns to next available player
				previousBid = currentBid
				currentBid = upBid(currentPlayer, previousBid, dicePool)
				
				#print bids
				print(currentBid.toString())

				#challenge on bid
				if(currentBid.face == 0):
					#previous bid holds actual bid that was challenged as current is now 0ed to signify a challenge
					#additionally, the current player is the challenger and the previous player is now the last bidder being challenged
					increaseBid = False
					faceCount = sumDice()
					dicePool -= 1 #decrement total of dice

					if(faceCount[previousBid.face] < previousBid.quantity):	#liar-last bidder loses a die
						players[previousPlayer].numDice -= 1	

						#update active players
						if(players[previousPlayer].numDice <= 0):
							activePlayers[previousPlayer] = 0					
						currentPlayer = safelySelectNextBidder(previousPlayer, activePlayers) #loser starts bid for next round
						print("***CHALLENGE*** %s loses a die!\n", players[previousPlayer].name)

						players[currentPlayer].numRoundsWon += 1	#count round win for winner
					else: #truther-challenger loses a die
						players[currentPlayer].numDice -= 1

						#update active players
						if(players[currentPlayer].numDice <= 0):
							activePlayers[currentPlayer] = 0
						currentPlayer = safelySelectNextBidder(currentPlayer, activePlayers) #loser starts bid for next round
						print("***CHALLENGE*** %s loses a die!\n" %players[currentPlayer].name)

						players[previousPlayer].numrRundsWon += 1	#count round win for winner

			moreRounds = not (checkForWinner(activePlayers)) #if no one has won, keep playing more rounds

		#award winner
		winner = getWinner()
		if(winner == -1):
			print("No winners somehow...\n")
		else:
			print("%s WINS!\n" %(players[winner].name))
			players[winner].numGamesWon += 1
		#prompt user if they wish to continue]
		userInput = input("Play Again? (Y/N)") 
		moreGames = (userInput == "Y" or userInput == "y")

#update with AI
def setInitialBid(currentPlayer):
	newFace = 2
	newQuantity = 1
	return bid.bid(newFace, newQuantity)

#update with AI; face = 0 is a call		
def upBid(currentPlayer, previousBid, dicePool):
	newFace = previousBid.face
	newQuantity = previousBid.quantity + 1

	if(newQuantity > dicePool):
		newFace, newQuantity = 0, 0

	return bid.bid(newFace, newQuantity)

#have all players roll a new hand
def rollAll():
	for i in range(NUM_PLAYERS):
		players[i].rollDice()

#counts the number of each face of dice and returns it in an array of length 6 (1 for each face)
def sumDice():
	count = np.zeros(6)	#holds quantity of each face
		
	#count all players' hands
	for i in range(NUM_PLAYERS):
		currentDice = players[i].getHand() 	#holds a hand of dice to count
		#count whole hand of dice
		for j in range(players[i].numDice):
			count[int(currentDice[j]-1)] += 1	#-1 to account for indexing at 0 (ie index 0 = quantity of 1s)

	return count

#ensures that a "dead" player isn't selected to bid
def safelySelectNextBidder(nextPlayer, activePlayers):
	nextBidder = -1
	currentCheck = nextPlayer #current player to check

	#ensure active players are not all zeros just in case
	if(np.any(activePlayers)):

		#loop until an active player is found
		while(nextBidder == -1):
			if(activePlayers[currentCheck] != 0):
				nextBidder = currentCheck

			currentCheck = (currentCheck + 1) % NUM_PLAYERS
	else:
		print("\n\n$#$#$#$#$#$#$ how did this happen lol $#$#$#$#$#$#$\n\n")

	return nextBidder

#checks active players to see if only one is left
def checkForWinner(activePlayers):
	isWinner = True 	#assume true, change to false once there are counterexamples
	activeTally = 0 	#count the number of players that have at least 1 die

	for i in range(NUM_PLAYERS):
		if (activePlayers[i] != 0): #increment tally for every player that isn't inactive
			activeTally += 1

		if(activeTally >= 2): #stop as soon as at least 2 players are found
			isWinner = False
			break

	print("DEBUG: ACTIVE TALLY %d" %activeTally)
	return isWinner

#gets index of the winner of the game, returns -1 if no winner exists somehow
def getWinner():
	winnerIndex = -1
	for i in range(NUM_PLAYERS):
		if(players[i] != 0):
			winnerIndex = i
			break

	return winnerIndex


#output data about all players
def printAllplayers():
	for i in range(NUM_PLAYERS):
		print(players[i].toString())


#main
NUM_PLAYERS = 3
players = []
for i in range(NUM_PLAYERS):
	players.append(player.player("Player %d" %i))

play()