import random
from tictactoe import *

# ================================

num_trials = 1000000
agent = MinimaxPlayer()
opponent = RandomPlayer(quiet=True)

# ================================

wins = 0
ties = 0
losses = 0

for ntrial in range(1,num_trials+1):

  # Determine starting player
  starting = random.random() > 0.5
  if starting:
    playerX = agent
    playerO = opponent
  else:
    playerX = opponent
    playerO = agent

  game = TicTacToe(playerX, playerO, quiet=True)
  winner = game.play()

  if winner == agent.mark:
    wins += 1
  elif winner == opponent.mark:
    losses += 1
  else:
    ties += 1

  if ntrial % (num_trials//20) == 0:
    print("%i/%i (%i%%)" % (ntrial, num_trials, 100*ntrial/num_trials))

print("Wins:", wins)
print("Ties:", ties)
print("Losses:", losses)

strength = (wins + ties/2) / num_trials
print("Strength:", strength)
