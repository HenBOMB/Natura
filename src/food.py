import random
from tools import clamp, energy_to_mass, mass_to_energy

TYPE_PLANT = 0
TYPE_MEAT = 1

PLANT_COLOR = (100, 255, 100)
MEAT_COLOR = (255, 100, 100)

PLANT_ENERGY_MULT = 1
MEAT_ENERGY_MULT = 2.5

class Food():
    def __init__(self, pos: tuple, energy: float = 0, type: int = TYPE_PLANT):
        self.mult = PLANT_ENERGY_MULT if type == TYPE_PLANT else MEAT_ENERGY_MULT
        self.color = PLANT_COLOR if type == TYPE_PLANT else MEAT_COLOR
        self.pos = pos
        self.energy = energy * self.mult
        self.type = type
        self.mass = 0
        self.size = 0
        self.update()
    
    def eat(self, mass: float):
        '''
        Take a bite out of the food, returns the energy consumed
        '''
        e = self.energy
        self.mass = max(0, self.mass - mass)
        self.energy = mass_to_energy(self.mass) * self.mult
        self.update()
        return e

    # used only once
    def energize(self, seed: float):
        random.seed(seed)
        self.energy = (30 + random.random() * 30) * self.mult
        self.update()

    def update(self):
        self.mass = energy_to_mass(self.energy / self.mult)
        self.size = 0.2 + (self.energy / 60) * 10
