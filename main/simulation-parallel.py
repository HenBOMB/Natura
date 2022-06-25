import natura
import neat

from natura.simulator import eval_genome as ev

world = natura.World(1500, 1500)

def eval_genome(genome, config):
    return ev(genome, config, world.width, world.height)

if __name__ == '__main__':
    import argutil
    import multiprocessing

    if argutil.has_arg("help"):
        print("Load the simulation from a checkpoint")
        print("--cp [path]")
        print("Maximum number of generations between save intervals")
        print("--int [int]")
        import sys
        sys.exit()


    simulator       = natura.Simulator(world)
    checkpoint      = argutil.get_arg("cp", None)
    interval        = argutil.get_arg("int", 50)
    workers         = argutil.get_arg("work", multiprocessing.cpu_count())

    if checkpoint:
        simulator.load_checkpoint(checkpoint)

    simulator.start_parallel(interval)

    pe = neat.ParallelEvaluator(workers, eval_genome)
    
    simulator.pop.run(pe.evaluate)