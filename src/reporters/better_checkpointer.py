"""Uses `pickle` to save and restore populations (and other aspects of the simulation state)."""
from __future__ import print_function

import gzip
import random
import time
import pickle

from neat.population import Population
from neat.reporting import BaseReporter

class BetterCheckpointer(BaseReporter):
    """
    A reporter class that performs checkpointing using `pickle`
    to save and restore populations (and other aspects of the simulation state).
    """
    def __init__(self, generation_interval=100, time_interval_seconds=300,
                 cp_filename_prefix='neat-checkpoint-', bg_filename_prefix='neat-best-genome-'):
        """
        Saves the current state (at the end of a generation) every ``generation_interval`` generations or
        ``time_interval_seconds``, whichever happens first.

        :param generation_interval: If not None, maximum number of generations between save intervals
        :type generation_interval: int or None
        :param time_interval_seconds: If not None, maximum number of seconds between checkpoint attempts
        :type time_interval_seconds: float or None
        :param str cp_filename_prefix: Prefix for the filename (the end will be the generation number)
        :param str bg_filename_prefix: Prefix for the best genome (the end will be the generation number)
        """
        self.generation_interval = generation_interval
        self.time_interval_seconds = time_interval_seconds
        self.cp_filename_prefix = cp_filename_prefix
        self.bg_filename_prefix = bg_filename_prefix

        self.current_generation = None
        self.last_generation_checkpoint = -1
        self.last_time_checkpoint = time.time()
        self.best_genome = None

    def start_generation(self, generation):
        self.current_generation = generation

    def end_generation(self, config, population, species_set):
        checkpoint_due = False

        if self.time_interval_seconds is not None:
            dt = time.time() - self.last_time_checkpoint
            if dt >= self.time_interval_seconds:
                checkpoint_due = True

        if (checkpoint_due is False) and (self.generation_interval is not None):
            dg = self.current_generation - self.last_generation_checkpoint
            if dg >= self.generation_interval:
                checkpoint_due = True

        if checkpoint_due:
            self.save_checkpoint(config, population, species_set, self.current_generation)
            self.last_generation_checkpoint = self.current_generation
            self.last_time_checkpoint = time.time()

    def save_checkpoint(self, config, population, species_set, generation):
        """ Save the current simulation state. """
        filename = '{0}{1}'.format(self.cp_filename_prefix, generation)
        print("Saving checkpoint to {0}".format(filename))

        with gzip.open(filename, 'w', compresslevel=5) as f:
            data = (generation, config, population, species_set, random.getstate())
            pickle.dump(data, f, protocol=pickle.HIGHEST_PROTOCOL)

        if self.best_genome == None: return
        if self.best_genome.fitness < 100: 
            print("No good genome found, skipping")
            return

        filename = '{0}{1}'.format(self.bg_filename_prefix, generation)
        print("Saving best genome to {0}".format(filename))
        
        with open(filename, 'wb') as f:
            pickle.dump(self.best_genome, f)

    @staticmethod
    def restore_checkpoint(filename):
        """Resumes the simulation from a previous saved point."""
        with gzip.open(filename) as f:
            generation, config, population, species_set, rndstate = pickle.load(f)
            random.setstate(rndstate)
            return Population(config, (population, species_set, generation))
    
    def post_evaluate(self, config, population, species, best_genome):
        self.best_genome = best_genome