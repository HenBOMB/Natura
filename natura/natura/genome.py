from enum import Enum
import neat

from random import gauss, random, uniform, randint, choice, random
from natura.util import clamp
from neat.six_util import iterkeys
from neat.graphs import creates_cycle


class Genes(Enum):
    ENERGY              = "aa"
    '''
    How much energy the creature has at its disposal
    `Value: 0-?`
    '''

    HEALTH              = "ab"
    '''
    How much health the creature has
    `Value: 0-?`
    '''

    SPEED               = "ac"
    '''
    How fast the creature moves per second (m/s)
    `Value: 0m-?m`
    '''

    VIEW_RANGE          = "ad"
    '''
    How far the creature can detect food or other creatures
    `Value: 0-? (meters)`
    '''

    COLOR               = "ae"
    '''
    The creature's skin color in 0-255 range
    `Value: (0-255, 0-255, 0-255)`
    '''

    FOV                 = "af"
    '''
    The field of view in which the creature can detect food or other creatures
    `Value: ?-? (degrees)`
    '''

    HUNGER_BIAS         = "ag"
    '''
    The 0-1 ratio in which the creature will start to get hungry\n
    `hungriness = energy / (ENERGY * HUNGER_BIAS) if energy / ENERGY < HUNGER_BIAS else 0`
    `Value: 0-1`
    '''

    REPRODUCTION_URGE   = "ba"
    '''
    The amount of reproduction urge to add
    `Value: 0.001-1 (seconds)`
    '''

    MATURITY_LENGTH     = "ya"
    '''
    How long till the creature reaches adult
    `Value: 0-max (seconds)`
    '''

    MATURITY_RATE       = "yb"
    '''
    How fast the creature matures from baby to adult
    `Value: 0-max (seconds)`
    ''' 

    BABY_MATURITY_LENGTH= "yc"
    '''
    At what stage does the baby get out of the egg
    `Value: 0-1 (%)`
    '''

    BABY_SIZE           = "bb"
    '''
    How big the baby egg will be
    `Value: 0.001-max (meters)`
    '''

    MUTATE_POWER        = "xa"
    '''
    The mutation power\n
    `value = value + random.gauss(0, MUTATE_POWER)`
    '''
    
    MUTATE_RATE         = "xb"
    '''
    Change for a gene to get mutated
    '''

    REPLACE_RATE        = "xc"
    '''
    The chance that a gene gets completely replaced with a new random value
    If `MUTATE_RATE` fails to mutate a gene, then the replace rate will be: `MUTATE_RATE + REPLACE_RATE`
    '''

class Gene(object):
    TYPE_FLOAT  = 0
    TYPE_INT    = 1
    TYPE_TUPLE  = 2

    def __init__(self, init_min, init_max, min = 0.00001, max = 99999, type = TYPE_FLOAT):
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
        self.genes[Genes.ENERGY]            = Gene(15, 30, type=Gene.TYPE_INT) 
        self.genes[Genes.HEALTH]            = Gene(10, 50, type=Gene.TYPE_INT)
        self.genes[Genes.SPEED]             = Gene(2, 4, 0)
        self.genes[Genes.FOV]               = Gene(20, 50, 100, type=Gene.TYPE_INT)
        self.genes[Genes.VIEW_RANGE]        = Gene(500, 1000, type=Gene.TYPE_INT)
        self.genes[Genes.COLOR]             = Gene((20, 20, 20), (210, 210, 210), 0, 255, Gene.TYPE_TUPLE)
        self.genes[Genes.HUNGER_BIAS]       = Gene(.4,  .8,   .1, 1)
        self.genes[Genes.REPRODUCTION_URGE] = Gene(.1,   1,    0, 2)
        self.genes[Genes.MATURITY_LENGTH]   = Gene(3, 5)
        self.genes[Genes.MATURITY_RATE]     = Gene(1, 2)
        self.genes[Genes.BABY_SIZE]         = Gene(.4, .7, .001)
        self.genes[Genes.BABY_MATURITY_LENGTH] = Gene(.2, .6, max=1)

        self.genes[Genes.MUTATE_POWER]      = Gene(.1, .2, .1, 1)
        self.genes[Genes.MUTATE_RATE]       = Gene(.1, .2, .1, 1)
        self.genes[Genes.REPLACE_RATE]      = Gene(.1, .2, .1, 1)

        # NOTE: Careful with this

        self.set_value(Genes.ENERGY, 20)
        self.set_value(Genes.HEALTH, 30)
        self.set_value(Genes.SPEED, 6)
        self.set_value(Genes.FOV, 45)
        self.set_value(Genes.VIEW_RANGE, 200)
        self.set_value(Genes.HUNGER_BIAS, .6)
        self.set_value(Genes.REPRODUCTION_URGE, 0)
        self.set_value(Genes.MATURITY_LENGTH, 4)
        self.set_value(Genes.MATURITY_RATE, 1)
        self.set_value(Genes.BABY_SIZE, .5)
        self.set_value(Genes.BABY_MATURITY_LENGTH, .5)

    # def configure_crossover(self, genome1, genome2, config):
    #     super().configure_crossover(genome1, genome2, config)
    #     for key in self.genes.keys():
    #         if random() > 0.5:
    #             self.genes[key] = genome1.genes[key]
    #         else: 
    #             self.genes[key] = genome2.genes[key]

    def mutate_genes(self):
        pass
        # mutate_power    = self.get_value(Genes.MUTATE_POWER)
        # mutate_rate     = self.get_value(Genes.MUTATE_RATE)
        # replace_rate    = self.get_value(Genes.REPLACE_RATE)

        # for key in self.genes.keys():
        #     if key == Genes.MUTATE_POWER: break
        #     self.genes[key].mutate(mutate_power, mutate_rate, replace_rate)

    def get_value(self, key: str) -> float | int | tuple: 
        return self.genes[key].value

    def set_value(self, gene: str, value):
        self.genes[gene].value = value

    def set_genes(self, genes: dict):
        self.genes = genes
