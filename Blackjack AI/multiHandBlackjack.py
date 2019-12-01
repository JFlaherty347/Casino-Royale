import tensorflow as tf
import multiprocessing as mp
import numpy as np
from multiprocessing import Process, Lock
import blackjackEnvironment as benv

#uses same state format as blackjackEnv.py
class multiHandBlackJack():

	#GLOBALS
	starting_balance = 1000
	num_players = 4
	player_balances = [starting_balance] * num_players

	#prepares game to be played
	def __init__(self):
		#load trained agent from disk
		self.agent = tf.saved_model.load("/models/")
		self.agent().initialize()

		self.env = benv.BlackjackEnv()
		self.tf_env = tf_py_environment.TFPyEnvironment(self.env)
		#setup GUI

	#visualize the hand that just happened
	def updateGUI():
		#show hands
		#show win/loss
		#show updated balances
		print("implement me")

	#player plays a hand using DDQNN
	def player(playerID, player_scores):
		print('Hello I am player ' + str(playerID))
		#lock before accessing player_scores

	#Dealer who plays as all houses do (at least 17); used to simulate dealer playstyle to see if players win
	def getDealerScore():
		#get starter cards
		starterCard1 = self.benv.drawNewCard()
		starterCard2 = self.benv.drawNewCard()
		#define dealer's state
		dealer_state = [(starterCard1 + starterCard2), starterCard1, starterCard2, 0, 0, 0, 0, 0, 0] 

		#hit if under 17, otherwise stand
		currentCardIndex = 3
		while(dealer_state[0] < 17 and currentCardIndex < 9):
			newCard = self.benv.drawNewCard()
			#update sum with newest card and add it to cards
			dealer_state[0] += newCard
			dealer_state[currentCardIndex] = newCard
			currentCardIndex += 1

			#when over, change any 11s(aces) to 1s (skip state[0] because its a sum)
            if(dealer_state[0] > 21):
                for i in range(1,9):
                    if(dealer_state[i] == 11):
                        dealer_state[i] = 1 #fix card
                        dealer_state[0] -= 10 #fix sum

                    #break if successfully reduced
                    if(dealer_state <= 21):
                        break

        #return dealer's score
        return dealer_state[0]


	#Plays a set amount of hands and updates scores
	def onNextBet(betAmount):
		#define globals
		global num_players
		global player_balances

		#get dealer score to check player hands against
		dealerScore = getDealerScore()

		#create an array to store results of player hands
		player_scores = np.zeros((num_players, 9))
		
		#play each hand
		processes = []
		for i in range(num_players):
			process = Thread(target = player, args = (i, player_scores))
			processes.append(process)
			process.start()

		#wait for all hands to finish
		for process in processes:
			process.join()

		#payout bets to all players
		for i in range(num_players):
			if(player_scores[i] > dealerScore):
				player_balances[i] += betAmount
			elif(player_scores[i] < dealerScore):
				player_balances[i] -= betAmount
			#otherwise, hand is a push

		#show results of hand
		updateGUI()
