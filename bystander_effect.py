import numpy as np
import pandas as pd
import time
import random
from random import choice

A = 100 # win if call police
B =  75 # cost of calling police
NUMBER_OF_STEPS = 60
X_MAX = 17
Y_MAX = 17
NUM_BOTS = 16 

class Bot:
  def __init__(self, name, x, y, hd):
    self.name = name
    self.x = x
    self.y = y
    self.hearing_distance = hd
    self.event_memory = (0, 0)
    
    # Current parameters at each step
    self.distance_event = 0.0
    self.proximity  = 0.0
    self.neighbours = 0
    self.prob_not_call  = 1.0
    self.prob_comb = 0 # Decision to call police: 0 -no, 1 - yes

    # Memory lists that tell the world the status of the bot at the end
    # of the simulation
    self.proximity_memory  = []
    self.x_pos_memory = []
    self.y_pos_memory = []
    self.neighbours_memory = []
    self.prob_memory       = []
    self.calls_police      = []
  
  def compute_distance(self, x2, y2):
    xsq = (self.x - x2) ** 2
    ysq = (self.y - y2) ** 2
    self.event_memory = (x2, y2)
    return round(np.sqrt(xsq + ysq), 2)
  
  def compute_proximity(self):
    if self.distance_event > self.hearing_distance:
      self.proximity = 0.0
      self.proximity_memory.append(self.proximity)
    else:
      # Probability that a person will not call police increases with increase of
      # distance from event. Proximity = probability not call police. Let the impact
      # be linear for now
      self.proximity = (self.distance_event / self.hearing_distance)
      self.proximity = round(self.proximity, 3)
      self.proximity_memory.append(self.proximity)

  def find_neighbours(self, bot_list):
    self.neighbours = 0
    for bystander in bot_list:
      if bystander.name == self.name:
        continue
      else:
        my_dist = self.compute_distance(bystander.x, bystander.y)
        if my_dist <= self.hearing_distance:
          self.neighbours += 1
    self.neighbours_memory.append(self.neighbours)
    self.x_pos_memory.append(self.x)
    self.y_pos_memory.append(self.y)

  def bystander_standalone(self, a, b):
    if self.neighbours >= 2:
      power_value = 1 / (self.neighbours - 1)
      base_value  = b / (self.neighbours * a)
      self.prob_not_call = round(base_value ** power_value, 3)
      self.prob_memory.append(self.prob_not_call)
    else:
      self.prob_not_call = 0.0
      self.prob_memory.append(self.prob_not_call)
    print("{}: n={}, prob_not_call={}".format(self.name, self.neighbours, self.prob_not_call))
  
  def bystander_combined(self):
    self.prob_comb = self.prob_not_call * self.proximity # prob of not calling police
    self.prob_comb = 1 / (1 + np.exp(-self.prob_comb))   # decision to not call police
    self.prob_comb = 1 - self.prob_comb                  # decision to call police
    if self.prob_comb >= 0.5:
      self.prob_comb = 1 # call police
    else:
      self.prob_comb = 0 # not call police
    self.calls_police.append(self.prob_comb)
    print("{} calls police = {}".format(self.name, self.prob_comb))

  def compute_new_dist(self, point):
    xsq = (self.event_memory[0] - point[0]) ** 2
    ysq = (self.event_memory[1] - point[1]) ** 2
    return round(np.sqrt(xsq + ysq), 2)

  
  def move_bot(self, matrix):
    print("Move {}".format(self.name))
    # A bot can move in 8 directions and occupy free spots on the grid
    # A bot tends to decrease proximity and avoids moves that increase it
    # (this is avoiding event as much as possible)
    # If a bot hits the end of the grid, it does not move and stay there
    d1 = (self.x + 1, self.y)
    d2 = (self.x + 1, self.y + 1)
    d3 = (self.x, self.y + 1)
    d4 = (self.x - 1, self.y + 1)
    d5 = (self.x - 1, self.y)
    d6 = (self.x - 1, self.y - 1)
    d7 = (self.x, self.y - 1)
    d8 = (self.x + 1, self.y - 1)
    directions = [d1, d2, d3, d4, d5, d6, d7, d8]

    # Pick random direction and test it for conditions -- accept if all satisfied
    # This is mimicking Monte Carlo method where current state depends only
    # on previous state
    occupied_cells = list(zip(*np.where(matrix == 1)))
    count_trials   = 0
    new_point      = ()

    while count_trials < 10 and len(new_point) == 0:
      new_dir = choice(directions)
      new_dist = self.compute_new_dist(new_dir)      
      if new_dist > self.distance_event:
        test1 = True
      else:
        test1 = False
      if all(item > 0 for item in new_dir):
        test2 = True
      else:
        test2 = False
      if all(item < matrix.shape[0] for item in new_dir):
        test3 = True
      else:
        test3 = False
      if new_dir in occupied_cells:
        test4 = False
      else:
        test4 = True
      tests = [test1, test2, test3, test3]
      if all(tests):
        print("Move {} from {} to {}".format(self.name, (self.x, self.y), new_dir))
        new_point = new_dir
        self.x = new_dir[0]
        self.y = new_dir[1]
      count_trials += 1




