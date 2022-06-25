import math
import neat

from natura.food import Food
from natura.genome import Genome, Genes
from natura.world import World
from natura.util import dist, energy_to_mass, angle_vec, sub_vec, percent, clamp, pixel_to_meter, meter_to_pixel
from random import random

class Creature(object):

    def __init__(self, genome: Genome, config: neat.Config, start_pos: tuple):
        self.GENE_FOV           = 45#genome.get_value(Genes.FOV)
        self.GENE_ENERGY        = 25#genome.get_value(Genes.ENERGY)
        self.GENE_HEALTH        = 100#genome.get_value(Genes.HEALTH)
        self.GENE_SPEED         = 1#genome.get_value(Genes.SPEED)
        self.GENE_VIEW_RANGE    = 5#genome.get_value(Genes.VIEW_RANGE)
        self.GENE_COLOR         = (100,100,100)#genome.get_value(Genes.COLOR)
        self.GENE_HUNGER        = .6#genome.get_value(Genes.HUNGER_BIAS)
        self.MAX_WASTE          = energy_to_mass(self.GENE_ENERGY / 3) # mass

        self.config             = config
        self.genome             = genome
        self.network            = neat.nn.FeedForwardNetwork.create(genome, config)
        self.pos                = start_pos
        self.angle              = random() * 2 * math.pi # radians
        self.energy             = self.GENE_ENERGY
        self.health             = self.GENE_HEALTH
        self.size_px            = energy_to_mass(self.GENE_ENERGY) * 8
        self.speed              = 0 # m/s
        self.mass               = 0 # mass
        self.weight             = 0 # mass * GRAVITY
        self.mass_waste         = 0 # mass
        self.do_eat_food        = False
        self.do_release_waste   = False

        # generic value used by other proceses
        self.color              = self.GENE_COLOR

    def get_closest(self, fwd: tuple, max_dist: int, array: list):
        _dist   = max_dist
        _angle  = 0
        _color  = (0, 0, 0)
        _count  = 0
        _index  = 0

        for i, item in enumerate(array):
            angle = angle_vec(fwd, sub_vec(item.pos, self.pos))
            if angle > self.GENE_FOV: continue

            _count += 1

            d = pixel_to_meter(dist(item.pos, self.pos))
            if d >= _dist: continue

            right = (math.cos(self.angle + math.pi / 2), math.sin(self.angle + math.pi / 2))
            angle_right = angle_vec(right, sub_vec(item.pos, self.pos))
            
            if angle_right > 90: angle *= -1

            _dist = d
            _angle = math.radians(angle)
            _color = item.color
            _index = i

        return (_dist, _angle, _color, _count, _index)

    # LEFT OFF:
    # Was gonna implement offsprings
    # also i added 3 inputs, creature stuff
    # finish and test realtime-simulation.py
    
    def tick(self, world: World, delta: float, pop: list = None):
        self.mass = energy_to_mass(self.GENE_ENERGY) + self.mass_waste
        self.weight = self.mass * 9.81

        # maybe if the creature runs out of energy it can transform health -> energy
        # depending on how much it costs to regenerate health, could work out some constant for the conversion
        if self.health <= 0:
            # food = Food(self.pos, mass_to_energy(self.mass - self.waste) * 4, TYPE_MEAT)
            # world.set_food(food)
            return ((), ())

        # energy spent per second
        # print((self.GENE_SPEED / 2 * self.mass) + (self.mass / 0.733), 'e/s')

        # how does metabolism affect digestion speed or energy consumption..?

        # print(len(self.genome.connections))

        fwd = (math.cos(self.angle), math.sin(self.angle))

        _creature_dist  = self.GENE_VIEW_RANGE
        _creature_angle = 0 
        _creature_count = 0 
        _crature_rgb    = (0, 0, 0)

        _food_dist      = self.GENE_VIEW_RANGE
        _food_angle     = 0
        _food_count     = 0
        _food_rgb       = (0, 0, 0)
        _food_index     = 0

        #_dist, _angle, _color, _count, _index

        if pop != None:
            _v = self.get_closest(fwd, _creature_dist, pop)
            _creature_dist, _creature_angle, _crature_rgb, _creature_count, _ = _v
        if self.do_eat_food:
            _v = self.get_closest(fwd, _food_dist, world.food)
            _food_dist, _food_angle, _food_rgb, _food_count, _food_index = _v
            
        # A observer class inherit from sense, returns info from external information
        # A sense base class goes in input and returns info from myself (creature)
        # These are hidden in the code, eg: food.pos, see, where did i get that.. not from myself ofc

        # energy intake class, how well it converts food to energy, or what food it prefers..?
        # Sense class as object?? maybe lol
        # returns a name and value to change
        # gets put in sense input node
        # or a memory node, returns a val when requested OH, same as actual neuron
        # 0 - 100% value on how hungry the creature is if energy / max < self.GENE_HUNGER
        _hungriness = self.energy / (self.GENE_ENERGY * self.GENE_HUNGER) if self.energy / self.GENE_ENERGY < self.GENE_HUNGER else 0

        # could have different methods, maybe not percent the input, and just send it in raw

        inputs = (
            # SENSES #

            # health
            percent(self.health, self.GENE_HEALTH),
            # hungriness
            round(_hungriness * 100),
            # speed %
            percent(self.speed, self.GENE_SPEED),

            # VISION #

            # angle to closest creature
            percent(_creature_angle, self.GENE_FOV),
            # distance to closest creature
            percent(_creature_dist, self.GENE_VIEW_RANGE),
            # color of closest creature
            percent(_crature_rgb[0], 255),
            percent(_crature_rgb[1], 255),
            percent(_crature_rgb[2], 255),
            # creature count in sight
            _creature_count,
            # angle to closest food
            percent(math.degrees(_food_angle), self.GENE_FOV),
            # distance to closest food
            percent(_food_dist, self.GENE_VIEW_RANGE),
            # food count in sight
            _food_count,
            # color of closest food
            percent(_food_rgb[0], 255),
            percent(_food_rgb[1], 255),
            percent(_food_rgb[2], 255),
        )

        out = self.network.activate(inputs)

        # output = lambda i : out[i] > .5

        self.do_eat_food = True#out[4] > .5

        self.speed = self.GENE_SPEED if out[0] > .5 else self.GENE_SPEED / 3 if out[1] > .5 else 0

        # NOTE: for eye quality, just blur the results more or less yk, and use lerp on the eye quality get the most accurate result!!

        # you can just use lerp and delta as t to smooth things out!
        # has more control rather than multiplying the value by delta!!

        # region testing
        # testing: using physics to move the creature

        # REMEMBER THAT DELTA IS DISTANCE!
        # its like cut into 60 parts that completes a computation second? ish-
        # once 60 frames are complete, that travels 1 meter
        # aka 1 second
        # aka 1m/s

        # mass = self.max_energy / 50 # each kg will store 30 energy
        # e=mc2
        # energy from mass = 1m * 29.9792458**2 / 5
        # mass from energy = 10e / (29.9792458**2 / 5)
        # 10 = x * 0.5
        # 10 / 0.5 = x

        # Δ = change in
        # a = Δv / Δt
        # a = (v(f)−v(i)) / (t(f)−t(i))
        # f = m * a

        # find a way to use force instead of self.speed
        # speed = some equation idk
        # this is much better cause at move start, move costs more, but to maintain the movement, it costs less!
        # or not cause we only simulating like legs or somethin

        # work
        # fd = force(Newtons) * distance(Meter)
        # W = Fd = 1/2 * m * v^2
        # v^2 = (Fd) / (1/2 * m)

        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        # coef = 0.05
        # distance = 1
        
        # ffric = coef * self.weight * delta # gravity is now affected by delta

        # vf = new_speed / 1 * delta
        # vi = self.speed / 1 * delta
        # # v = distance / time
        # # kinetic energy
        # # ke = 1/2 * m * v^2
        # # add - cause we want to consume energy
        # move_energy = -.5 * mass * self.speed**2

        # force = mass * (vf - vi) / delta

        # new_v = ((force - ffric) * distance) / (0.5 * mass)
        # # no work will be done once the creature starts moving
        # # new_speed = work / (0.5 * mass)

        # new_speed += new_v * delta

        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

        # energy per second
        # print("e/s ", move_energy)

        # endregion

        if out[2] > .5: self.angle += math.pi / 2 * 4 * delta
        if out[3] > .5: self.angle -= math.pi / 2 * 4 * delta
        if out[0] > .5:
            self.pos = (
                max(-world.width,  min(world.width,  self.pos[0] + math.cos(self.angle) * meter_to_pixel(self.speed) * delta)), 
                max(-world.height, min(world.height, self.pos[1] + math.sin(self.angle) * meter_to_pixel(self.speed) * delta)))
        elif out[1] > .5:
            self.pos = (
                max(-world.width,  min(world.width,  self.pos[0] + math.cos(self.angle + math.pi) * meter_to_pixel(self.speed) * delta)), 
                max(-world.height, min(world.height, self.pos[1] + math.sin(self.angle + math.pi) * meter_to_pixel(self.speed) * delta)))

        self.drain_energy(self.speed / 2 * self.mass * delta)
        # https://journals.biologists.com/jeb/article/208/9/1717/9377/Body-size-energy-metabolism-and-lifespan
        self.drain_energy(self.mass / 0.733 * delta) # metabolic rate 0.666 - 0.8

        if self.energy <= 0:
            self.health = 0
            return (inputs, out)

        if self.do_eat_food:
            food = world.food[_food_index]
            if meter_to_pixel(_food_dist) - self.size_px < food.size:
                self.eat_food(food)

        return (inputs, out)

    def eat_food(self, food: Food):
        # make a vault for the food, when full, it means it has to poop
        # a min max capacity, when the first fill (max1) + next fill reach global max, then poop inminent
        # like humans
        # its not like you can poop whenever, only when the vault is fool
        # aka intestines
        # if self.mass_waste >= self.MAX_WASTE:
        #     # pooping takes time depending on the amount to release
        #     return

        #TODO: here 0.3 can be how well it compresses its shit lol
        # quality = 0.6
        # self.mass_waste += self.MAX_WASTE * quality

        self.gain_energy(food.eat(self.MAX_WASTE))

    def gain_energy(self, energy: float):
        self.energy += energy
        self.energy = clamp(self.energy, 0, self.GENE_ENERGY)

    def drain_energy(self, energy: float):
        self.energy -= energy
        self.energy = clamp(self.energy, 0, self.GENE_ENERGY)