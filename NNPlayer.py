from NeuralNetwork import NeuralNetwork
import numpy as np

# A Neural Network tictacoe player
class NNPlayer:

  def __init__(self, mark=None, NN=None, fname=None, debug=False):
    self.name = "NeuralNetwork"
    self.mark = mark
    if NN is not None:
      self.NN = NN
    else:
      self.NN = None
      if fname is not None:
        self.load_NN_from_file(fname)
    self.debug = debug

  # Loads a NN definition from file
  def load_NN_from_file(self, fname):
    self.NN = NeuralNetwork()
    self.NN.load_from_file(fname)

  # Receives a GameState and returns the position to play
  # Human must enter comma-separated row and column. (0,0) is upper left.
  def get_play(self, state):

    invalues = np.zeros(9)
    for i in range(3):
      for j in range(2):
        if state.grid[i][j] is None:
          invalues[3*i+j] = 0
        elif state.grid[i][j] == "X":
          invalues[3*i+j] = +1
        elif state.grid[i][j] == "O":
          invalues[3*i+j] = -1

    # Evaluate the network
    outvalues = self.NN.evaluate(invalues)

    # Filter out and sort legals plays
    legal_plays = state.get_legal_plays()
    play_scores = []
    for i in range(9):
      pos = (i // 3, i % 3)
      if pos in legal_plays:
        play_scores.append((pos, outvalues[i]))
    play_scores.sort(key=lambda x: x[1], reverse=True)

    if self.debug:
      print("Play scores")
      for play, score in play_scores:
        print(play, "%.5f" % score)

    return play_scores[0][0]

# ================================

if __name__ == "__main__":

  from tictactoe import *

  playerX = NNPlayer(fname="random.nn")
  playerO = RandomPlayer()

  game = Game(playerX, playerO, quiet=False)
  winner = game.play()
