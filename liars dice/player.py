import random
import numpy as np

class player:		

	def __init__(self, name):
		self.name = name #current dice player has in play
		self.numDice = 5
		self.numGamesWon = 0
		self.numRoundsWon = 0
		self.hand = np.zeros(5) #players set of dice (max 5)

	#rolls all dice in hand
	def rollDice(self):
		for i in range(self.numDice):
			self.hand[i] = random.randint(1, 6)

	#return hand of dice(an array)
	def getHand(self):
		return self.hand

	#create string representation of a player (aka toString)
	def toString(self):
		output = "<> %s: %d dice; %d games won; %d rounds won; current hand: [" %(self.name, self.numDice, self.numGamesWon, self.numRoundsWon)
		#iterate through hand for number of dice the player has
		for i in range(self.numDice):
			output += str(self.hand[i]) + ", "

		return output + "]\n"