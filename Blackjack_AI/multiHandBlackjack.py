import tensorflow as tf
import threading
import numpy as np
import blackjackEnvironment as benv
import tkinter

from threading import Thread, Lock
from tf_agents.environments import py_environment
from tf_agents.environments import tf_environment
from tf_agents.environments import tf_py_environment
from tkinter import *
from PIL import ImageTk, Image

#GLOBALS
starting_balance = 5000
num_players = 4
player_balances = [starting_balance] * num_players	#money of each player
player_states = np.zeros((num_players + 1, 9))			#current sums and cards of players AND dealer
#win_tie_counts = np.zeros(4) #eval variable

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
		global playerw_states

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
				#win_tie_counts[i] += 1 #for eval
			elif(player_states[i][0] < player_states[num_players][0]):
				player_balances[i] -= betAmount
			#else:
				#win_tie_counts[i] += 1 #for eval
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
def onBetPress(betAmount, game, balance_labels, net_return_label, sum_labels, hand_labels):
	#conduct next hand
	game.onNextBet(betAmount)

	#eval success rates
	#for count in win_tie_counts:
	#	print("\n()()()()()()()()()()()COUNT: " + str(count))

	#update balance labels
	for i in range(num_players):
		balance_labels[i].config(text = "P" + str(i+1) + " Balance: $" + str(player_balances[i]))

	updateNetReturn(net_return_label)
	updateHands(sum_labels, hand_labels)

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

def updateHands(sum_labels, hand_labels):
	#update sums (all players + dealer)
	for i in range(num_players + 1):
		#update sum differently if bust(stored as -21)
		if(player_states[i][0] == -21):
			sum_labels[i].config(text = "Sum: BUST")
		else:
			#[i][0] is the sum for the ith player; note that dealer is included in player state
			sum_labels[i].config(text = "Sum: " + str(player_states[i][0]))

	#update cards for all players
	for i in range(num_players + 1):
		#for first 5 cards (skipping 0 because it is the sum and ending at 5 for sake of visibility)
		for j in range(1, 6):
			#get image path
			image_path = getCardImagePath(player_states[i][j], i)
			new_card_image = Image.open(image_path).resize((99, 151), Image.ANTIALIAS)
			new_card_image = ImageTk.PhotoImage(new_card_image)
			#update label with new card image
			hand_labels[i][j-1].config(image = new_card_image)
			hand_labels[i][j-1].image = new_card_image

def getCardImagePath(value, player):
	#cards are name as [value](face)
	card_path = "./assets/cards/"
	suit = getRandomSuit()

	if(value == 0):						#check if empty card
		back_colors = ["red", "blue", "yellow", "green", "gray"] #back colors per player
		card_path += back_colors[player] + "_back"
	elif(value == 1 or value == 11):	#check if ace(listed as 1 or 11)
		card_path += "A" + getRandomSuit()
	elif(value == 10):					#check if some value of 10
		ten_cards = ["J", "Q", "K", "10"] #all cards with value of 10
		card_path += ten_cards[np.random.randint(0,4)] + getRandomSuit()
	else:								#normal card
		card_path += str(int(value)) + getRandomSuit()

	return card_path + ".png"

def getRandomSuit():
	suits = ["C", "D", "H", "S"]	#clubs/diamonds/hearts/spades
	return suits[np.random.randint(0, 4)]

