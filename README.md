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
The process was accelerated through using Tensorflow-GPU, allowing more massive parallelization during the lengthy training process. A graph of the average return that the agent was getting during training is shown below. Keep in mind that the graph is scaled from 0 to 21, with 0 being the best for anyone iteration. The points are marked with average return so reaching zero is improbable as it would require the agent to get a score of 21 1000 times in a row.

![Graph of Training](https://github.com/JFlaherty347/Casino-Royale/blob/master/Blackjack_AI/graphs/DDQN-FINAL-200k.png)

## Application of Agent
The agent was applied in an application where it's policy is used to make decisions in a hand of blackjack visible to the user. The game state is shown through a GUI and also keeps track of running balances of players.

![Image of Blackjack GUI](https://github.com/JFlaherty347/Casino-Royale/blob/master/Images/BlackjackGUI.png)

## Use of Parallelism in Application
Via Python's Threading library, it becomes much easier to keep track of multiple hands of blackjack at the same time. This emulates either having multiple players or playing multiple hands at the same time. Threads in python are primarily useful for organization due to the fact that the [Global Interpreter Lock](https://wiki.python.org/moin/GlobalInterpreterLock) means only one thread can have control over the interpreter at a time.

## Evaluation of the Blackjack Model
In its current state, the agent is able to achieve ~44% win/tie rate against a standard dealer. This estimate was done through running 4 hands at the same time for 100000 games and keeping track of any time the agent won or tied the dealer. The results are outlined below:
```
Player 1: 44172/100000
Player 2: 44173/100000
Player 3: 43823/100000
Player 4: 44164/100000
Average: 44083/100000

Win/Tie Rate: 44.083%
```

## Accreditations
Joseph Flaherty - Blackjack AI, Blackjack GUI

Aaron Jimenez - Horse racing simulator, Horse racing GUI, Main menu GUI, Music functionality
