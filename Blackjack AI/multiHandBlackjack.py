import tensorflow as tf
import threading
import numpy as np
import blackjackEnvironment as benv

from threading import Thread, Lock
from tf_agents.environments import py_environment
from tf_agents.environments import tf_environment
from tf_agents.environments import tf_py_environment

#GLOBALS
starting_balance = 1000
num_players = 4
player_balances = [starting_balance] * num_players	#money of each player
player_states = np.zeros((num_players, 9))			#current sums and cards of players

#uses same state format as blackjackEnv.py
class multiHandBlackJack():

	#prepares game to be played
	def __init__(self):
		#load trained agent from disk
		self.policy = tf.saved_model.load("./models/policy")

		self.env = benv.BlackjackEnv()
		self.tf_env = tf_py_environment.TFPyEnvironment(self.env)
		#setup GUI

	#visualize the hand that just happened
	def updateGUI(self):
		#show hands
		#show win/loss
		#show updated balances
		print("\n*GUI goes here*")

	#player plays a hand using DDQNN
	def player(self, playerID, lock):
		global player_states

		#print('\nHello I am player ' + str(playerID)) #test multiproc
		
		#reset
		time_step = self.tf_env.reset()
		policy_state = self.policy.get_initial_state(batch_size = self.tf_env.batch_size)
		action_step = [1]

		#while still playing hand
		while(action_step[0] is 1):
			#decide and take action
			action_step, policy_state, _info = self.policy.action(time_step, policy_state)
			time_step = self.tf_env.step(action_step)

		#convert player state tensor into a numpy array
		player_state = time_step.observation.numpy()

		#lock before accessing player_scores
		lock.acquire()
		try:
			#update player_scores with the current player
			player_states[playerID] = player_state[0][0]
		finally:
			lock.release()
		

	#Dealer who plays as all houses do (at least 17); used to simulate dealer playstyle to see if players win
	def getDealerState(self):
		#get starter cards
		starterCard1 = self.env.drawNewCard()
		starterCard2 = self.env.drawNewCard()
		#define dealer's state
		dealer_state = [(starterCard1 + starterCard2), starterCard1, starterCard2, 0, 0, 0, 0, 0, 0] 

		#hit if under 17, otherwise stand
		currentCardIndex = 3
		while(dealer_state[0] < 17 and currentCardIndex < 9):
			newCard = self.env.drawNewCard()
			#update sum with newest card and add it to cards
			dealer_state[0] += newCard
			dealer_state[currentCardIndex] = newCard
			currentCardIndex += 1

			#if over, change any 11s(aces) to 1s (skip state[0] because its a sum)
			if(dealer_state[0] > 21):
			    for i in range(1,9):
			        if(dealer_state[i] == 11):
			            dealer_state[i] = 1 #fix card
			            dealer_state[0] -= 10 #fix sum

			        #break if successfully reduced
			        if(dealer_state[0] <= 21):
			            break

		#if bust, set score to -21
		if(dealer_state[0] > 21):
			dealer_state[0] = -21

		#return dealer's state
		return dealer_state


	#Plays a set amount of hands and updates scores
	def onNextBet(self, betAmount):
		#define globals
		global player_balances
		global player_states

		#get dealer score to check player hands against
		dealer_state = self.getDealerState()
		
		#create lock to prevent race conditions
		lock = Lock()

		#play each hand
		threads = []
		for i in range(num_players):
			thread = Thread(target = self.player, args = (i, lock))
			threads.append(thread)
			thread.start()

		for thread in threads:
			thread.join()

		#payout bets to all players
		for i in range(num_players):
			#check the sum (0th element) in each player state vs dealer's sum
			if(player_states[i][0] > dealer_state[0]):
				player_balances[i] += betAmount
			elif(player_states[i][0] < dealer_state[0]):
				player_balances[i] -= betAmount
			#otherwise, hand is a push

		#show results of hand
		self.updateGUI()


print("Ok starting...")
game = multiHandBlackJack()
game.onNextBet(100)

print("\nResults...")
for i in range(num_players):
	print("\nBalance of Player " + str(i) + ": " + str(player_balances[i]))