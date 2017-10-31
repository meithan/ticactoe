import random
# ==============================================================================
# Player agents for tic-tac-toe

# Any player class must have three things:
# self.name: indicates the player's name
# self.mark: stores the assigned playing mark
# self.get_play(self, state): receives a gamestate and returns the move to play
# Might use ABCs in the future

# =====================================

# A player that plays at random
class RandomPlayer():

  def __init__(self, mark=None, quiet=False):
    self.name = "RandomPlayer"
    self.mark = mark
    self.quiet = quiet

  # Receives a GameState and returns the position to play
  def get_play(self, state):
    legal_plays = state.get_legal_plays()
    if len(legal_plays) == 0:
      raise RuntimeError("No legal plays possible!")
    if not self.quiet:
      if random.random() <= 0.3:
        print("RandomPlayer says: I have no idea what I'm doing.")
    return random.choice(legal_plays)

# =====================================

# Plays a winning move if it can, randomly otherwise
# Will win if you let it!
class OpportunistPlayer():

  def __init__(self, mark=None, quiet=False):
    self.name = "OpportunistPlayer"
    self.mark = mark
    self.quiet = quiet

  # Receives a GameState and returns the position to play
  def get_play(self, state):
    legal_plays = state.get_legal_plays()
    if len(legal_plays) == 0:
      raise RuntimeError("No legal plays possible!")
    for play in legal_plays:
      newstate = state.try_play_at(self.mark, play)
      if newstate.get_winner() == self.mark:
        if not self.quiet:
          print("OpportunistPlayer says: Hah, you're toast!")
        return play
    return random.choice(legal_plays)

# =====================================

# If the opponent is about to win, blocks (one of) the winning move; plays
# randomly otherwise
class BlockingPlayer():

  def __init__(self, mark=None, quiet=False):
    self.name = "BlockingPlayer"
    self.mark = mark
    self.quiet = quiet

  # Receives a GameState and returns the position to play
  def get_play(self, state):
    legal_plays = state.get_legal_plays()
    if len(legal_plays) == 0:
      raise RuntimeError("No legal plays possible!")
    for pos in legal_plays:
      opponent = "O" if self.mark == "X" else "X"
      newstate = state.try_play_at(opponent, pos)
      if newstate.get_winner() == opponent:
        if not self.quiet:
          print("BlockingPlayer says: You thought I wouldn't see that, didn't you.")
        return pos
    return random.choice(legal_plays)

# =====================================

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

# =====================================

# A Minimax AI player
# Uses a game cache to greatly speed up score estimation
class MinimaxPlayer:

  def __init__(self, mark=None, debug=False):
    self.name = "MinimaxPlayer"
    self.mark = mark
    self.debug = debug
    self.cache = {}

  # Receives a GameState and returns the position to play
  def get_play(self, state):

    legal_plays = state.get_legal_plays()
    if len(legal_plays) == 0:
      raise RuntimeError("No legal plays possible!")
    self.opp_mark = "O" if self.mark == "X" else "X"

    # Obtain expected scores for all plays
    self.explored = 0
    if self.debug: print("Size of game cache:", len(self.cache))
    play_scores = self.minimax(self.mark, state, 0)
    if self.debug: print("Explored positions:", self.explored)

    # Rank plays by score
    play_scores.sort(key=lambda x: x[1], reverse=True)

    # Determine game result and depth for each play
    if self.debug:
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
      if self.debug: print(play, score, depth)

    # Select best play (pick randomly in case of ties)
    best_plays = [x for x in play_scores if x[1] == play_scores[0][1]]
    best_play, best_score, best_result, best_depth = random.choice(best_plays)
    if self.debug:
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

# =====================================
