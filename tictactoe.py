from copy import deepcopy
import random

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
# PLAYERS

# Any player class must have three things:
# self.name: indicates the player's name
# self.mark: stores the assigned playing mark
# self.get_play(self, state): receives a gamestate and returns the move to play
# Might use ABCs in the future

# A player that plays at random
class RandomPlayer():

  def __init__(self, mark=None):
    self.name = "RandomPlayer"
    self.mark = mark

  # Receives a GameState and returns the position to play
  def get_play(self, state):
    legal_plays = state.get_legal_plays()
    if len(legal_plays) == 0:
      raise RuntimeError("No legal plays possible!")
    if random.random() <= 0.3:
      print("RandomPlayers says: I have no idea what I'm doing.")
    return random.choice(legal_plays)

# Plays a winning move if it can, randomly otherwise
# Will win if you let it!
class OpportunistPlayer():

  def __init__(self, mark=None):
    self.name = "OpportunistPlayer"
    self.mark = mark

  # Receives a GameState and returns the position to play
  def get_play(self, state):
    legal_plays = state.get_legal_plays()
    if len(legal_plays) == 0:
      raise RuntimeError("No legal plays possible!")
    for play in legal_plays:
      newstate = state.try_play_at(self.mark, play)
      if newstate.get_winner() == self.mark:
        print("OpportunistPlayer says: Hah, you're toast!")
        return play
    return random.choice(legal_plays)

# If the opponent is about to win, blocks (one of) the winning move; plays
# randomly otherwise
class BlockingPlayer():

  def __init__(self, mark=None):
    self.name = "BlockingPlayer"
    self.mark = mark

  # Receives a GameState and returns the position to play
  def get_play(self, state):
    legal_plays = state.get_legal_plays()
    if len(legal_plays) == 0:
      raise RuntimeError("No legal plays possible!")
    for pos in legal_plays:
      opponent = "O" if self.mark == "X" else "X"
      newstate = state.try_play_at(opponent, pos)
      if newstate.get_winner() == opponent:
        print("BlockingPlayer says: You thought I wouldn't see that, didn't you.")
        return pos
    return random.choice(legal_plays)

# A "player" that asks the human what to do in the prompt
class HumanPlayer():

  def __init__(self, mark=None):
    self.name = "Human"
    self.mark = mark

  # Receives a GameState and returns the position to play
  # Human must enter comma-separated row and column. (0,0) is upper left.
  def get_play(self, state):
    legal_plays = state.get_legal_plays()
    if len(legal_plays) == 0:
      raise RuntimeError("No legal plays possible!")
    playsstr = " | ".join(["%i,%i" % play for play in legal_plays])
    print("Legal plays:", playsstr)
    accept = False
    while not accept:
      ans = input("Your play: ")
      try:
        i,j = ans.split(",")
        i = int(i)
        j = int(j)
        if i in [0,1,2] and j in [0,1,2] and (i,j) in legal_plays:
          accept = True
      except:
        continue
    return (i,j)

