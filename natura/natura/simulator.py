import neat
import natura
import pickle
import gzip
import random

from natura import Creature, Genome
from random import randint
from neat.genes import DefaultConnectionGene, DefaultNodeGene
from itertools import count

DEFAULT_DELTA = 0.04

def eval_genome(genome: Genome, config: neat.Config, width: int, height: int, max_fitness: int):
    tick_count  = 0
    world       = natura.World(width, height)
    creature    = Creature(genome, config, (randint(-world.width, world.width), randint(-world.height, world.height)))

    world.spawn_food(250)

    while True:
        if tick_count / 100 > max_fitness: return tick_count / 100
        world.tick()
        creature.tick(world, DEFAULT_DELTA)
        if creature.health <= 0: return tick_count / 100
        tick_count += 1

class NaturaSimulator():
    '''
    Mimic real evolution with this class\n
    Creatures will pass on their genes through offsprings, only the toughest will survive!
    '''
    def __init__(self, world: natura.World, config: neat.Config):
        self.world              = world
        self.delta              = DEFAULT_DELTA
        self.config             = config
        self.indexer            = count(1)
        self.population         = []
        self.species            = {}
        self.best_genomes       = {}
        self.generation         = 0
        self.generation_start   = 0

    def spawn_species(self, name: str, pos: tuple, radius: int, count: int):
        '''
        Spawn a species at a give position.
        '''

        self.best_genomes[name] = None
        self.species[name] = (pos, radius, count)

    def run(self, tick_function = None, end_gen_function = None, generations: int = None, save_interval: int = 10, save_path: str = './natura-checkpoint-'):
        while True:
            self.spawn_pop()
            tick_count = 0
            
            creature: Creature
            for i, creature in enumerate(self.population):
                creature.tick(self.world, DEFAULT_DELTA, self.population)

                if creature.health <= 0:
                    creature.genome.fitness = tick_count / 100
                    if self.best_genomes[creature.species].fitness < creature.genome.fitness:
                        self.best_genomes[creature.species] = creature.genome
                    self.population.pop(i)

                if tick_function: tick_function(self.population)

                tick_count += 1

            if end_gen_function: end_gen_function(self.generation)

            self.generation += 1
            self.generation_start += 1

            if generations and generations == self.generation_start: 
                break

            if self.generation_start % save_interval == 0:
                self.save(save_path)
    
    def save(self, path):
        filename = f'{path}{self.generation}'
        print("Saving checkpoint to {0}".format(filename))

        with gzip.open(filename, 'w', compresslevel=5) as f:
            data = (self.generation, self.config, self.species, self.best_genomes, random.getstate())
            pickle.dump(data, f, protocol=pickle.HIGHEST_PROTOCOL)

    @staticmethod
    def load(world, path):
        with gzip.open(path) as f:
            generation, config, species, best_genomes, state = pickle.load(f)
            random.setstate(state)
            sim = NaturaSimulator(world, config)
            sim.generation = generation
            sim.species = species
            sim.best_genomes = best_genomes
            return sim

    def spawn_pop(self):
        self.population = []

        for key in self.species:
            pos, radius, count = self.species[key]

            for _ in range(count):
                k = next(self.indexer)
                g = natura.Genome(k)
                g.configure_new(self.config.genome_config)
                if self.best_genomes[key]:
                    g.nodes = self.best_genomes[key].nodes
                    g.connections = self.best_genomes[key].connections
                c = Creature(g, self.config, (randint(pos[0]-radius, pos[0]+radius), randint(pos[1]-radius, pos[1]+radius)))
                c.species = key
                self.population.append(c)
    
class NeatSimulator():
    '''
    This does not mimic real evolution\n
    Tince there is no natural reproduction going on\n
    This does not allow generations to pass on their genes to their offsprings and go maybe extinct or not
    '''
    def __init__(self, world: natura.World):
        self.world              = world
        self.delta              = DEFAULT_DELTA
        self.pop                = None
    
    def run(self, fitness_function, n = None):
        self.pop.run(fitness_function, n)

    def start(self, save_interval = 100, generations: int = None, tick_function = None, end_gen_function = None, network_path: str = None):
        self.tick_function      = tick_function
        self.end_gen_function   = end_gen_function

        if not self.pop:
            config = neat.Config(
                Genome, neat.DefaultReproduction,
                neat.DefaultSpeciesSet, neat.DefaultStagnation,
                "./neat-config"
            )
            self.pop = neat.Population(config)
        else:
            config = self.pop.config

        self.pop.add_reporter(neat.Checkpointer(save_interval, None, './saves/gen-'))
        self.pop.add_reporter(neat.StdOutReporter(True))
        
        if network_path: self.load_network(network_path, config)

        self.pop.run(self.eval_genomes, generations)
    
    def start_parallel(self, save_interval = 100, network_path: str = None):
        if not self.pop:
            config = neat.Config(
                Genome, neat.DefaultReproduction,
                neat.DefaultSpeciesSet, neat.DefaultStagnation,
                "./neat-config"
            )
            self.pop = neat.Population(config)
        else:
            config = self.pop.config

        self.pop.add_reporter(neat.Checkpointer(save_interval, None, './saves/gen-'))
        self.pop.add_reporter(neat.StdOutReporter(True))

        if network_path: self.load_network(network_path, config)

    def load_network(self, path: str, config: neat.Config):
        with open(path, 'rb') as f:
            inputs, hidden, outputs, connections = pickle.load(f)

            genome: Genome
            for genome in self.pop.population:
                self.pop.population[genome].nodes       = {}
                self.pop.population[genome].connections = {}

                for key in outputs + hidden:
                    node = DefaultNodeGene(key)
                    node.init_attributes(config.genome_config)
                    node.mutate(config.genome_config)
                    self.pop.population[genome].nodes[key] = node

                for key in connections:
                    conn = DefaultConnectionGene(key)
                    conn.init_attributes(config.genome_config)
                    conn.mutate(config.genome_config)
                    self.pop.population[genome].connections[key] = conn

    def load_checkpoint(self, path: str):
        self.pop = neat.Checkpointer().restore_checkpoint(path)
    
    def eval_genomes(self, genomes: list, config: neat.Config):
        tick_count  = 0
        population  = []
        best_genome = None
        
        self.world.clear()
        self.world.spawn_food(250)

        for genome_id, genome in genomes:
            genome.fitness = 0
            population.append(Creature(genome, config, (randint(-self.world.width, self.world.width), randint(-self.world.height, self.world.height))))

        while True:
            self.world.tick()

            creature: Creature
            for i, creature in enumerate(population):
                creature.tick(self.world, self.delta, population)
                if creature.health <= 0:
                    creature.genome.fitness = tick_count / 100

                    if not best_genome: best_genome = creature.genome
                    elif best_genome.fitness < creature.genome.fitness: best_genome = creature.genome

                    population.pop(i)
                    if len(population) == 0: 
                        if self.end_gen_function: self.end_gen_function(self.pop.generation, best_genome)
                        return

            tick_count += 1
            if self.tick_function: self.delta = self.tick_function(population) or DEFAULT_DELTA