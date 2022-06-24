if __name__ != '__main__':
    raise ImportError(f"Cannot import module '{__file__}'")

from fileinput import filename
import sys
import neat
import pygame
import pickle
import natura

pygame.init()
pygame.font.init()
pygame.display.set_caption("Natura - Life Evolution")

from natura import Creature, World, util, Genome
from nndraw import NN
from camera import Camera
from random import randint, uniform, random
from math   import radians, sin, cos

SCREEN_WIDTH        = 1600
SCREEN_HEIGHT       = 1000
WORLD_WIDTH         = 1500
WORLD_HEIGHT        = 1500
FPS                 = 60

TEXT_FONT     = pygame.font.SysFont("comicsans", 15)
WORLD               = World(WORLD_WIDTH, WORLD_HEIGHT)
CAMERA              = Camera(SCREEN_WIDTH, SCREEN_HEIGHT)
IMAGE_FOOD          = pygame.image.load('./assets/food.png', 'food')

DRAW_NETWORK        = False
DRAW_STATS          = False
QUIT = False
# Will not draw anything, just run the simulation
ONLY_SIMULATE = False

COLOR_BACKGROUND    = (0, 0, 16)
COLOR_HIGHLIGHT     = (COLOR_BACKGROUND[0], COLOR_BACKGROUND[1], COLOR_BACKGROUND[2] * 4)
COLOR_WHITE         = (255, 255, 255)

# Statistics
GENERATION = 0
MAX_FITNESS = 0
MAX_FITNESS_ARR = [0]

def draw_text(txt: str, pos: tuple, color = COLOR_WHITE):
    CAMERA.screen.blit(TEXT_FONT.render(str(txt), True, COLOR_WHITE), pos)

def draw_properties(creature: Creature):
    width, height = (300, 100)
    surf = pygame.Surface((width, height), pygame.SRCALPHA)
    surf.fill((100, 100, 100, 100))
    CAMERA.screen.blit(surf, (SCREEN_WIDTH - width, 0))

    def draw_txt(txt, i):
        text = TEXT_FONT.render(str(txt), True, COLOR_WHITE)
        CAMERA.screen.blit(text, (SCREEN_WIDTH - width, 7.5 * 2 * i))

    def draw_v_txt(txt, i):
        text = TEXT_FONT.render(str(txt), True, COLOR_WHITE)
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

def draw_stats(pop_count: int):
    surf = pygame.Surface((200, 85), pygame.SRCALPHA)
    surf.fill((0, 0, 0, 200))
    CAMERA.screen.blit(surf, (0, 0))

    draw_text(f"Generation: {GENERATION}", (0, 0))
    draw_text(f"Max Fitness: {MAX_FITNESS_ARR[len(MAX_FITNESS_ARR)-1]}", (0, 20))
    draw_text(f"Avr Fitness: {sum(MAX_FITNESS_ARR)/len(MAX_FITNESS_ARR)}", (0, 40))
    draw_text(f"Pop count: {pop_count}", (0, 60))

def draw_creature(c: Creature, highlight: bool = False):
    CAMERA.draw_circle(c.GENE_COLOR, c.pos, c.size_px)
    rad = radians(c.GENE_FOV/1.5)
    CAMERA.draw_circle((0,0,0), (
            c.pos[0] + cos(c.angle-rad) * c.size_px, 
            c.pos[1] + sin(c.angle-rad) * c.size_px), c.size_px / 4)
    CAMERA.draw_circle((0,0,0), (
            c.pos[0] + cos(c.angle+rad) * c.size_px, 
            c.pos[1] + sin(c.angle+rad) * c.size_px), c.size_px / 4)

    if highlight:
        CAMERA.draw_circle((200, 200, 200), c.pos, c.size_px+5, 1)

def draw_world():
    for i, food in enumerate(WORLD.food):
        CAMERA.draw_image(IMAGE_FOOD, (food.pos[0] - food.size / 2, food.pos[1] - food.size / 2), food.size * 2.5)

def draw_static():
    CAMERA.clear_screen()
    draw_text(f"Generation: {GENERATION}", (0, 0))
    draw_text(f"Max Fitness: {MAX_FITNESS_ARR[len(MAX_FITNESS_ARR)-1]}", (0, 20))
    draw_text(f"Avr Fitness: {sum(MAX_FITNESS_ARR)/len(MAX_FITNESS_ARR)}", (0, 40))
    draw_text(f"Press 'F' to resume viewing the realtime simulation", (0, 80))
    pygame.display.update()

