# Connect-Four-AI

## Aims

The aims of this repository are:
* Ensure that the entire project is created whilst adhering to good coding practices and the object-orientated programming paradigm.
* Train a Reinforcement Learning agent to play Connect Four against a human opponent, and win.

I understand that Connect Four is a solvable game with the use of an efficient tree-search algorithm of all possible moves.
However, the primary purpose of this project is for me to develop my knowledge of reinforcement learning algorithms and environments in which they can learn.

In addition, I believe it would be interesting to see how a reinforcement learning agent would perform on a larger game board, in comparison to a human player, with the theory that a larger game board would be unsolvable.

## Connect Four

Connect four is a board game played between two people who take it in turns to drop a counter into one of7 columns, each of which is usually 6 spaces high.
The aim is to be the first person to have a line of 4 counters in any horizontal, vertical or diagonal row.

## The Agents

I hope to use Reinforcement Learning algorithms, specifically policy gradient methods, to create agents.
These agents will be trained by making them play games against other agents, and themselves (self-play).

To do this, I will use the Gym Environments and Stable-Baselines to create the agents.

## Downloading

The easiest way to download the code is to press the download button on the home page of the GitHub repository.

## Use

The best way to use the program currently is to call it from the command line using:

```sh
python3 play.py -p2 ppo
```

This will let you play an exhibition game against a default RL agent.

## Next Steps

The next steps are:
* Create a GUI for the game to better show the board during the game.
* Improve upon current agents.
* Look into multi-agent environments for true self-play.
