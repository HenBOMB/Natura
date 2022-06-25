import neat
import natura
import pickle

from natura import Creature
from random import randint
from neat.genes import DefaultConnectionGene, DefaultNodeGene

def eval_genome(genome: natura.Genome, config: neat.Config, width, height):
    tick_count  = 0
    world       = natura.World(width, height)
    creature    = Creature(genome, config, (randint(-world.width, world.width), randint(-world.height, world.height)))

    world.spawn_food(250)

    while True:
        if tick_count / 100 > 100: return tick_count / 100
        world.tick()
        creature.tick(world, 0.04)
        if creature.health <= 0: return tick_count / 100
        tick_count += 1

class Simulator():
    def __init__(self, world: natura.World):
        self.world              = world
        self.delta              = 0.04
        self.pop                = None
    
    def start(self, save_interval = 100, generations: int = None, tick_function = None, end_gen_function = None, network_path: str = None):
        self.tick_function      = tick_function
        self.end_gen_function   = end_gen_function

        if not self.pop:
            config = neat.Config(
                natura.Genome, neat.DefaultReproduction,
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
                natura.Genome, neat.DefaultReproduction,
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

            genome: natura.Genome
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
            if self.tick_function: self.delta = self.tick_function(population) or 0.04