def eval_genomes(_genomes: list, config: neat.Config):
    global DRAW_NETWORK, DRAW_STATS, QUIT, ONLY_SIMULATE, GENERATION, MAX_FITNESS
    MAX_FITNESS = 0

    if QUIT:
        pygame.quit()
        sys.exit()

    GENERATION += 1

    WORLD.clear()
    WORLD.spawn_food(250)

    population  = []
    tick_count  = 0
    dragging    = False

    for genome_id, genome in _genomes:
        genome.fitness = 0
        population.append(Creature(genome, config, (uniform(-WORLD_WIDTH, WORLD_WIDTH), uniform(-WORLD_HEIGHT, WORLD_HEIGHT))))

    creature_index = randint(0, len(population)-1)

    if ONLY_SIMULATE:
        draw_static()

    # smallest distance for the creature and world is limited to delta aka our plank length
    # so delta = 0.1 should be 1 meter since 1 pixel = 10 meters
    # or, if that is wrong: delta * m/s = meters sinde t value cancels out
    while True:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                QUIT = True
                for creature in population:
                    creature.health = 0

            elif event.type == pygame.WINDOWMINIMIZED:
                print("WARNING! Simulation Paused due to pygame enabled and window minimized")

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
                    if d < CAMERA.fix_scale(creature.size_px*2):
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
                elif event.key == pygame.K_RETURN:
                    ONLY_SIMULATE = not ONLY_SIMULATE
                    draw_static()
                elif event.key == pygame.K_f:
                    if len(population) != 0:
                        CAMERA.set_global_pos(population[creature_index].pos)

            elif event.type == pygame.K_UP:
                creature_index += 1
                if creature_index == len(population): creature_index = 0

            elif event.type == pygame.K_DOWN:
                creature_index -= 1
                if creature_index < 0: creature_index = len(population) - 1

        WORLD.tick()

        if not ONLY_SIMULATE:
            CAMERA.clear_screen()
            CAMERA.draw_rect(COLOR_BACKGROUND, (-WORLD_WIDTH, -WORLD_HEIGHT, WORLD_WIDTH*2, WORLD_HEIGHT*2))
            draw_world()

        creature: Creature
        for i, creature in enumerate(population):
            delta = 0.03 if ONLY_SIMULATE else CAMERA.delta
            inputs, out = creature.tick(WORLD, delta, population)

            if creature.health <= 0: 
                # this is the issue, all the fitnesses are getting moved somewhere else..?
                creature.genome.fitness = tick_count / 100.
                population.pop(i)
                if creature.genome.fitness > MAX_FITNESS:
                    MAX_FITNESS = creature.genome.fitness
                    MAX_FITNESS_ARR.append(MAX_FITNESS)
                    if len(MAX_FITNESS_ARR) == 5: MAX_FITNESS_ARR.pop(0)
                
                if len(population) == 0: return
                continue

            if ONLY_SIMULATE: continue

            if i != creature_index:
                draw_creature(creature)
                continue
            
            draw_creature(creature, True)

            if DRAW_NETWORK:
                nndraw = NN(config, genome, (50, SCREEN_HEIGHT/2), SCREEN_HEIGHT)
                nndraw.update_inputs([
                    f"H {inputs[0]}",
                    f"H {inputs[1]}",
                    f"S {inputs[2]}",
                    f"A {inputs[3]}",
                    f"D {inputs[4]}",
                    f"R {inputs[5]}",
                    f"G {inputs[6]}",
                    f"B {inputs[7]}",
                    f"C {inputs[8]}",
                    f"A {inputs[9]}",
                    f"D {inputs[10]}",
                    f"R {inputs[11]}",
                    f"G {inputs[12]}",
                    f"B {inputs[13]}",
                    f"C {inputs[14]}",
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

        if not ONLY_SIMULATE:
            draw_stats(len(population))
            CAMERA.tick(FPS)

        tick_count += 1

print("****** Running Natura ******")

cp = neat.Checkpointer(10, None, './saves/gen-')

# pop = neat.Population(neat.Config(
#     Genome, neat.DefaultReproduction,
#     neat.DefaultSpeciesSet, neat.DefaultStagnation,
#     "./neat-config"
# ))
pop = cp.restore_checkpoint('./saves/gen-289')

pop.add_reporter(cp)
pop.add_reporter(neat.StdOutReporter(True))

best = pop.run(eval_genomes)

with open('./saves/best-genome', 'wb') as f:
    pickle.dump(best, f)