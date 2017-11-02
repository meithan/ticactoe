# Trains a neural network to play tic-tac-toe using Particle
# Swarm Optimization
import random
import numpy as np
from NeuralNetwork import NeuralNetwork
from NNPlayer import NNPlayer
from trials import evaluate_player

# ==================================

# PSO global constants
xi = 0.72984
c1 = 2.05
c2 = 2.05

# The particles, yo
# Note that fitness calculation has been outsourced to the trainer class
# so that it can be computed in parallel
class Particle:

  def __init__(self, pos=None, vel=None):
    if pos is None:
      self.pos = None
    else:
      self.pos = np.copy(pos)
    if vel is None:
      self.vel = None
    else:
      self.vel = np.copy(vel)
    self.fitness = None
    self.neighbors = None
    self.best_pos = None
    self.best_fit = None

  # Update the particle velocity
  # Assumes fitness of all particles has been computed
  def update_vel(self):

    # Obtain best pos of neighbors
    best_npos = None
    best_nfit = None
    for neigh in self.neighbors:
      if best_npos is None or neigh.fitness > best_nfit:
        best_nfit = neigh.fitness
        best_npos = neigh.pos

    # The update
    e1 = np.random.random(self.vel.shape)
    e2 = np.random.random(self.vel.shape)
    self.vel = \
      xi * ( \
      self.vel \
      + c1 * e1 * (self.best_pos - self.pos) \
      + c2 * e2 * (best_npos - self.pos) \
      )

  # Moves the particle (only)
  # Assumes velocity is updated
  def move(self):
    self.pos = self.pos + self.vel

  # Updates the best position the particle has seen so far
  # Assumes fitness for the current position has been calculated
  def update_best_pos(self):
    if self.best_pos is None or self.fitness > self.best_fit:
      self.best_fit = self.fitness
      self.best_pos = self.pos

# Receives a NNagent and uses the PSO algorithm to train it
class PSOTrainer:

  # num_steps is the number of steps of the PSO
  # num_parts is the number of particles to use
  # num_neighs is the number of neighbors each particle has
  # num_games is the number of games used to determine the win ratio
  def __init__(self, num_steps=1000, num_parts=100, num_neighs=5, num_games=100000):
    self.num_steps = num_steps
    self.num_parts = num_parts
    self.num_games = num_games
    self.num_neighs = num_neighs
    self.particles = []

  # Evaluates the fitness of the particle
  def eval_fitness(self, particle):
    NN = NeuralNetwork(L=3, Ns=[9,9,9])
    NN.load_serialized(particle.pos)
    player = NNPlayer(NN=NN)
    results = evaluate_player(player, self.num_games)
    strength = results[0]
    # Hack to prevent weight explosion
    # if np.sum(np.abs(NN.weights[0])) > 1800 or np.sum(np.abs(NN.weights[1])) > 1800:
    #   strength = 0
    return strength

  # The actual training routine
  def train(self):

    # Create particles (with random NNs)
    print("Creating particles ...")
    for i in range(self.num_parts):
      p = Particle()
      NN = NeuralNetwork(L=3, Ns=[9,9,9])
      NN.randomize()
      p.pos = NN.serialize()
      #p.vel = np.random.rand(len(p.pos))
      p.vel = np.zeros(len(p.pos))
      self.particles.append(p)

    # Randomly set neighbors
    print("Setting neighbors ...")
    for i in range(self.num_parts):
      particle = self.particles[i]
      particle.neighbors = []
      while len(particle.neighbors) < self.num_neighs:
        neigh = random.choice(self.particles)
        if neigh is not particle:
          particle.neighbors.append(neigh)

    # Evaluate initial fitness
    print("Initializing ...")
    fits = []
    for i,particle in enumerate(self.particles):
      particle.fitness = self.eval_fitness(particle)
      particle.update_best_pos()
      fits.append(particle.fitness)
    print("Max fitness: %.5f" % max(fits))
    print("Avg fitness: %.5f" % np.mean(fits))
    print("Min fitness: %.5f" % min(fits))
    print("Std fitness: %.5f" % np.std(fits))

    # Main loop
    print("\nTRAINING ...")
    for step in range(1,self.num_steps+1):

      print("\nStep %i" % step)

      for i,particle in enumerate(self.particles):
        particle.update_vel()
        particle.move()
        particle.fitness = self.eval_fitness(particle)
        particle.update_best_pos()
        if i % 1 == 0:
          print("=", end="", flush=True)
      print()

      best_part = None
      best_fit = None
      fits = []
      for particle in self.particles:
        fits.append(particle.fitness)
        if best_fit is None or particle.fitness > best_fit:
          best_fit = particle.fitness
          best_part = particle
      print("Max fitness: %.5f" % max(fits))
      print("Avg fitness: %.5f" % np.mean(fits))
      print("Min fitness: %.5f" % min(fits))
      print("Std fitness: %.5f" % np.std(fits))

      outfname = "swarm_%03i.nn" % step
      NN = NeuralNetwork(L=3, Ns=[9,9,9])
      NN.load_serialized(best_part.pos)
      NN.save_to_file(outfname)
      print("Saved best to %s" % outfname)


# ============================================

trainer = PSOTrainer(num_parts=50, num_games=1000)
trainer.train()
