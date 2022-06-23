import sys
sys.path.insert(0, './src')
sys.path.insert(1, './src/tools')
sys.path.insert(1, './src/reporters')

import neat
import pickle
import re
import time
from genes import *
from creature import *
from better_checkpointer import BetterCheckpointer

def eval_genome(genome, config, generation):
    creature = Creature(genome, neat.nn.FeedForwardNetwork.create(genome, config), (WORLD_WIDTH/2, WORLD_HEIGHT/2), Genes(87374))
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

    cp = BetterCheckpointer(save_interval, None, "./neat-data/checkpoint-", "./neat-data/genome-")

    if path != None:
        pop = cp.restore_checkpoint(path)
    else:
        pop = neat.Population(config)

    pop.add_reporter(cp)
    pop.add_reporter(neat.StdOutReporter(True))
    pop.add_reporter(neat.StatisticsReporter())
    # pop.add_reporter(KeepPCAwake())
    
    # Blazing fast!
    pe = neat.ParallelEvaluator(4, eval_genome, pop)

    print(f"****** Running {generations}/{save_interval} generations ******")
    time.sleep(2)

    winner = pop.run(pe.evaluate, generations + 1)

    with open('./latest-genome', 'wb') as f:
        pickle.dump(winner, f)

# python .\evolve-parallel.py --gen 800 --int 10 --cp .\neat-data\checkpoint-299

if __name__ == '__main__':
    def get_arg(name, default):
        for i in range(1, len(sys.argv)-1):
            m = re.findall("(?<=--)\w+", sys.argv[i])
            if len(m) == 1 and m[0] == name:
                return sys.argv[i+1]
        return default

    run(
        get_arg("cp", None), 
        int(get_arg("gen", 100)), 
        int(get_arg("int", int(get_arg("gen", 100)) // 4))
    )
