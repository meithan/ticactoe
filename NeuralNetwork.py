import random
import numpy as np

class NeuralNetwork:

  # Class constructor takes two parameters:
  # L: the number of layers (L >= 3) in the NN
  # Ns: a list of length L with the number of neurons for each layer
  # Layer 0 is the input layer while layer L-1 is the output layer
  # Neurons are always fully connected between layers
  def __init__(self, L=None, Ns=None):
    self.L = L
    self.Ns = Ns
    if L is not None and Ns is not None:
      assert L >= 3
      self.L = L
      self.Ns = list(Ns)
      assert len(self.Ns) == L
      self.initialize()

  # Initializes the NN
  # Separated from the constructor so it can also be called after
  # loading a definition from file
  def initialize(self):
    assert self.L is not None
    assert self.Ns is not None
    self.weights = []
    self.biases = []
    for l in range(1, self.L):
      self.weights.append(np.zeros((self.Ns[l], self.Ns[l-1])))
      self.biases.append(np.zeros(self.Ns[l]))
    self.wshape = self.weights[0].shape

  # Randomizes all weights
  def randomize(self):
    for l in range(self.L-1):
      M, N = self.weights[l].shape
      self.weights[l] = np.random.rand(M, N)

  # Returns a "serialized" version of all weights and biases so that they
  # can be more easily fed to optimizations algorithms
  def serialize(self):
    serial = np.array([], dtype=self.weights[0].dtype)
    for l in range(self.L-1):
      M, N = self.weights[l].shape
      serial = np.concatenate([serial, self.weights[l].reshape(M*N)])
      serial = np.concatenate([serial, self.biases[l]])
    return serial

  # Unpacks and loads the serialized weights and biases
  def load_serialized(self, serial):
    i0 = 0
    for l in range(self.L-1):
      M, N = self.weights[l].shape
      K = len(self.biases[l])
      self.weights[l] = serial[i0:i0+M*N].reshape(M,N)
      self.biases[l] = serial[i0+M*N:i0+M*N+K]
      i0 = M*N + K

  # Saves the definition of the neural network to a file
  # Excluding comments:
  # The first line is L,
  # The second line is the the list Ns,
  # Then the L-1 weight matrices follow, one at a time, each preceeded by its shape
  def save_to_file(self, fname):
    f = open(fname, "w")
    f.write("# L\n")
    f.write("%i\n" % self.L)
    f.write("# Ns\n")
    f.write("%s\n" % " ".join("%i" % N for N in self.Ns))
    for l in range(self.L-1):
      f.write("# l=%i\n" % (l+1))
      w = self.weights[l]
      f.write("%i %i\n" % (w.shape))
      for i in range(w.shape[0]):
        f.write("%s\n" % " ".join("%f" % x for x in w[i,:]))
    f.close()

  # Loads a NN definition from file
  def load_from_file(self, fname):
    f = open(fname)
    f.readline()
    self.L = int(f.readline().strip())
    f.readline()
    self.Ns = list(map(int, f.readline().strip().split()))
    self.initialize()
    for l in range(self.L-1):
      f.readline()
      shape = tuple(map(int, f.readline().strip().split()))
      M, N = shape
      for i in range(M):
        row = list(map(float, f.readline().strip().split()))
        for j in range(N):
          self.weights[l][i,j] = row[j]

  # The activation function
  # Currently a logistic sigmoid
  def activation(self, values):
    return np.tanh(values)
    #return 1 / (1 + np.exp(-values))

  # Feedforward evaluation
  def evaluate(self, input_values):
    invals = input_values[:]
    for l in range(self.L-1):
      tmp = np.dot(self.weights[l], invals) + self.biases[l]
      outvals = self.activation(tmp)
      invals = outvals[:]
    return outvals

# ===============================

if __name__ == "__main__":

  NN = NeuralNetwork(L=3, Ns=[9,9,9])
  NN.randomize()
  NN.save_to_file("random.nn")

  print(NN.weights[0], NN.weights[1], NN.biases)

  serial = NN.serialize()
  #print(serial, serial.size)

  NN.load_serialized(serial)
  print("\n\n")
  print(NN.weights[0], NN.weights[1], NN.biases)
