import pyautogui

from neat.reporting import BaseReporter

pyautogui.FAILSAFE = False

class KeepPCAwake(BaseReporter):
    def end_generation(self, config, population, species_set):
        current_pos = pyautogui.position()
        for i in range(1, 5):
            pyautogui.moveTo(0, i * 10)
        pyautogui.moveTo(current_pos)