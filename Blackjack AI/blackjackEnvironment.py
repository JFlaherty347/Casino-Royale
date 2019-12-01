""" Created referencing google's tensorflow agents github page
    In order to allow for Reinforcement Learning there must be an environment that represents that task that the agent is intended to learn
    see the following pages for more info on RL:
        -Wikipedia's Pages on RL, Q-Learning, DRL
        -Google's tf-agents tutorials on their github
    Glossary of RL terms:
        Agent-The AI itself
        Environment- The task that the AI is solving(Everything that exists)
        Actions- How the agent interacts with the environment
        Policy- How the AI decides what action to take
        Reward- Feedback from the environment as a result of an action
        Observation- Information available to the AI(just what the AI percieves)

"""
import tensorflow as tf
import numpy as np

from tf_agents.environments import py_environment
from tf_agents.environments import tf_environment
from tf_agents.environments import tf_py_environment
from tf_agents.environments import utils
from tf_agents.environments import wrappers
from tf_agents.trajectories import time_step as ts
from tf_agents.specs import array_spec

tf.compat.v1.enable_v2_behavior()

#Enviornment class to probide representation of blackjack for agent to learn
class BlackjackEnv(py_environment.PyEnvironment):
    
    #initializs the Environment for blackjack
    def __init__(self):
        #Specify available actions: 0 = hold, 1 = hit; 
        self._action_spec = array_spec.BoundedArraySpec(shape = (1,), dtype = np.int32, minimum = 0, maximum = 1, name = 'action')
        #Specify Observation: (current score, [list of cards]x6) given in a single, length 9 array
        self._observation_spec = array_spec.BoundedArraySpec(shape = (1,9), dtype = np.int32, minimum = 0, name = 'observation') 
        self._state = [0, 0, 0, 0, 0, 0, 0, 0, 0]  #stores current gamestate same as observation
        self._episode_ended = False #Holds wether or not the game has ended

    #return action spec
    def action_spec(self):
        return self._action_spec

    #return observation spec
    def observation_spec(self):
        return self._observation_spec

   #Resets Environment to initial state. Returns state of environment
    def _reset(self):
    	#draw first 2 cards
        starterCard1 = self.drawNewCard()
        starterCard2 = self.drawNewCard()
        #set state with current sum and first 2 cards drawn
        self._state = [(starterCard1 + starterCard2), starterCard1, starterCard2, 0, 0, 0, 0, 0, 0] 
        self._episode_ended = False #reset end boolean

        #check for double aces to avoid instant bust
        if(self._state[0] > 21):
        	self._state[1] = 1		#change ace to 1
        	self._state[0] = 12		#update sum

        return ts.restart(np.array([self._state], dtype = np.int32)) #return a time_step

    #Takes action and returns reward
    def _step(self, action):
        #if done, reset
        if (self._episode_ended):
            return self.reset()

        #behavior for valid input
        if (action == 0 or self._state[8] != 0):
            self._episode_ended = True #stand or max of 4 hits
        elif (action == 1):
            newCard = self.drawNewCard()
            self._state[0] += newCard

            #start looking at 4th spot since first 3 are set by default
            for i in range(3,9):
                #once you find the first empty card slot, add new card then break
                if(self._state[i] == 0):
                    self._state[i] = newCard
                    break

            #when over, change any 11s(aces) to 1s (skip state[0] because its a sum)
            if(self._state[0] > 21):
                for i in range(1,9):
                    if(self._state[i] == 11):
                        self._state[i] = 1 #fix card
                        self._state[0] -= 10 #fix sum

                    #break if successfully reduced
                    if(self._state[0] <= 21):
                        break
        else:
            raise ValueError('Invalid action, non-binary action detected')


        #if game is over, grant rewards, otherwise just transition
        if (self._episode_ended or self._state[0] >= 21):
            #score - 21 is reward value, if bust, -21
            resultReward = self._state[0] - 21 if self._state[0] <= 21 else -21
            return ts.termination(np.array([self._state], dtype=np.int32), resultReward)
        else:
            return ts.transition(np.array([self._state], dtype=np.int32), reward = 0.0, discount = 1.0)


    #helper method to get a new card
    def drawNewCard(self):
    	#there are 4 tens with: actual 10, Jack, Queen, and King
    	cards = [2, 3, 4, 5, 6, 7, 8, 9, 10, 10, 10, 10, 11]
    	newCardIndex = np.random.randint(0,13)

    	return cards[newCardIndex]


'''
#Environment validation
env = BlackjackEnv() #Initialize python enviornment
#utils.validate_py_environment(environment, episodes = 5)i #validate env works

#wrap python enviornment in discrete enviornment then in tensorflow enviornment

#for action usage
stand = 0
hit = 1

time_step = env.reset()
print(time_step)
cumulative_reward = time_step.reward

#hit once, then stand
time_step = env.step(hit)
print(time_step)
cumulative_reward += time_step.reward

time_step = env.step(stand)
print(time_step)
cumulative_reward += time_step.reward

print('Final Reward = ', cumulative_reward)
'''