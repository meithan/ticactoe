from copy import deepcopy
import random
from players import *

# ==============================================================================

# The game state
class GameState:

  # Creates a new game
  # The state ot the grid (a "3x3" python list) is an optional argument
  # Each "square" holds either "X", "O" or None
  def __init__(self, grid=None):
    if grid is None:
      self.grid = [[None,None,None],[None,None,None],[None,None,None]]
      self.plays = 0
    else:
      self.grid = deepcopy(grid)
      self.plays = self.count_plays()

  # Plays for player ("X" or "O") at pos (i,j)
  def play_at(self, player, pos):
    i,j = pos
    if self.grid[i][j] is not None:
      raise RuntimeError("Illegal play!")
    self.grid[i][j] = player
    self.plays += 1

  # Returns the gamestate that results from player playing at pos
  def try_play_at(self, player, pos):
    i,j = pos
    if self.grid[i][j] is not None:
      raise RuntimeError("Illegal play!")
    newstate = GameState(self.grid)
    newstate.play_at(player, pos)
    return newstate

  # Returns the list of (i,j) squares of legal plays (i.e. unplayed squares)
  def get_legal_plays(self):
    legal_plays = []
    for i in range(3):
      for j in range(3):
        if self.grid[i][j] is None:
          legal_plays.append((i,j))
    return legal_plays

  # Counts the number of played squares
  def count_plays(self):
    count = 0
    for i in range(3):
      for j in range(3):
        if self.grid[i][j] is not None:
          count += 1
    return count

  # Returns whether the grid has no played squares
  def is_empty(self):
    return self.plays == 0

  # Returns whether the grid has no unplayed squares left
  def is_full(self):
    return self.plays == 9

  # Returns whether the game state is a winning position (three in line)
  def is_winning(self):
    return self.get_winner() is not None

  # Returns the winner of the game state: the player or 0 if no winner
  def get_winner(self):
    winners = []
    for player in ["X", "O"]:
      # Rows
      for i in range(3):
        if self.grid[i][0] == self.grid[i][1] == self.grid[i][2] == player:
          if player not in winners:
            winners.append(player)
          continue
      # Columns
      for j in range(3):
        if self.grid[0][j] == self.grid[1][j] == self.grid[2][j] == player:
          if player not in winners:
            winners.append(player)
          continue
      # Diagonals
      if (self.grid[0][0] == self.grid[1][1] == self.grid[2][2] == player)\
      or (self.grid[0][2] == self.grid[1][1] == self.grid[2][0] == player):
        if player not in winners:
          winners.append(player)
    if len(winners) == 0:
      if self.is_full():
        return "tie"
      else:
        return None
    elif len(winners) == 1:
      return winners[0]
    else:
      raise RuntimeError("Illegal board with 2 winners!")

  # ASCII representation of the game state
  def show(self):
    for i in range(3):
      s = ""
      for j in range(3):
        s += " "
        if self.grid[i][j] is None:
          symb = " "
        elif self.grid[i][j] in ["X","O"]:
          symb = self.grid[i][j]
        else:
          raise RuntimeError("Illegal symbol found in grid!")
        s += symb
        if j != 2:
          s += " |"
      print(s)
      if i != 2:
        print("-----------")

# ==============================================================================

# The actual game
class TicTacToe():

  # Initializes a new game
  # playerX and playerO must be Player objects
  def __init__(self, playerX, playerO, quiet=False):
    self.playerX = playerX
    self.playerO = playerO
    self.quiet = quiet
    self.playerX.mark = "X"
    self.playerO.mark = "O"
    self.plays = 0
    self.ended = False
    self.gamestate = GameState()
    self.to_play = "X"

  # Plays the game
  def play(self):

    while True:
      if self.to_play == "X":
        player = self.playerX
      elif self.to_play == "O":
        player = self.playerO
      else:
        raise RuntimeError("Invalid player: %s" % str(self.to_play))
      if not self.quiet:
        print()
        print("\n== Player %s's turn (%s) ==" % (player.mark, player.name))
        self.gamestate.show()
      play = player.get_play(self.gamestate)
      if not self.quiet:
        print("\nPlayer %s plays at %s" % (player.mark, play))
      self.gamestate.play_at(player.mark, play)
      self.plays += 1
      self.to_play = "O" if self.to_play == "X" else "X"
      winner = self.gamestate.get_winner()
      if winner is not None:
        break

    self.ended = True
    if not self.quiet:
      if winner == "tie":
        print("\nGAME TIED!")
      else:
        winner = self.playerX if winner == "X" else self.playerO
        print("\nPLAYER %s WINS! Congrats, %s!" % (winner.mark, winner.name))
      self.gamestate.show()

    return winner


# ==============================================================================

if __name__ == "__main__":

  # gs = GameState()
  # for i in range(3):
  #   for j in range(3):
  #     gs.grid[i,j] = random.choice([0,1,2])
  # gs.show()
  # print("Legal plays:", gs.get_legal_plays())
  # print("Is empty:", gs.is_empty())
  # print("Is full:", gs.is_full())
  # print("Is winning:", gs.is_winning())
  # print("Winner:", gs.get_winner())
  #
  # #player = RandomPlayer()
  # #player = SimplePlayer()
  # player = HumanPlayer()
  #
  # pos = player.play(gs)
  # print("\nPlayer 1 plays at", pos)
  # gs.play_at(1, pos)
  #
  # gs.show()
  # print("Legal plays:", gs.get_legal_plays())
  # print("Is empty:", gs.is_empty())
  # print("Is full:", gs.is_full())
  # print("Is winning:", gs.is_winning())
  # print("Winner:", gs.get_winner())

  # Available players
  # RandomPlayer: plays at random
  # OpportunistPlayer: plays winning move if it can, random otherwise
  # BlockingPlayer: blocks opponent's winning move if it can, random otherwise
  # MinimaxPlayer: a full Minimax agent. Plays almost perfectly.
  # HumanPlayer: a human playing through the terminal
  playerX = MinimaxPlayer(debug=True)
  playerO = HumanPlayer()

  game = TicTacToe(playerX, playerO, quiet=False)
  winner = game.play()