class World:
  def __init__(self, width, height):
    self.width  = width
    self.height = height
    self.matrix = np.zeros((width, height), dtype=int)
    self.bot_list = []
    self.event_x = 0
    self.event_y = 0
    self.x_dim = range(self.width)
    self.y_dim = range(self.height)

    # History lists to hold full story of simulation
    self.x_history = []
    self.y_history = []
    self.col_history = []
  
  # Create new event and place randomly in the world
  def add_event(self):
    x = choice(range(self.width))
    y = choice(range(self.height))
    self.matrix[x, y] = 1
    self.event_x = x
    self.event_y = y
  
  # Add new bot
  def add_bot(self, bot_name):    
    # Update coordinates not occupied by an event or other bots
    # Do not place two entities on the same spot
    index_ones = list(zip(*np.where(self.matrix == 1)))
    index_ones = np.column_stack(index_ones)
    x_free = np.delete(self.x_dim, index_ones[0])
    y_free = np.delete(self.y_dim, index_ones[1])

    # Randomly place a bot on the grid amd update matrix
    x = choice(x_free)
    y = choice(y_free)
    self.matrix[x, y] = 1

    # Create new bot and add it to the list of bots
    hd = choice(np.arange(5, 10, 1))
    self.bot_list.append(Bot(bot_name, x, y, hd))
  
  # Compute proximity to event
  def compute_effect(self, step):
    print("\nCompute effect on step {}".format(step))
    
    for bot in self.bot_list:
      # Compute proximity to event
      bot.distance_event = bot.compute_distance(self.event_x, self.event_y)
      bot.compute_proximity()
      # Comput distance to neighbours and find neigbours within hearing distance
      bot.find_neighbours(self.bot_list)      
      # Compute bystander effect standalone
      bot.bystander_standalone(A, B)
      # Compute bystander effect combined with proximity to event
      bot.bystander_combined()

  def move_bots(self, step):
    print("\nMove bots on step {}".format(step))
    for bot in self.bot_list:
      # Record old coordinates to be able to free a spot on the grid after move
      old_coord = [bot.x, bot.y]
      bot.move_bot(self.matrix)
      # Free old spot and occupy new spot on the grid
      self.matrix[old_coord[0], old_coord[1]] = 0
      self.matrix[bot.x, bot.y] = 1
  
  def collect_history(self):
    for bot in self.bot_list:
      print("Collect plot data history for {}".format(bot.name))
      self.x_history.append(bot.x_pos_memory)
      self.y_history.append(bot.y_pos_memory)
      self.col_history.append(bot.calls_police)
    self.x_history = pd.DataFrame(self.x_history).T.add_prefix("bot")
    self.y_history = pd.DataFrame(self.y_history).T.add_prefix("bot")
    self.col_history = pd.DataFrame(self.col_history).T.add_prefix("bot")


def main():
  generations    = 0
  NewWorld = World(X_MAX, Y_MAX)
  NewWorld.add_event()

  for bot_number in range(NUM_BOTS):
    bot_name = "bot" + str(bot_number)
    NewWorld.add_bot(bot_name)
  
  for step in range(NUMBER_OF_STEPS):
    NewWorld.compute_effect(step)
    NewWorld.move_bots(step)
  
  NewWorld.collect_history()
  pd.DataFrame({'x': NewWorld.event_x, 'y': NewWorld.event_y}, index = [0]).\
          to_csv('event.csv', index = False)
  NewWorld.x_history.to_csv('x_hist.csv', index = False)
  NewWorld.y_history.to_csv('y_hist.csv', index = False)
  NewWorld.col_history.to_csv('col_hist.csv', index = False)
  pd.DataFrame({'x': X_MAX, 'y': Y_MAX}, index = [0]).to_csv('xy_max.csv', index = False)


if __name__ == '__main__':
 start_time = time.time()
 main()
 end_time = time.time()
 duration = end_time - start_time
 print("\nRuntime for this program is {} seconds".format(duration))
