import neat
import natura
import pickle
import gzip
import random

from natura import Creature, Genome, Genes
from random import randint
from neat.genes import DefaultConnectionGene, DefaultNodeGene
from itertools import count

DEFAULT_DELTA = 0.04

def eval_genome(genome: Genome, config: neat.Config, width: int, height: int, max_fitness: int):
    tick_count  = 0
    world       = natura.World(width, height)
    creature    = Creature(genome, config, (0, 0), world)

    world.spawn_food(250)

    while True:
        if creature.food_eaten > 20: return 20
        world.tick()
        creature.tick(DEFAULT_DELTA)
        if creature.dead: return 0 if creature.food_eaten < 2 else creature.food_eaten
        tick_count += 1

class NaturaSimulator():
    '''
    Mimic real evolution with this class\n
    Creatures will pass on their genes through offsprings, only the toughest will survive!
    '''
    def __init__(self, world: natura.World):
        self.world              = world
        self.delta              = DEFAULT_DELTA
        self.indexer            = count(1)
        self.population         = []
        self.species            = {}
        self.best_genomes       = {}
        self.generation         = 1
        self.generation_start   = 1

    def spawn_species(self, name: str, pos: tuple, radius: int, count: int, color: tuple = None):
        '''
        Spawn a species at a give position.
        '''
        self.best_genomes[name] = None
        genome = Genome(0)
        if color: genome.set_value(Genes.COLOR, color)
        self.species[name] = (pos, radius, count, genome.genes)

    def init(self, config: neat.Config):
        self.config = config

    def run(self, tick_function = None, end_gen_function = None, max_generations: int = None, save_interval: int = 10, save_path: str = './natura-checkpoint-'):
        while True:
            self.start_generation(tick_function)
            self.end_generation(end_gen_function)
            
            if self.generation_start % save_interval == 0:
                self.save(save_path)

            if max_generations and max_generations >= self.generation: break
    
    def start_generation(self, func):
        self.spawn_population()
        self.world.clear()
        self.world.spawn_food(250)

        tick_count = 0

        while True:
            self.world.tick()

            creature: Creature
            for i, creature in enumerate(self.population):
                if creature.food_eaten > 20: creature.dead = True
                creature.tick(DEFAULT_DELTA, self.population)

                if not creature.dead: continue

                creature.genome.fitness = 0 if creature.food_eaten < 2 else creature.food_eaten

                if not self.best_genomes[creature.species]: 
                    self.best_genomes[creature.species] = creature.genome

                if self.best_genomes[creature.species].fitness < creature.genome.fitness:
                    self.best_genomes[creature.species] = creature.genome

                self.population.pop(i)

                if len(self.population) == 0: return

            if func: func(self.population)

            tick_count += 1
    
    def end_generation(self, func):
        self.generation += 1
        self.generation_start += 1
        if func: func(self.generation)
        
    def save(self, path):
        filename = f'{path}{self.generation}'
        print("Saving checkpoint to {0}".format(filename))

        with gzip.open(filename, 'w', compresslevel=5) as f:
            data = (self.generation, self.config, self.species, self.best_genomes, random.getstate())
            pickle.dump(data, f, protocol=pickle.HIGHEST_PROTOCOL)

    def load(self, path):
        if not path: return
        with gzip.open(path) as f:
            generation, config, species, best_genomes, state = pickle.load(f)
            random.setstate(state)
            self.config       = config
            self.generation   = generation
            self.species      = species
            self.best_genomes = best_genomes

    def spawn_population(self):
        self.population = []

        for key in self.species:
            pos, radius, count, genes = self.species[key]

            for _ in range(count):
                k = next(self.indexer)
    
                genome = natura.Genome(k, True)
                genome.configure_new(self.config.genome_config)
                if self.best_genomes[key]:
                    genome.nodes = self.best_genomes[key].nodes
                    genome.connections = self.best_genomes[key].connections
                genome.mutate(self.config.genome_config)
                genome.set_genes(genes)

                c = Creature(genome, self.config, 
                    (randint(pos[0]-radius, pos[0]+radius), randint(pos[1]-radius, pos[1]+radius)), self.world)

                c.species = key
                self.population.append(c)

class NaturaNeatSimulator():
   
    def __init__(self, world: natura.World):
        self.world              = world
        self.delta              = DEFAULT_DELTA
        self.pop                = None
    
    def run(self, save_interval = 100, generations: int = None, tick_function = None, end_gen_function = None, network_path: str = None):
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
        valid       = []
        best_genome = None
        
        self.world.clear()
        self.world.spawn_food(250)

        for genome_id, genome in genomes:
            genome.fitness = 0
            population.append(Creature(genome, config, 
                (randint(-self.world.width, self.world.width), randint(-self.world.height, self.world.height)), self.world))

        while True:
            self.world.tick()

            creature: Creature
            for i, creature in enumerate(population):
                l = len(population)
                creature.tick(self.delta, population)
                _l = len(population)
                if l != _l: genomes.append(population[_l-1].genome)

                if creature.food_eaten > 20: creature.dead = True
                if creature.dead:
                    creature.genome.fitness = 0 if creature.food_eaten < 2 else creature.food_eaten

                    if not best_genome: best_genome = creature.genome
                    elif best_genome.fitness < creature.genome.fitness: best_genome = creature.genome

                    population.pop(i)
                    if l - 1 == 0: 
                        if self.end_gen_function: self.end_gen_function(self.pop.generation)
                        return

            tick_count += 1
            if self.tick_function: self.delta = self.tick_function(population) or DEFAULT_DELTA
            
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
            population.append(Creature(genome, config, 
                (randint(-self.world.width, self.world.width), randint(-self.world.height, self.world.height)), self.world))

        while True:
            self.world.tick()

            for i, creature in enumerate(population):
                if creature.food_eaten > 20: creature.dead = True
                creature.tick(self.delta, population)
                if creature.dead:
                    creature.genome.fitness = 0 if creature.food_eaten < 2 else creature.food_eaten

                    if not best_genome: best_genome = creature.genome
                    elif best_genome.fitness < creature.genome.fitness: best_genome = creature.genome

                    population.pop(i)
                    if len(population) == 0: 
                        if self.end_gen_function: self.end_gen_function(self.pop.generation, best_genome)
                        return

            tick_count += 1
            if self.tick_function: self.delta = self.tick_function(population) or DEFAULT_DELTA
