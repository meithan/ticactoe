import datetime
import random
import os
from tictactoe import *
from players import *
from NNPlayer import *
import numpy as np

# ================================

def evaluate_player(player, num_games, opponent=None, report=False, xs=None):

  if opponent is None:
    opponent = RandomPlayer(quiet=True)

  if xs is not None:
    ys = []

  wins = 0
  ties = 0
  losses = 0
  start = datetime.datetime.now()

  for ntrial in range(1,num_games+1):

    # Determine starting player
    starting = random.random() > 0.5
    if starting:
      playerX = player
      playerO = opponent
    else:
      playerX = opponent
      playerO = player

    game = TicTacToe(playerX, playerO, quiet=True)
    winner = game.play()

    if winner == player.mark:
      wins += 1
    elif winner == opponent.mark:
      losses += 1
    else:
      ties += 1

    if report:
      if ntrial % (num_games//20) == 0:
        print("{:,}/{:,} ({:.0f}%)".format(ntrial, num_games, 100*ntrial/num_games))

    if xs is not None:
      if ntrial in xs:
        strength = (wins + ties/2) / ntrial
        ys.append(strength)
        if report: print("{:,} {:.7f}".format(ntrial, strength))

  strength = (wins + ties/2) / ntrial
  elapsed = (datetime.datetime.now() - start).total_seconds()
  results = (strength, wins, ties, losses, elapsed)
  if xs is not None:
    results += (ys,)

  return results

# ================================

if __name__ == "__main__":

  import matplotlib.pyplot as plt

  #agents = [MinimaxPlayer(), RandomPlayer(quiet=True), NNPlayer(fname="random.nn"), OpportunistPlayer(quiet=True), BlockingPlayer(quiet=True)]
  players = [RandomPlayer(quiet=True)]

  num_games = 100000

  opponent = RandomPlayer()
  xs = np.logspace(1, np.log10(num_games), 31, dtype=int)

  for player in players:

    print("Player:", player.name)

    strength, wins, ties, losses, elapsed, ys = evaluate_player(player, num_games=num_games, report=True, xs=xs)

    print("Wins: %i (%.1f%%)" % (wins, 100*wins/num_games))
    print("Ties: %i (%.1f%%)" % (ties, 100*ties/num_games))
    print("Losses: %i (%.1f%%)" % (losses, 100*losses/num_games))

    strength = (wins + ties/2) / num_games
    print("Strength:", strength)

    timestr = "%im %.1fs" % divmod(elapsed, 60)
    print("Elapsed:", timestr)

    #plt.plot(ys)
    plt.figure()
    plt.clf()
    plt.semilogx(xs, ys, "o-")
    plt.xlabel("Number of games")
    plt.ylabel("Measured player strength")
    title = player.name
    title += "\nStrength: %.4f (vs. %s)" % (strength, opponent.name)
    title += "\n{:,} games in {}".format(num_games, timestr)
    title += "\n{:,} wins - {:,} ties - {:,} losses".format(wins, ties, losses)
    plt.title(title, fontsize=10)
    plt.grid()
    plt.subplots_adjust(top=0.845)

#    outfname = "trials_%s.png" % player.name.replace("Player","")
#    plt.savefig(outfname)
#    print("Wrote %s" % outfname)
    plt.show()
