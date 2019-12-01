import tensorflow as tf
import numpy as np
import blackjackEnvironment as benv
import matplotlib
import matplotlib.pyplot as plt


from tf_agents.specs import array_spec
from tf_agents.specs import tensor_spec
from tf_agents.networks import network

from tf_agents import specs
from tf_agents.agents.dqn import dqn_agent
from tf_agents.drivers import dynamic_step_driver
from tf_agents.networks import q_network
from tf_agents.replay_buffers import py_uniform_replay_buffer
from tf_agents.replay_buffers import tf_uniform_replay_buffer
from tf_agents.trajectories import time_step as ts
from tf_agents.environments import tf_py_environment

from tf_agents.eval import metric_utils
from tf_agents.metrics import tf_metrics
from tf_agents.policies import q_policy
from tf_agents.utils import common
from tf_agents.policies import random_tf_policy
from tf_agents.trajectories import trajectory

class TrainAndSaveModel(network.Network):

    #
    #HYPERPARAMETERS
    #
    num_iterations = 25000 #number of batches in an epoch(a single passthrough of a dataset)
    #
    initial_collect_steps = 1000
    collect_steps_per_iteration = 1
    replay_buffer_capacity = 50000
    #
    batch_size = 64 #number of training examples before updating model
    learning_rate  = 0.01 #a measure of how resistant a model is to change (important)
    log_interval = 200 #for printing progress during training
    #
    num_eval_episodes = 10
    eval_interval = 1000 #for deciding when to add a data point of progress
    #END OF HYPERPARAMETERS

    #
    #HELPER METHODS
    #
    #records the data that results from executing the specified policy in the environment into the buffer
    def collect_step(env, policy, buffer):
        time_step = env.current_time_step()
        action_step = policy.action(time_step)
        next_time_step = env.step(action_step.action)
        traject = trajectory.from_transition(time_step, action_step, next_time_step)

        buffer.add_batch(traject)

    #record data over specified number of steps
    def collect_data(env, policy, buffer, steps):
        for _ in range(steps):
            collect_step(env, policy, buffer)

    #average the reward gained by the policy (TODO: parallelize this function)
    def avg_return(env, policy, num_episodes = 10):

        total_return = 0.0
        for _ in range(num_episodes):
            time_step = env.reset()
            episode_return = 0.0

            while(not time_step.is_last()):
                action_step = policy.action(time_step)
                time_step = env.step(action_step.action)
                episode_return += time_step.reward

            total_return += episode_return

        avg_return = total_return/num_episodes
        return avg_return.numpy()[0]
    #END OF HELPER METHODS

    #
    #MAIN EXECUTION
    #

    #initialize environment and wrap it in tf environment
    env = benv.BlackjackEnv()
    tf_env = tf_py_environment.TFPyEnvironment(env)

    #initialize network environment
    network = q_network.QNetwork(tf_env.observation_spec(),
                                 tf_env.action_spec(),
                                 fc_layer_params = (100,))

    #initialize the agent with the listed parameters
    agent = dqn_agent.DqnAgent(tf_env.time_step_spec(),
    	tf_env.action_spec(),
    	q_network = network,
    	optimizer = tf.compat.v1.train.AdamOptimizer(learning_rate = learning_rate),
    	td_errors_loss_fn = common.element_wise_squared_loss,
        train_step_counter = tf.Variable(0))
    agent.initialize()

    #create q policy for the agent to use to evaluate actions
    #policy = q_policy.QPolicy(tf_env.time_step_spec(),
    #                          tf_env.action_spec(),
    #                          q_network = network,
    #                          action_step = 

    
    #create replay buffer to keep track of training
    replay_buffer = tf_uniform_replay_buffer.TFUniformReplayBuffer(agent.collect_data_spec, 
                                                                   batch_size = tf_env.batch_size,
                                                                   max_length = replay_buffer_capacity)


    #add an observer to add to the buffer
    replay_observer = [replay_buffer.add_batch]

    #create step driver
    #collect_op = dynamic_step_driver.DynamicStepDriver(tf_env, agent.collect_policy, observers  = replay_observer, num_steps = 10).run()

    #create random policy to help generate dataset
    random_policy = random_tf_policy.RandomTFPolicy(tf_env.time_step_spec(), tf_env.action_spec())

    #populate replay buffer
    collect_data(tf_env, random_policy, replay_buffer, initial_collect_steps) 

    #generate trajectories; num steps = 2 so that it views current and next observation in dataset
    dataset = replay_buffer.as_dataset(num_parallel_calls = 3,
                                       sample_batch_size = batch_size,
                                       num_steps = 2).prefetch(3)

    #create iterator for dataset to feed the agent
    iterator = iter(dataset)
    #print(iterator)

    #wrap in a graph for TF optimization
    agent.train = common.function(agent.train)

    agent.train_step_counter.assign(0) #reset

    #Evaluate the initialized policy prior to training for baseline
    avg_return = avg_return(tf_env, agent.policy, num_eval_episodes)
    returns = [avg_return] #holds average returns from multiple points during training

    #main training loop
    for _ in range(num_iterations):

        #collect steps and save to buffer based on hyperparameter
        for _ in range(collect_steps_per_iteration):
            collect_step(tf_env, agent.collect_policy, replay_buffer)

        #sample and update network
        exp, _ = next(iterator)
        loss = agent.train(experience).loss

        #get step
        step = agent.train_step_counter.numpy()

        #log progress or evaluate policy if needed (depending on hyperparameters)
        if(step % log_interval == 0):
            print('step = {0}: loss = {1}'.format(step, avg_return))

        if(step % eval_interval == 0):
            avg_return = avg_return(tf_env, agent.policy, num_eval_episodes)
            print('step = {0}: Average retrun = {1}'.format(step, avg_return))
            returns.append(avg_return)



    #results
    iterations = (0, num_iterations+1, eval_interval)

    plt.plot(iterations, returns)
    plt.ylabel('Average Return')
    plt.xlabel('Iteration')
