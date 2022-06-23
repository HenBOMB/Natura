if __name__ != '__main__':
    raise ImportError(f"Cannot import module '{__file__}'")

from fileinput import filename
import sys
import neat
import pygame
import pickle
import time

pygame.init()
pygame.font.init()
pygame.display.set_caption("Natura - Life Evolution")

from natura import Creature, World, util, Genome
from neat.reporting import ReporterSet
from nndraw import NN
from camera import Camera
from random import randint, uniform, getstate
from math   import radians, sin, cos

SCREEN_WIDTH        = 800
SCREEN_HEIGHT       = 800
WORLD_WIDTH         = 1000
WORLD_HEIGHT        = 1000
FPS                 = 60

PROPERTIES_FONT     = pygame.font.SysFont("comicsans", 15)
WORLD               = World(WORLD_WIDTH, WORLD_HEIGHT)
CAMERA              = Camera(SCREEN_WIDTH, SCREEN_HEIGHT)
IMAGE_FOOD          = pygame.image.load('./assets/food.png', 'food')

DRAW_NETWORK        = False
DRAW_STATS          = False

COLOR_BACKGROUND    = (0, 0, 16)
COLOR_HIGHLIGHT     = (COLOR_BACKGROUND[0], COLOR_BACKGROUND[1], COLOR_BACKGROUND[2] * 4)

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
    draw_v_txt(f"{util.percent(creature.energy, creature.GENE_ENERGY)}% / {creature.GENE_ENERGY}", 1)
    draw_txt("Health", 2)
    draw_v_txt(f"{util.percent(creature.health, creature.GENE_HEALTH)}% / {creature.GENE_HEALTH}", 2)
    draw_txt("Speed", 3)
    draw_v_txt(creature.GENE_SPEED, 3)
    draw_txt("View Range", 4)
    draw_v_txt(creature.GENE_VIEW_RANGE, 4)
    draw_txt("Hunger", 5)
    draw_v_txt(creature.GENE_HUNGER, 5)

def draw_creature(c: Creature, camera: Camera, highlight: bool = False):
    camera.draw_circle(c.GENE_COLOR, c.pos, c.size_px)
    rad = radians(c.GENE_FOV/1.5)
    camera.draw_circle((0,0,0), (
            c.pos[0] + cos(c.angle-rad) * c.size_px, 
            c.pos[1] + sin(c.angle-rad) * c.size_px), c.size_px / 4)
    camera.draw_circle((0,0,0), (
            c.pos[0] + cos(c.angle+rad) * c.size_px, 
            c.pos[1] + sin(c.angle+rad) * c.size_px), c.size_px / 4)

    if highlight:
        camera.draw_circle((200, 200, 200), c.pos, c.size_px+5, 1)

def eval_genomes(_genomes: list, config: neat.Config):
    global DRAW_NETWORK, DRAW_STATS

    population  = []
    genomes     = []
    time_start  = time.time()
    dragging    = False

    for genome_id, genome in _genomes:
        genome.fitness = 0
        genomes.append(genome)
        population.append(Creature(genome, config, (uniform(-WORLD_WIDTH, WORLD_WIDTH), uniform(-WORLD_HEIGHT, WORLD_HEIGHT))))

    creature_index = randint(0, len(population)-1)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
                pass
            
            elif event.type == pygame.MOUSEWHEEL:
                CAMERA.zoom(-event.y)

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                dragging = True
                CAMERA.set_pos(pygame.mouse.get_pos())

            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                dragging = False
                creature: Creature

                for i, creature in enumerate(population):
                    d = util.dist(CAMERA.fix_pos(creature.pos), pygame.mouse.get_pos())
                    if d < CAMERA.fix_scale(creature.size_px):
                        creature_index = i
                        break

            elif event.type == pygame.MOUSEMOTION and dragging:
                if util.dist(CAMERA.cam_pos, pygame.mouse.get_pos()) > 5:
                    CAMERA.pan_camera(pygame.mouse.get_pos())

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_n:
                    DRAW_NETWORK = not DRAW_NETWORK
                elif event.key == pygame.K_s:
                    DRAW_STATS = not DRAW_STATS

            elif event.type == pygame.K_UP:
                creature_index += 1
                if creature_index == len(population): creature_index = 0

            elif event.type == pygame.K_DOWN:
                creature_index -= 1
                if creature_index < 0: creature_index = len(population) - 1

        CAMERA.clear_screen()
        CAMERA.draw_rect(COLOR_BACKGROUND, (-WORLD_WIDTH, -WORLD_HEIGHT, WORLD_WIDTH*2, WORLD_HEIGHT*2))

        WORLD.tick()

        for i, food in enumerate(WORLD.food):
            if food.energy == 0:
                WORLD.food.pop(i)
                continue
            CAMERA.draw_image(IMAGE_FOOD, (food.pos[0] - food.size / 2, food.pos[1] - food.size / 2), food.size * 2.5)

        if len(WORLD.food) == 0:
            WORLD.seed = randint(0, 10000)
            WORLD.spawn_food(50)

        creature: Creature
        for i, creature in enumerate(population):
            inputs, out = creature.tick(WORLD, CAMERA.delta, population)

            if creature.health <= 0: 
                population[i].fitness = time.time() - time_start
                population.pop(i)
                if len(population) == 0:
                    break
                continue

            if i != creature_index:
                draw_creature(creature, CAMERA)
                continue
            
            draw_creature(creature, CAMERA, True)

            if DRAW_NETWORK:
                nndraw = NN(config, genome, (50, SCREEN_HEIGHT/2), SCREEN_HEIGHT)
                nndraw.update_inputs([
                    f"{inputs[0]}",
                    f"{inputs[1]}",
                    f"{inputs[2]}",
                    f"{inputs[3]}",
                    f"{inputs[4]}",
                    f"{inputs[5]}",
                    f"{inputs[6]}",
                    f"{inputs[7]}",
                    f"{inputs[8]}",
                    f"{inputs[9]}",
                    f"{inputs[10]}",
                    f"{inputs[11]}",
                    f"{inputs[12]}",
                    f"{inputs[13]}",
                    f"{inputs[14]}",
                ])

                nndraw.update_outputs([
                    f"{out[0]>.5}",
                    f"{out[1]>.5}",
                    f"{out[2]>.5}",
                    f"{out[3]>.5}",
                    f"{out[4]>.5}",
                ])

                nndraw.draw(CAMERA.screen)

            if DRAW_STATS:
                draw_properties(creature)

        CAMERA.tick()

print("****** Running Natura ******")

pop = neat.Population(neat.Config(
    Genome, neat.DefaultReproduction,
    neat.DefaultSpeciesSet, neat.DefaultStagnation,
    "./neat-config"
))
pop.add_reporter(neat.Checkpointer(1, None, './saves/gen-'))

best = pop.run(eval_genomes)

with open('./saves/best-genome', 'wb') as f:
    pickle.dump(best, f)