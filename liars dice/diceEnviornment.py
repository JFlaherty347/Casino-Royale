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
i
class liarsDiceEnv(py_environment.PyEnvironment):
    
    #initializs the Environment for Liars Dice
    def __init__(self):
        #Specify available actions bid: (face, quantity) note that bounds are inclusive, 1 array of length 2 to allow both to be changed at once. Face = 7 means call liar
        self._action_spec = array_spec.BoundedArraySpec(shape = (1,2), dtype = np.int32, minimum = [0, 0], maximum = [7, 20], name = 'bid')
        #Specify Observation: (face, quantity, current dice pool size, hand size, players remaining) given in a single, length 3 array
        self._observation_spec = array_spec.BoundedArraySpec(shape = (1,5) dtype = np.int32, minimum = [0, 0, 0, 0], maximum = [7, 20, 15, 5, 3], name = 'observation') 
        self._state = [0, 0, 15, 5, 3] #stores current gamestate in same form as observation
        self._episode_ended = False #Holds wether or not the game has ended

    #return action spec
    def action_spec(self):
        return self._action_spec

    #return observation spec
    def observation_spec(self)
        return self._observation_spec

   #Resets Environment to initial state. Returns state of environment
   def _reset(self):
        self._state = [0, 0, 15, 5, 3] #restore default state
        self._episode_ended = False #reset end boolean
        return ts.restart(np.array([self._state], dtype = np.int32))

    #Takes action and returns reward
    def _step(self, action):
        #if done, reset
        if (self._episode_ended):
            return self.reset()

        #behavior for valid input
        if (self._state[4] <= 1):
            self._episode_ended = True

        #if game is over give reward, otherwise transition to new state as handled above
        if(self._episode_ended):
            winReward = self._state[3] * 10 if self._state[3] > 0 else -50
            return ts.termination(np.array([self._state], dtype  =np.int32), reward = winReward)
        else: 
            return ts.transition(np.array([self._state], dtype  =np.int32), reward = 0, discount = 1.0)