# A Minimax AI player
# Uses a game cache to greatly speed up score estimation
class MinimaxPlayer:

  def __init__(self, mark=None):
    self.name = "MinimaxPlayer"
    self.mark = mark
    self.cache = {}

  # Receives a GameState and returns the position to play
  def get_play(self, state):

    legal_plays = state.get_legal_plays()
    if len(legal_plays) == 0:
      raise RuntimeError("No legal plays possible!")
    self.opp_mark = "O" if self.mark == "X" else "X"

    # Obtain expected scores for all plays
    self.explored = 0
    print("Size of game cache:", len(self.cache))
    play_scores = self.minimax(self.mark, state, 0)
    print("Explored positions:", self.explored)

    # Rank plays by score and determine result and depth
    play_scores.sort(key=lambda x: x[1], reverse=True)
    print("Game analysis:")
    for i in range(len(play_scores)):
      play, score = play_scores[i]
      if score > 0:
        result = +1
        depth = 10 - score
      elif score == 0:
        result = 0
        depth = 9
      elif score < 0:
        result = -1
        depth = 10 + score
      play_scores[i] = play_scores[i] + (result, depth)
      print(play, score, depth)

    # Select best play
    best_play, best_score, best_result, best_depth = play_scores[0]
    plays_togo = best_depth - state.plays
    if best_result == +1:
      expected_str = "WIN in %i plays" % (plays_togo)
    elif best_result == -1:
      expected_str = "LOSS in %i plays" % (plays_togo)
    elif best_result == 0:
      expected_str = "TIE in %i plays" % (plays_togo)
    print("Expected result:", expected_str)
    print("Selected play:", best_play)

    return best_play

  # Serializes a game state (including the player to move) so it can
  # be hashed and cached
  def serialize_state(self, playing, state):
    if playing == self.mark:
      serialized = "A"    # Agent
    else:
      serialized = "O"    # Opponent
    for i in range(3):
      for j in range(3):
        if state.grid[i][j] is None:
          s = "_"
        else:
          s = state.grid[i][j]
        serialized += s
    return serialized

  # Returns (action, score, depth) where score is the optimal expected score
  # (a maximum for the agent, a minimum for its opponent), the action
  # that leads to that optimal score, and the depth of the best winning state
  def minimax(self, cur_player, state, depth):

    # If the passed state is an end state, return the score
    # The score is compound: it includes whether the result is a win, loss
    # or tie, but also the depth required to reach it
    # The idea is that a win is preferable sooner, while a loss or tie is
    # preferable later
    winner = state.get_winner()
    if winner is not None:
      if winner == self.mark:
        return +10 - depth
      elif winner == "tie":
        return 0
      elif winner == self.opp_mark:
        return -10 + depth
      else:
        print(self.mark, self.opp_mark)
        raise RuntimeError("Invalid winner:", winner)

    # If not, get list of actions, obtain the next game state for each
    # play and evaluate its score recursively
    play_scores = []
    for play in state.get_legal_plays():
      new_state = state.try_play_at(cur_player, play)
      next_player = "O" if cur_player == "X" else "X"
      serialized = self.serialize_state(next_player, new_state)
      if serialized in self.cache:
        score = self.cache[serialized]
      else:
        self.explored += 1
        score = self.minimax(next_player, new_state, depth+1)
        self.cache[serialized] = score
      play_scores.append((play, score))

    # Then return the action that maximizes or minimizes the score, depending
    # on who's the current player
    best_score = None
    for play, score in play_scores:
      if best_score is None:
        best_score = score
      else:
        if cur_player == self.mark:
          is_better = score > best_score   # Maximizer
        else:
          is_better = score < best_score   # Minimizer
        if is_better:
          best_score = score

    if depth == 0:
      return play_scores
    else:
      return best_score

# ==============================================================================

# The actual game
class Game():

  # Initializes a new game
  # playerX and playerO must be Player objects
  def __init__(self, playerX, playerO):
    self.playerX = playerX
    self.playerO = playerO
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
      print()
      print("\n== Player %s's turn (%s) ==" % (player.mark, player.name))
      self.gamestate.show()
      play = player.get_play(self.gamestate)
      print("\nPlayer %s plays at %s" % (player.mark, play))
      self.gamestate.play_at(player.mark, play)
      self.plays += 1
      self.to_play = "O" if self.to_play == "X" else "X"
      winner = self.gamestate.get_winner()
      if winner is not None:
        break

    self.ended = True
    if winner == "tie":
      print("\nGAME TIED!")
    else:
      winner = playerX if winner == "X" else playerO
      print("\nPLAYER %s WINS! Congrats, %s!" % (winner.mark, winner.name))
    self.gamestate.show()


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
  playerX = MinimaxPlayer()
  playerO = HumanPlayer()

  game = Game(playerX, playerO)
  game.play()
