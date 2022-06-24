from enum import Enum
import neat
import pickle

from random import gauss, random, uniform, randint
from natura.util import clamp

# https://neat-python.readthedocs.io/en/latest/_modules/attributes.html?highlight=mutate_value#

class Genes(Enum):
    ENERGY          = "a"
    HEALTH          = "b"
    SPEED           = "c"
    VIEW_RANGE      = "d"
    COLOR           = "e"
    FOV             = "f"
    HUNGER_BIAS     = "g"
    MUTATE_POWER    = "aa"
    MUTATE_RATE     = "ab"
    REPLACE_RATE    = "ac"

class Gene(object):
    TYPE_FLOAT  = 0
    TYPE_INT    = 1
    TYPE_TUPLE  = 2

    def __init__(self, init_min, init_max, min = 0, max = 99999, type = TYPE_FLOAT):
        self.value = None
        self.min = min
        self.max = max
        self.init_min = init_min
        self.init_max = init_max
        self.type = type
        
        self.init_value()

    def init_value(self):
        if self.type == Gene.TYPE_FLOAT:
            self.value = uniform(self.init_min, self.init_max)
        elif self.type == Gene.TYPE_INT:
            self.value = randint(self.init_min, self.init_max)
        elif self.type == Gene.TYPE_TUPLE:
            self.value = tuple(randint(self.init_min[i], self.init_max[i]) for i in range(len(self.init_min)))
        else:
            raise RuntimeError(f"Unknown gene value type '{type}'")

    def mutate(self, mutate_power: float, mutate_rate: float, replace_rate: float):
        r = random()

        if r < mutate_rate:
            if self.type == Gene.TYPE_FLOAT:
                self.value = clamp(self.value + gauss(0, mutate_power), self.min, self.max)
            elif self.type == Gene.TYPE_INT:
                self.value = clamp(self.value + int(round(gauss(0, mutate_power))), self.min, self.max)
            elif self.type == Gene.TYPE_TUPLE:
                self.value = tuple(
                    clamp(self.value[i] + int(round(gauss(0, mutate_power))), self.min, self.max)
                    for i in range(len(self.value)))

        elif r < replace_rate + mutate_rate:
            self.init_value()

class Genome(neat.DefaultGenome):
    def __init__(self, key, skip = False):
        super().__init__(key)
        self.genes = {}
        if skip: return
        self.genes[Genes.VIEW_RANGE]    = Gene(3, 6, type=Gene.TYPE_INT) # 5
        self.genes[Genes.ENERGY]        = Gene(15, 30, type=Gene.TYPE_INT) # 25 
        self.genes[Genes.HEALTH]        = Gene(10, 50, type=Gene.TYPE_INT) #100
        self.genes[Genes.SPEED]         = Gene(0.1, 2, 0) # 1
        self.genes[Genes.FOV]           = Gene(20, 50, 160) # 45
        self.genes[Genes.COLOR]         = Gene((20, 20, 20), (210, 210, 210), 0, 255, Gene.TYPE_TUPLE)
        self.genes[Genes.HUNGER_BIAS]   = Gene(.4, .8, .1, 1) # .5
        self.genes[Genes.MUTATE_POWER]  = Gene(.1, .3, .1, 1) # .2
        self.genes[Genes.MUTATE_RATE]   = Gene(.1, .3, .1, 1) # .3
        self.genes[Genes.REPLACE_RATE]  = Gene(.1, .2, .1, 1) # .1
    
    def get_gene(self, key: str) -> Gene: 
        return self.genes[key]

    def get_value(self, key: str): 
        return self.genes[key].value

    def set_gene(self, key: str, gene: Gene):
        self.genes[key] = gene

    def mutate(self, config):
        super().mutate(config)

        mutate_power    = self.get_value(Genes.MUTATE_POWER)
        mutate_rate     = self.get_value(Genes.MUTATE_RATE)
        replace_rate    = self.get_value(Genes.REPLACE_RATE)

        for key in self.genes.keys():
            self.genes[key].mutate(mutate_power, mutate_rate, replace_rate)

    def configure_crossover(self, genome1, genome2, config):
        super().configure_crossover(genome1, genome2, config)
        for key in self.genes.keys():
            if random() > 0.5:
                self.genes[key] = genome1.get_gene(key)
            else: 
                self.genes[key] = genome2.get_gene(key)

    def save(self, path: str):
        with open(path, 'wb') as f:
            pickle.dump(self.genes, f)
            print(f"Saved {len(self.genes)} genes to {path}")

    def load(self, path: str):
        with open(path, 'rb') as f:
            self.genes = pickle.load(f)
            print(f"Loaded {len(self.genes)} genes from {path}")

