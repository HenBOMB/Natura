import sys
from turtle import distance
sys.path.insert(0, './src')
sys.path.insert(1, './src/tools')

if __name__ != '__main__':
    raise ImportError("Cannot import module 'display.py'")

import re
import pygame
import neat
import pickle
import tools

pygame.init()
pygame.font.init()

pygame.display.set_caption("Simbiol - Simulated Biological Life")

from nndraw import NN
from genes import *
from creature import *
from camera import *

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 800
CAMERA = Camera(SCREEN_WIDTH, SCREEN_HEIGHT)
SEED = random.randint(0, 10000)
FPS = 60
WORLD = World(SEED)
SHOW_NN = False
SHOW_NN_CREATURE_I = 0

dragging = False

WORLD.image_food = pygame.image.load('./assets/food.png', 'food')

PROPERTIES_FONT = pygame.font.SysFont("comicsans", 15)

def draw_properties(creature: Creature):
    width, height = (200, 100)
    surf = pygame.Surface((width, height), pygame.SRCALPHA)
    surf.fill((100, 100, 100, 100))
    CAMERA.screen.blit(surf, (SCREEN_WIDTH - width, 0))

    text = PROPERTIES_FONT.render("uwu", True, (0,0,0))

    CAMERA.screen.blit(text, (SCREEN_WIDTH - width, -7.5))

def display_genomes(GENOME: neat.DefaultGenome, CONFIG: neat.Config, COUNT: int = 1):
    global dragging, SHOW_NN_CREATURE_I, SHOW_NN

    creatures = []
    
    for _ in range(COUNT):
        c = Creature(GENOME, Genes(random.randint(0, 10000)), neat.nn.FeedForwardNetwork.create(GENOME, CONFIG), rand_negpos(random.random())*500, rand_negpos(random.random())*500)
        creatures.append(c)

    nndraw = NN(CONFIG, GENOME, (50, SCREEN_HEIGHT/2), SCREEN_HEIGHT)
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            elif event.type == pygame.MOUSEWHEEL:
                CAMERA.zoom(-event.y)

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                dragging = True
                CAMERA.set_pos(pygame.mouse.get_pos())

            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                dragging = False
                creature: Creature

                for i, creature in enumerate(creatures):
                    d = tools.dist(CAMERA.fix_pos(creature.pos), pygame.mouse.get_pos())
                    if d < CAMERA.fix_scale(creature.size_px):
                        SHOW_NN_CREATURE_I = i
                        break

            elif event.type == pygame.MOUSEMOTION and dragging:
                if tools.dist(CAMERA.cam_pos, pygame.mouse.get_pos()) > 5:
                    CAMERA.pan_camera(pygame.mouse.get_pos())

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_n:
                    SHOW_NN = not SHOW_NN

            elif event.type == pygame.K_UP:
                SHOW_NN_CREATURE_I += 1
                if SHOW_NN_CREATURE_I == len(creatures): SHOW_NN_CREATURE_I = 0

            elif event.type == pygame.K_DOWN:
                SHOW_NN_CREATURE_I -= 1
                if SHOW_NN_CREATURE_I < 0: SHOW_NN_CREATURE_I = len(creatures) - 1

        CAMERA.clear_screen()

        CAMERA.draw_rect((200, 200, 200), (-WORLD_WIDTH, -WORLD_HEIGHT, WORLD_WIDTH*2, WORLD_HEIGHT*2))
        CAMERA.draw_rect((50, 50, 50), (-WORLD_WIDTH-5, -WORLD_HEIGHT-5, WORLD_WIDTH*2+10, WORLD_HEIGHT*2+10), 5)

        WORLD.tick()
        WORLD.draw(CAMERA)

        if len(WORLD.food) == 0:
            WORLD.seed = random.randint(0, 10000)
            WORLD.spawn_food(50)

        creature: Creature
        for i, creature in enumerate(creatures):
            inputs, out = creature.tick(WORLD, CAMERA.delta)

            if creature.health <= 0: continue

            if i != SHOW_NN_CREATURE_I:
                creature.draw(CAMERA)
                continue

            col = creature.genes.get(Genes.COLOR)
            creature.genes.set(Genes.COLOR, (150, 150, 255))
            creature.draw(CAMERA)
            creature.genes.set(Genes.COLOR, col)

            if SHOW_NN:
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

                nndraw.draw(CAMERA.screen)

                draw_properties(creature)

        CAMERA.tick()

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