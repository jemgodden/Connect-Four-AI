# Connect-Four-AI

## Background

The primary aim of this project is to create and train a reinforcement learning (RL) agent to play the board game Connect Four.
Connect Four was chosen as it is a simple game that can be used as a starting place to learn about reinforcement learning and to begin developing RL agents and environments.
It is worth acknowledging that a standard game of Connect Four is [solvable](https://connect4.gamesolver.org/#) using an efficient tree-search algorithm of all possible moves. Thus, the standard agents developed will not be groundbreaking by any means.

In addition, I believe it would be interesting to see how a reinforcement learning agent would perform on a larger game board against a human player.
The theory is that a larger game board is unsolvable, and that a RL Agent will outperform a human player.

A final aim of this project is to practice writing complete, production-level code that adheres to common programming principles.

## Connect Four

[Connect Four](https://en.wikipedia.org/wiki/Connect_Four) is a board game played between two people who take it in turns to drop a counter into one of 7 columns, each of which typically has 6 spaces.
The aim of the game is to be the first person to have a line of 4 counters in any horizontal, vertical or diagonal row.

## The Agents

I hope to use reinforcement learning algorithms, specifically policy gradient methods, to create agents.
These agents will be trained by making them play games against other simple agents, heuristic agents, and other RL agents, or event themselves (self-play).

I will create these agents, and the environment, using the TensorFlow framework.

## Usage

The best way to play an exhibition game is to call the play.py script from the command line using:

```sh
python3 play.py -p2 look
```

## Next Steps

The next steps for this project are:
* Create a GUI for the game.
* Train an agent on a larger board using Cloud Computing resources.
* Look into multi-agent environments for true self-play.
