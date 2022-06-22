import sys
sys.path.insert(0, 'C:/Users/alani/OneDrive/Desktop/Coding/Stella/tools')

if __name__ != '__main__':
    raise ImportError("Cannot import module 'display.py'")

import re
import pygame
import neat
import pickle

pygame.init()
pygame.font.init()

from nndraw import NN
from genes import *
from creature import *

SCREEN_WIDTH = 800#1600
SCREEN_HEIGHT = 800
SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
FONT = pygame.font.Font('freesansbold.ttf', 20)
CLOCK = pygame.time.Clock()
SEED = random.randint(0, 10000)
FPS = 60

WORLD = World(SEED, SCREEN_WIDTH, SCREEN_HEIGHT)

dragging = False

def display_genomes(GENOME, CONFIG, COUNT = 1):
    global dragging
    creatures = []
    
    for _ in range(COUNT):
        c = Creature(GENOME, Genes(random.randint(0, 10000)), neat.nn.FeedForwardNetwork.create(GENOME, CONFIG), rand_negpos(random.random())*500, rand_negpos(random.random())*500)
        creatures.append(c)

    nndraw = NN(CONFIG, GENOME, (50, SCREEN_HEIGHT/2), SCREEN_HEIGHT)
    
    delta = 1. / 60.

    while True:
        if CLOCK.get_fps() != 0: delta = 1. / CLOCK.get_fps()
            
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                dragging = True
                WORLD.set_click(pygame.mouse.get_pos())

            if event.type == pygame.MOUSEBUTTONUP:
                dragging = False

            if event.type == pygame.MOUSEMOTION and dragging:
                WORLD.pan_camera(pygame.mouse.get_pos())

        SCREEN.fill((0, 0, 0))

        pygame.draw.rect(SCREEN, (200, 200, 200), (
            -WORLD_WIDTH + WORLD.offset_x, 
            -WORLD_HEIGHT + WORLD.offset_y, 
            WORLD_WIDTH*2,  
            WORLD_HEIGHT*2))

        pygame.draw.rect(SCREEN, (50, 50, 50), (
            -WORLD_WIDTH + WORLD.offset_x-5, 
            -WORLD_HEIGHT + WORLD.offset_y-5, 
            WORLD_WIDTH*2+5,  
            WORLD_HEIGHT*2+5), 5)

        WORLD.tick()
        WORLD.draw(SCREEN, pygame)

        if len(WORLD.food) == 0:
            WORLD.seed = random.randint(0, 10000)
            WORLD.spawn_food(50)

        for i, creature in enumerate(creatures):
            inputs, out = creature.tick(WORLD, delta)

            if creature.health <= 0: continue

            creature.draw(SCREEN, WORLD, pygame)

            if i != 0: continue

            creature.genes.set(Genes.COLOR, (150, 150, 255))

            nndraw.update_inputs([
                f"{inputs[0]}%",
                f"{inputs[1]}%",
                f"{inputs[2]}%m/s",
                f"{inputs[3]}",
                f"{round(math.degrees(inputs[4]))}deg",
                f"{round(inputs[5])}px",
                f"{inputs[6]}"
            ])

            nndraw.update_outputs([
                f"{out[0]>.5}",
                f"{out[1]>.5}",
                f"{out[2]>.5}",
                f"{out[3]>.5}",
                f"{out[4]>.5}",
                f"{out[5]>.5}"
            ])

            nndraw.draw(SCREEN)

        CLOCK.tick(FPS)
        pygame.display.update()

def run():
    def get_arg(name, default):
        for i in range(1, len(sys.argv)-1):
            m = re.findall("(?<=--)\w+", sys.argv[i])
            if len(m) == 1 and m[0] == name:
                return sys.argv[i+1]
        return default

    path = get_arg("path", "best-genome")
    config = get_arg("config", "config")

    config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction, neat.DefaultSpeciesSet, neat.DefaultStagnation, config)
    
    with open(path, 'rb') as f:
        display_genomes(pickle.load(f), config, int(get_arg("count", 1)))

run()