import tensorflow as tf
import numpy as np
import blackjackEnvironment as benv

from tf_agents.specs import array_spec
from tf_agents.specs import tensor_spec
from tf_agents.networks import network

from tf_agents import specs
from tf_agents.agents.dqn import dqn_agent
from tf_agents.drivers import dynamic_step_driver
from tf_agents.networks import q_network
from tf_agents.replay_buffers import py_uniform_replay_buffer
from tf_agents.replay_buffers import tf_uniform_replay_buffer
from tf_agents.trajectories import time_step
from tf_agents.environments import tf_py_environment

from tf_agents.policies import q_policy

class QNetwork(network.Network):

    #initialize environment and wrap it in tf environment
    env = benv.BlackjackEnv()
    tf_env = tf_py_environment.TFPyEnvironment(env)

    #initialize network
    network = q_network.QNetwork(tf_env.time_step_spec().observation, tf_env.action_spec(), fc_layer_params = (100,))
    #initialize agent with a learning rate of 0.001
    agent = dqn_agent.DqnAgent(tf_env.time_step_spec(), tf_env.action_spec(), q_network = network, optimizer = tf.compat.v1.train.AdamOptimizer(0.001))

    #create replay buffer to keep track of training
    buffer_capacity = 500
    replay_buffer = tf_uniform_replay_buffer.TFUniformReplayBuffer(agent.collect_data_spec, batch_size = tf_env.batch_size, max_length = buffer_capacity)

    #add an observer to add to the buffer
    replay_observer = [replay_buffer.add_batch]

    collect_steps = 10
    #create step driver
    collect_op = dynamic_step_driver.DynamicStepDriver(tf_env, agent.collect_policy, observers  = replay_observer, num_steps = collect_steps).run()


    print(replay_buffer)

