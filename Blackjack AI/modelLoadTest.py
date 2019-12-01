import tensorflow as tf
import blackjackEnvironment as benv

from tf_agents.environments import py_environment
from tf_agents.environments import tf_environment
from tf_agents.environments import tf_py_environment

class modelLoadTest():

	def __init__(self):
		self.policy = tf.saved_model.load("./models/policy")

		self.env = benv.BlackjackEnv()
		self.tf_env = tf_py_environment.TFPyEnvironment(self.env)
		#self.policy = self.agent.policy()

#test
model = modelLoadTest()

#run game
num_hands = 10
for i in range(num_hands):
	#reset
	time_step = model.tf_env.reset()
	policy_state = model.policy.get_initial_state(batch_size = model.tf_env.batch_size)
	action_step = [1]

	#show new deal
	print("\n$$$$$$$$$$$$$\n HAND " + str(i) + ":" + str(time_step))

	while(action_step[0] is 1):
		#decide and take action
		action_step, policy_state, _info = model.policy.action(time_step, policy_state)
		time_step = model.tf_env.step(action_step)

		print("\n&&&&&&&&&&&&&&&&\n" + str(time_step))
		#print("\n****************\n" + str(action_step))

	print("\nhand is done")