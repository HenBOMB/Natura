import natura
import neat

from natura.simulator import eval_genome as ev

world = natura.World(1500, 1500)

def eval_genome(genome, config):
    return ev(genome, config, world.width, world.height, 300)

if __name__ == '__main__':
    import argutil
    import multiprocessing

    if argutil.has_arg("help"):
        print("Load the simulation from a checkpoint, default is None")
        print("--c [path]")
        print("Maximum number of generations between save intervals, default is 50")
        print("default is 50")
        print("--i [int]")
        print("The number of cpu workers to use, default is multiprocessing.cpu_count()")
        print("--w [int]")
        import sys
        sys.exit()

    simulator       = natura.NeatSimulator(world)
    checkpoint      = argutil.get_arg("c", None)
    interval        = int(argutil.get_arg("i", 100))
    workers         = int(argutil.get_arg("w", multiprocessing.cpu_count()))

    if checkpoint:
        simulator.load_checkpoint(checkpoint)

    simulator.start_parallel(interval)

    pe = neat.ParallelEvaluator(workers, eval_genome)
    
    simulator.run(pe.evaluate)