###window creation
def createBlackjackWindow(root):
	#create game class
	game = multiHandBlackJack()

	#create a window, title it, and set size
	window = Toplevel(root)
	#window.title("Blackjack")
	#window.geometry('1700x900')

	#get icon file
	#icon = PhotoImage(file = "./assets/blackjackicon.png")

	#set icon of window
	#window.iconphoto(False, icon)

	#widget creation

	###column label widets

	#add labels for balances
	balances = []

	#create labels for balance of each player and put them into the balances array
	for i in range(num_players):
		balances.append(Label(window, text = "P" + str(i+1) +" Balance: $" + str(player_balances[0]), font = ("Garamond", 20)))

	#place labels on grid
	for i in range(num_players):
		balances[i].grid(column = i, row = 1, padx = 15, pady = 10)

	#create label to mark dealer's column and place it on the grid
	dealer_label = Label(window, text = "Dealer", font = ("Garamond", 20))
	dealer_label.grid(column = 4, row = 1, padx = 15, pady = 10)

	###hand visualization

	#add labels for sums
	sums = []

	#create labels for each players' sum and put them into the sums array
	for i in range(num_players + 1):
		sums.append(Label(window, text = "Sum: 0", font = ("Garamond", 20)))

	#place labels on grid, 1 extra for dealer
	for i in range(num_players + 1):
		sums[i].grid(column = i, row = 2, padx = 15, pady = 10)

	###create labels for all card slots

	#load card back images and resize them (width, height)
	p1_cardBack = Image.open("./assets/cards/red_back.png").resize((99, 151), Image.ANTIALIAS)
	p2_cardBack = Image.open("./assets/cards/blue_back.png").resize((99, 151), Image.ANTIALIAS)
	p3_cardBack = Image.open("./assets/cards/yellow_back.png").resize((99, 151), Image.ANTIALIAS)
	p4_cardBack = Image.open("./assets/cards/green_back.png").resize((99, 151), Image.ANTIALIAS)
	d_cardBack = Image.open("./assets/cards/gray_back.png").resize((99, 151), Image.ANTIALIAS)

	#convert images to photoImage for use with labels
	p1_cardBack = ImageTk.PhotoImage(p1_cardBack)
	p2_cardBack = ImageTk.PhotoImage(p2_cardBack)
	p3_cardBack = ImageTk.PhotoImage(p3_cardBack)
	p4_cardBack = ImageTk.PhotoImage(p4_cardBack)
	d_cardBack = ImageTk.PhotoImage(d_cardBack)


	p1_cards = []
	#add a label for all five visible cards in hand and add them into p1's cards
	for i in range(5):
		p1_cards.append(Label(window, image = p1_cardBack))

	#place labels on grid
	for i in range(len(p1_cards)):
		#row 3+i will start at row 3 and go up for each additonal card
		p1_cards[i].grid(column = 0, row = (3+i), padx = 15, pady = 5)

	p2_cards = []
	#add a label for all five visible cards in hand and add them into p2's cards
	for i in range(5):
		p2_cards.append(Label(window, image = p2_cardBack))

	#place labels on grid
	for i in range(len(p2_cards)):
		#row 3+i will start at row 3 and go up for each additonal card
		p2_cards[i].grid(column = 1, row = (3+i), padx = 15, pady = 5)

	p3_cards = []
	#add a label for all five visible cards in hand and add them into p3's cards
	for i in range(5):
		p3_cards.append(Label(window, image = p3_cardBack))

	#place labels on grid
	for i in range(len(p3_cards)):
		#row 3+i will start at row 3 and go up for each additonal card
		p3_cards[i].grid(column = 2, row = (3+i), padx = 15, pady = 5)

	p4_cards = []
	#add a label for all five visible cards in hand and add them into p4's cards
	for i in range(5):
		p4_cards.append(Label(window, image = p4_cardBack))

	#place labels on grid
	for i in range(len(p4_cards)):
		#row 3+i will start at row 3 and go up for each additonal card
		p4_cards[i].grid(column = 3, row = (3+i), padx = 15, pady = 5)

	d_cards = []
	#add a label for all five visible cards in hand and add them into dealer's cards
	for i in range(5):
		d_cards.append(Label(window, image = d_cardBack))

	#place labels on grid
	for i in range(len(p3_cards)):
		#row 3+i will start at row 3 and go up for each additonal card
		d_cards[i].grid(column = 4, row = (3+i), padx = 15, pady = 5)

	hands = [p1_cards, p2_cards, p3_cards, p4_cards, d_cards] #holds all hands 

	###top info bar widgets

	#create bet amount label and place it on the grid
	bet_label = Label(window, text = "Bet Amount:", font = ("Garamond", 16))
	bet_label.grid(column = 0, row = 0, pady = 25)
	#create bet amount variable for use with spinbox
	bet_amount = IntVar()
	bet_amount.set(100)
	#create bet amount spinbox and place it on the grid
	bet_spin = Spinbox(window, from_ = 0, to = 10000, width = 10, textvariable = bet_amount, font = ("Garamond", 16))
	bet_spin.grid(column = 1, row = 0, pady = 25)

	#create net return label and place it on the grid
	net_return_label = Label(window, text = "Net Return: $0", font = ("Garamond", 20))
	net_return_label.grid(column = 4, row  = 0, pady = 25)

	#create button for betting and place it on the grid
	bet_button = Button(window, text = "Bet!", 
		command = lambda: onBetPress(bet_amount.get(), game, balances, net_return_label, sums, hands), 
		font = ("Garamond", 16), activebackground = "green", width = 20)
	bet_button.grid(column = 2, row = 0, pady = 25, padx = 10)

	#create button to reset player balances and place it on the grid
	reset_balances_button = Button(window, text = "Reset Balances",
		command = lambda: onResetPress(balance_labels = balances, net_return_label = net_return_label), font  = ("Garamond", 16),
		activebackground = "red", width = 20)
	reset_balances_button.grid(column = 3, row = 0, pady = 25, padx = 10)


root = Tk()
createBlackjackWindow(root)
###start window
root.mainloop()