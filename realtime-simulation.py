import sys

from population import Population
sys.path.insert(0, './src')
sys.path.insert(1, './src/tools')

if __name__ != '__main__':
    raise ImportError(f"Cannot import module '{__file__}'")

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
from creature import Creature
from camera import Camera
from world import *
from population import Population

PROPERTIES_FONT = pygame.font.SysFont("comicsans", 15)
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 800
CAMERA = Camera(SCREEN_WIDTH, SCREEN_HEIGHT)
FPS = 60
WORLD = World()
SHOW_NN = False
SHOW_STATS = False
SHOW_NN_CREATURE_I = 0

dragging = False
WORLD.image_food = pygame.image.load('./assets/food.png', 'food')

def draw_properties(creature: Creature):
    width, height = (300, 100)
    surf = pygame.Surface((width, height), pygame.SRCALPHA)
    surf.fill((100, 100, 100, 100))
    CAMERA.screen.blit(surf, (SCREEN_WIDTH - width, 0))

    def draw_txt(txt, i):
        text = PROPERTIES_FONT.render(str(txt), True, (0,0,0))
        CAMERA.screen.blit(text, (SCREEN_WIDTH - width, 7.5 * 2 * i))

    def draw_v_txt(txt, i):
        text = PROPERTIES_FONT.render(str(txt), True, (0,0,0))
        CAMERA.screen.blit(text, (SCREEN_WIDTH - width + 80, 7.5 * 2 * i))

    draw_txt("Fov", 0)
    draw_v_txt(creature.GENE_FOV, 0)
    draw_txt("Energy", 1)
    draw_v_txt(f"{tools.percent(creature.energy, creature.GENE_ENERGY)}% / {creature.GENE_ENERGY}", 1)
    draw_txt("Health", 2)
    draw_v_txt(f"{tools.percent(creature.health, creature.GENE_HEALTH)}% / {creature.GENE_HEALTH}", 2)
    draw_txt("Speed", 3)
    draw_v_txt(creature.GENE_SPEED, 3)
    draw_txt("View Range", 4)
    draw_v_txt(creature.GENE_SIGHT_RANGE, 4)
    draw_txt("Hunger", 5)
    draw_v_txt(creature.GENE_HUNGER, 5)

def run(pop: Population):
    global dragging, SHOW_NN_CREATURE_I, SHOW_NN, SHOW_STATS
    
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

                for i, creature in enumerate(pop.population):
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
                elif event.key == pygame.K_s:
                    SHOW_STATS = not SHOW_STATS

            elif event.type == pygame.K_UP:
                SHOW_NN_CREATURE_I += 1
                if SHOW_NN_CREATURE_I == len(pop.population): SHOW_NN_CREATURE_I = 0

            elif event.type == pygame.K_DOWN:
                SHOW_NN_CREATURE_I -= 1
                if SHOW_NN_CREATURE_I < 0: SHOW_NN_CREATURE_I = len(pop.population) - 1

        CAMERA.clear_screen()

        CAMERA.draw_rect((0, 0, 16), (-WORLD_WIDTH, -WORLD_HEIGHT, WORLD_WIDTH*2, WORLD_HEIGHT*2))
        CAMERA.draw_rect((50, 50, 50), (-WORLD_WIDTH-5, -WORLD_HEIGHT-5, WORLD_WIDTH*2+10, WORLD_HEIGHT*2+10), 5)

        WORLD.tick()
        WORLD.draw(CAMERA)

        if len(WORLD.food) == 0:
            WORLD.seed = random.randint(0, 10000)
            WORLD.spawn_food(50)

        creature: Creature
        for i, creature in enumerate(pop.population):
            inputs, out = creature.tick(WORLD, CAMERA.delta, pop)

            if creature.health <= 0: 
                pop.population.pop(i)
                continue

            if i != SHOW_NN_CREATURE_I:
                creature.draw(CAMERA, False)
                continue

            creature.draw(CAMERA, True)

            # if SHOW_NN:
            #     nndraw = NN(config, genome, (50, SCREEN_HEIGHT/2), SCREEN_HEIGHT)
            #     nndraw.update_inputs([
            #         f"{inputs[0]}%",
            #         f"{inputs[1]}%",
            #         f"{inputs[2]}%",
            #         f"{inputs[3]}%",
            #         f"{inputs[4]}%",
            #         f"{inputs[5]}"
            #     ])

            #     nndraw.update_outputs([
            #         f"{out[0]>.5}",
            #         f"{out[1]>.5}",
            #         f"{out[2]>.5}",
            #         f"{out[3]>.5}",
            #         f"{out[4]>.5}",
            #         f"{out[5]>.5}"
            #     ])

            #     nndraw.draw(CAMERA.screen)

            if SHOW_STATS:
                draw_properties(creature)

        CAMERA.tick()