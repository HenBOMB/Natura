import pickle
import pyautogui
import neat
from neat.reporting import BaseReporter

pyautogui.FAILSAFE = False

class Checkpointer(neat.Checkpointer):
    def __init__(self, generation_interval=100, time_interval_seconds=300,
                 cp_filename_prefix='neat-checkpoint-', bg_filename_prefix='neat-best-genome-'):
        super().__init__(generation_interval, time_interval_seconds, cp_filename_prefix)
        self.bg_filename_prefix = bg_filename_prefix

    def save_checkpoint(self, config, population, species_set, generation):
        super().save_checkpoint(config, population, species_set, generation)

        filename = '{0}{1}'.format(self.bg_filename_prefix, generation)
        print("Saving best genome to {0}".format(filename))
        
        with open(filename, 'wb') as f:
            pickle.dump(self.best_genome, f)

    def post_evaluate(self, config, population, species, best_genome):
        super().post_evaluate(config, population, species, best_genome)
        self.best_genome = best_genome

class KeepPCAwake(BaseReporter):
    def end_generation(self, config, population, species_set):
        current_pos = pyautogui.position()
        for i in range(1, 5):
            pyautogui.moveTo(0, i * 10)
        pyautogui.moveTo(current_pos)