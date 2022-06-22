import sys
sys.path.insert(0, 'C:/Users/alani/OneDrive/Desktop/Coding/Stella/tools')

import neat
import pickle
import re
import time

from genes import *
from creature import *

def eval_genome(genome, config, generation):
    creature = Creature(genome, Genes(87374), neat.nn.FeedForwardNetwork.create(genome, config), WORLD_WIDTH/2, WORLD_HEIGHT/2)
    world = World(generation)
    world.spawn_food(100)

    delta = 0.05
    runs = 0
    valid = False

    while True:
        if len(world.food) == 0:
            return runs / 10

        old_energy = creature.energy
        creature.tick(world, delta)
        
        if old_energy < creature.energy: valid = True

        if creature.health <= 0: 
            if valid:
                return runs / 10
            else:
                return 0

        runs += 1

def run(path, generations, save_interval):
    # local_dir = os.path.dirname(__file__)
    # config_path = os.path.join(local_dir, 'config')

    config = neat.Config(
        neat.DefaultGenome, neat.DefaultReproduction,
        neat.DefaultSpeciesSet, neat.DefaultStagnation,
        "./config"
    )

    cp = neat.Checkpointer(save_interval, None, "./checkpoints/neat-checkpoint-")
    
    if path != None:
        pop = cp.restore_checkpoint(path)
    else:
        pop = neat.Population(config)

    pop.add_reporter(cp)
    pop.add_reporter(neat.StdOutReporter(True))
    pop.add_reporter(neat.StatisticsReporter())
    
    # Blazing fast!
    pe = neat.ParallelEvaluator(4, eval_genome, pop)

    print(f"****** Running {generations}/{save_interval} generations ******")
    time.sleep(2)

    winner = pop.run(pe.evaluate, generations + 1)

    with open('best-genome', 'wb') as f:
        pickle.dump(winner, f)

    print('\nBest genome:\n{!s}'.format(winner))

if __name__ == '__main__':
    def get_arg(name, default):
        for i in range(1, len(sys.argv)-1):
            m = re.findall("(?<=--)\w+", sys.argv[i])
            if len(m) == 1 and m[0] == name:
                return sys.argv[i+1]
        return default

    run(
        get_arg("path", None), 
        int(get_arg("gen", 100)), 
        int(get_arg("interval", int(get_arg("gen", 100)) // 4))
    )
