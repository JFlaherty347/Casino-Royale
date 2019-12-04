# Casino-Royale
## What is this Repository?
Tasked with employing a creative use of parallelism in the creation of casino games, we set out to make a blackjack AI that 
plays multiple hands at once and a horce race simulator.

## Blackjack AI Model
The blackjack AI uses a [DDQN](https://en.wikipedia.org/wiki/Q-learning), as described [in this paper](https://arxiv.org/abs/1509.06461), in order to achieve success playing
blackjack. It was created using [Tensorflow 2.0](https://www.tensorflow.org/) and [TF Agents](https://github.com/tensorflow/agents). 

## Blackjack AI Training
The training process involved 200,000 iterations, rewarding the agent as follows: 
``` 
-21 + sum,  if sum <= 21
-21,        if sum > 21
```
The process was accelerated through using Tensorflow-GPU, allowing more massive parallelization during the lengthy training  
process.

## Use of Parallelization in Multihand Blackjack
Via Python's Threading library, it becomes much easier to keep track of multiple hands of blackjack at the same time. This
emulates either having multiple players or playing multiple hands at the same time.

## Evaluation of the Blackjack Model
In its current state, the agent is able to achieve ~44% win/tie rate against a standard dealer.

## Accreditations
Joseph Flaherty - Blackjack AI, Blackjack GUI

Aaron Jimenez - Horse racing simulator, Horse racing GUI, Main menu GUI, Music functionality
