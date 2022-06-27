from random import uniform
from natura.util import circle_to_mass

TYPE_PLANT      = 0
TYPE_MEAT       = TYPE_PLANT + 1
TYPE_POOP       = TYPE_MEAT + 1

PLANT_COLOR     = (100, 255, 100)
MEAT_COLOR      = (170, 60, 59)
POOP_COLOR      = (115, 74, 22)

PLANT_ENERGY    = 0.5
MEAT_ENERGY     = 1.5
POOP_ENERGY     = 0

class Food():
    def __init__(self, pos: tuple, type: int = TYPE_PLANT):
        self.color  = PLANT_COLOR  if type == TYPE_PLANT else MEAT_COLOR  if type == TYPE_MEAT else POOP_COLOR
        self.pos    = pos
        self.radius = uniform(.3, 1)
        self.update()
    
    def eat(self, radius: float) -> float:
        '''
        Take a bite out of the food, returns the energy consumed\n
        radius is in meters
        '''
        old_energy = self.energy
        self.radius = max(self.radius - radius, 0)
        self.update()
        return old_energy - self.energy

    def update(self):
        div         = PLANT_ENERGY if type == TYPE_PLANT else MEAT_ENERGY if type == TYPE_MEAT else POOP_ENERGY
        self.energy = circle_to_mass(self.radius) * div