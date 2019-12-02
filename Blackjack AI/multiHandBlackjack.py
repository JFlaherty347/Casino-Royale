import tensorflow as tf
import threading
import numpy as np
import blackjackEnvironment as benv
import tkinter as tk

from threading import Thread, Lock
from tf_agents.environments import py_environment
from tf_agents.environments import tf_environment
from tf_agents.environments import tf_py_environment

#GLOBALS
starting_balance = 5000
num_players = 4
player_balances = [starting_balance] * num_players	#money of each player
player_states = np.zeros((num_players + 1, 9))			#current sums and cards of players AND dealer

#uses same state format as blackjackEnv.py
class multiHandBlackJack():

	#prepares game to be played
	def __init__(self):
		#load trained agent from disk
		self.policy = tf.saved_model.load("./models/policy")

		self.env = benv.BlackjackEnv()
		self.tf_env = tf_py_environment.TFPyEnvironment(self.env)
		#setup GUI

	#player plays a hand using DDQNN
	def player(self, playerID, lock):
		global player_states

		#print('\nHello I am player ' + str(playerID)) #test multiproc
		
		#reset
		time_step = self.tf_env.reset()
		policy_state = self.policy.get_initial_state(batch_size = self.tf_env.batch_size)
		#set defaults for checks
		action_step = [1]
		player_state = np.zeros(shape = (1,1,1))

		#while still hitting and busted
		while(action_step[0] is 1 and not player_state[0][0][0] > 21):
			#decide and take action
			action_step, policy_state, _info = self.policy.action(time_step, policy_state)
			time_step = self.tf_env.step(action_step)

			#convert player state tensor into a numpy array
			player_state = time_step.observation.numpy()

		#check for bust
		if(player_state[0][0][0] > 21):
			player_state[0][0][0] = -21

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

		#get dealer score to check player hands against and put it into the player_states array
		player_states[num_players] = self.getDealerState()
		
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
			if(player_states[i][0] > player_states[num_players][0]):
				player_balances[i] += betAmount
			elif(player_states[i][0] < player_states[num_players][0]):
				player_balances[i] -= betAmount
			#otherwise, hand is a push

'''
#test
print("Ok starting...")
game = multiHandBlackJack()
game.onNextBet(100)

print("\nResults...")
for i in range(num_players):
	print("\nBalance of Player " + str(i) + ": " + str(player_balances[i]))
'''

### GUI methods 

#button methods
def onBetPress(betAmount, game, balance_labels, net_return_label, sum_labels):
	#conduct next hand
	game.onNextBet(betAmount)

	#update balance labels
	for i in range(num_players):
		balance_labels[i].config(text = "P" + str(i+1) + " Balance: $" + str(player_balances[i]))

	updateNetReturn(net_return_label)
	updateHands(sum_labels)

def onResetPress(balance_labels, net_return_label):
	#set all balances to starting balance
	for i in range(num_players):
		player_balances[i] = starting_balance

	#update balance labels
	for i in range(num_players):
		balance_labels[i].config(text = "P" + str(i+1) + " Balance: $" + str(player_balances[i]))

	#update net return label
	net_return_label.config(text = "Net Return: $0")

#helper methods
def updateNetReturn(net_return_label):
	#calculate net return
	net_return = 0
	for i in range(num_players):
		net_return += (player_balances[i] - starting_balance)

	#update net return label
	net_return_label.config(text = "Net Return: $" + str(net_return))

def updateHands(sum_labels):
	#update sums (all players + dealer)
	for i in range(num_players + 1):
		#update sum differently if bust(stored as -21)
		if(player_states[i][0] == -21):
			sum_labels[i].config(text = "Sum: BUST")
		else:
			#[i][0] is the sum for the ith player; note that dealer is included in player state
			sum_labels[i].config(text = "Sum: " + str(player_states[i][0]))

###window creation

#create game class
game = multiHandBlackJack()

#create a window, title it, and set size
window = tk.Tk()
window.title("Blackjack")
window.geometry('1700x900')

#get icon file
icon = tk.PhotoImage(file = "./assets/blackjackicon.png")

#set icon of window
window.iconphoto(False, icon)

#widget creation

###column label widets

#add labels for balances
balances = []

p1_balance_label = tk.Label(window, text = "P1 Balance: $" + str(player_balances[0]), font = ("Garamond", 20))
p2_balance_label = tk.Label(window, text = "P2 Balance: $" + str(player_balances[1]), font = ("Garamond", 20))
p3_balance_label = tk.Label(window, text = "P3 Balance: $" + str(player_balances[2]), font = ("Garamond", 20))
p4_balance_label = tk.Label(window, text = "P4 Balance: $" + str(player_balances[3]), font = ("Garamond", 20))

#add labels to list
balances.append(p1_balance_label)
balances.append(p2_balance_label)
balances.append(p3_balance_label)
balances.append(p4_balance_label)

#place labels on grid
for i in range(num_players):
	balances[i].grid(column = i, row = 1, padx = 15, pady = 10)

#create label to mark dealer's column and place it on the grid
dealer_label = tk.Label(window, text = "Dealer", font = ("Garamond", 20))
dealer_label.grid(column = 4, row = 1, padx = 15, pady = 10)

###hand visualization

#add labels for sums
sums = []

p1_sum_label = tk.Label(window, text = "Sum: 0", font = ("Garamond", 20))
p2_sum_label = tk.Label(window, text = "Sum: 0", font = ("Garamond", 20))
p3_sum_label = tk.Label(window, text = "Sum: 0", font = ("Garamond", 20))
p4_sum_label = tk.Label(window, text = "Sum: 0", font = ("Garamond", 20))
dealer_sum_label = tk.Label(window, text = "Sum: 0", font = ("Garamond", 20) )

#add labels to list
sums.append(p1_sum_label)
sums.append(p2_sum_label)
sums.append(p3_sum_label)
sums.append(p4_sum_label)
sums.append(dealer_sum_label)

#place labels on grid, 1 extra for dealer
for i in range(num_players + 1):
	sums[i].grid(column = i, row = 2, padx = 15, pady = 10)



###top info bar widgets

#create bet amount label and place it on the grid
bet_label = tk.Label(window, text = "Bet Amount:", font = ("Garamond", 16))
bet_label.grid(column = 0, row = 0, pady = 25)
#create bet amount variable for use with spinbox
bet_amount = tk.IntVar()
bet_amount.set(100)
#create bet amount spinbox and place it on the grid
bet_spin = tk.Spinbox(window, from_ = 0, to = 10000, width = 10, textvariable = bet_amount, font = ("Garamond", 16))
bet_spin.grid(column = 1, row = 0, pady = 25)

#create net return label and place it on the grid
net_return_label = tk.Label(window, text = "Net Return: $0", font = ("Garamond", 20))
net_return_label.grid(column = 4, row  = 0, pady = 25)

#create button for betting and place it on the grid
bet_button = tk.Button(window, text = "Bet!", 
	command = lambda: onBetPress(betAmount = bet_amount.get(), game = game, balance_labels = balances, net_return_label = net_return_label, sum_labels = sums), 
	font = ("Garamond", 16), activebackground = "green", width = 20)
bet_button.grid(column = 2, row = 0, pady = 25, padx = 10)

#create button to reset player balances and place it on the grid
reset_balances_button = tk.Button(window, text = "Reset Balances",
	command = lambda: onResetPress(balance_labels = balances, net_return_label = net_return_label), font  = ("Garamond", 16),
	activebackground = "red", width = 20)
reset_balances_button.grid(column = 3, row = 0, pady = 25, padx = 10)

###start window
window.mainloop()