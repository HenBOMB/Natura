from enum import Enum
import neat
import pickle

from random import gauss, random, uniform, randint, choice, random
from natura.util import clamp
from neat.six_util import iterkeys
from neat.graphs import creates_cycle

# https://neat-python.readthedocs.io/en/latest/_modules/attributes.html?highlight=mutate_value#

# TODO: Add nature laws, for eg: baby size relative to parent must not be half the parent's size
# basically all creature inputs and food color
# TODO: This is temporary
allowed_inputs      = [-10, -11, -12]

class Genes(Enum):
    ENERGY          = "a"
    '''
    How much energy the creature has at its disposal
    '''

    HEALTH          = "b"
    '''
    How much health the creature has
    '''

    SPEED           = "c"
    '''
    How fast in meters the creature moves per second (m/s)
    '''

    VIEW_RANGE      = "d"
    '''
    How far in meters the creature can detect food or other creatures
    '''

    COLOR           = "e"
    '''
    The creature's skin color in 0-255 range
    '''

    FOV             = "f"
    '''
    The field of view in which the creature can detect food or other creatures
    '''

    HUNGER_BIAS     = "g"
    '''
    The 0-1 ratio in which the creature will start to get hungry\n
    `hungriness = energy / (ENERGY * HUNGER_BIAS) if energy / ENERGY < HUNGER_BIAS else 0`
    '''

    BABY_SIZE       = "h"
    '''
    The 0.2-1 ratio of the creature's baby.\n 
    The egg size will be 1/3 of the parent's size multiplied by this
    '''

    MUTATE_POWER    = "aa"
    '''
    The mutation power\n
    `value = value + random.gauss(0, MUTATE_POWER)`
    '''
    
    MUTATE_RATE     = "ab"
    '''
    Change for a gene to get mutated
    '''

    REPLACE_RATE    = "ac"
    '''
    The chance that a gene gets completely replaced with a new random value
    If `MUTATE_RATE` fails to mutate a gene, then the replace rate will be: `MUTATE_RATE + REPLACE_RATE`
    '''

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
        self.genes[Genes.VIEW_RANGE]    = Gene(3, 6, 0, 10, Gene.TYPE_INT) # 5
        self.genes[Genes.ENERGY]        = Gene(15, 30, type=Gene.TYPE_INT) # 25 
        self.genes[Genes.HEALTH]        = Gene(10, 50, type=Gene.TYPE_INT) #100
        self.genes[Genes.SPEED]         = Gene(0.1, 2, 0) # 1
        self.genes[Genes.FOV]           = Gene(20, 50, 100) # 45
        self.genes[Genes.COLOR]         = Gene((20, 20, 20), (210, 210, 210), 0, 255, Gene.TYPE_TUPLE)
        self.genes[Genes.HUNGER_BIAS]   = Gene(.4, .8, .1, 1) # .5
        self.genes[Genes.BABY_SIZE]     = Gene(.2, 1, .2, 1) # .5

        self.genes[Genes.MUTATE_POWER]  = Gene(.1, .2, .1, 1) # .2
        self.genes[Genes.MUTATE_RATE]   = Gene(.1, .2, .1, 1) # .3
        self.genes[Genes.REPLACE_RATE]  = Gene(.1, .2, .1, 1) # .1

    def configure_crossover(self, genome1, genome2, config):
        super().configure_crossover(genome1, genome2, config)
        for key in self.genes.keys():
            if random() > 0.5:
                self.genes[key] = genome1.genes[key]
            else: 
                self.genes[key] = genome2.genes[key]

    def mutate_genes(self):
        mutate_power    = self.get_value(Genes.MUTATE_POWER)
        mutate_rate     = self.get_value(Genes.MUTATE_RATE)
        replace_rate    = self.get_value(Genes.REPLACE_RATE)

        for key in self.genes.keys():
            if key == Genes.MUTATE_POWER: break
            self.genes[key].mutate(mutate_power, mutate_rate, replace_rate)

    

    def mutate_add_connection(self, config):
        possible_outputs = list(iterkeys(self.nodes))
        out_node = choice(possible_outputs)

        possible_inputs = possible_outputs + allowed_inputs#config.input_keys
        in_node = choice(possible_inputs)

        key = (in_node, out_node)
        if key in self.connections:
            if config.check_structural_mutation_surer():
                self.connections[key].enabled = True
            return

        if in_node in config.output_keys and out_node in config.output_keys:
            return

        if config.feed_forward and creates_cycle(list(iterkeys(self.connections)), key):
            return

        cg = self.create_connection(config, in_node, out_node)
        self.connections[cg.key] = cg

    def get_value(self, key: str): 
        return self.genes[key].value

    def set_value(self, gene: str, value):
        self.genes[gene].value = value

    def set_genes(self, genes: dict):
        self.genes = genes
    
    def save(self, path: str):
        with open(path, 'wb') as f:
            pickle.dump(self.genes, f)
            print(f"Saved {len(self.genes)} genes to {path}")

    def load(self, path: str):
        with open(path, 'rb') as f:
            self.genes = pickle.load(f)
            print(f"Loaded {len(self.genes)} genes from {path}")

