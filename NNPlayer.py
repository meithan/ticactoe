

# A Neural Network tictacoe player
class NNPlayer:

  def __init__(self, mark=None):
    self.name = "Human"
    self.mark = mark

  # Receives a GameState and returns the position to play
  # Human must enter comma-separated row and column. (0,0) is upper left.
  def get_play(self, state):
