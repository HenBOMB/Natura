from copy import copy
import math
import neat

from natura.food import Food
from natura.genome import Genome, Genes
from natura.world import World
from natura.util import dist, angle_vec, sub_vec, percent, clamp, pixel_to_meter, meter_to_pixel, lerp, circle_to_mass
from random import random

# https://discord.com/channels/@me/935436884681846854/990679103512408235
# https://discord.com/channels/@me/935436884681846854/990687154160156702

class Creature(object):

    def __init__(self, genome: Genome, config: neat.Config, start_pos: tuple, world: World, is_baby = False):
        self.config             = config
        self.genome             = genome
        self.network            = neat.nn.FeedForwardNetwork.create(genome, config)
        self.world              = world

        self.GENE_HEALTH        = genome.get_value(Genes.HEALTH)
        self.GENE_FOV           = genome.get_value(Genes.FOV)
        self.GENE_VIEW_RANGE    = genome.get_value(Genes.VIEW_RANGE)
        self.GENE_COLOR         = genome.get_value(Genes.COLOR)
        self.GENE_HUNGER        = genome.get_value(Genes.HUNGER_BIAS)
        self.GENE_REP_URGE      = genome.get_value(Genes.REPRODUCTION_URGE)
        self.GENE_SPEED         = genome.get_value(Genes.SPEED)
        self.GEN_MATURITY_LENGTH        = genome.get_value(Genes.MATURITY_LENGTH)
        self.GEN_MATURITY_RATE          = genome.get_value(Genes.MATURITY_RATE)
        self.GEN_BABY_MATURITY_LENGTH   = genome.get_value(Genes.BABY_MATURITY_LENGTH)

        self.maturity           = self.GEN_MATURITY_LENGTH * (1-int(is_baby))
        self.min_size           = genome.get_value(Genes.BABY_SIZE)
        '''
        BABY_SIZE = 1.2m
        MATURITY_LENGTH = 60s
        BABY_MATURITY_LENGTH = 50%

        GOAL = MATURITY_LENGTH * BABY_MATURITY_LENGTH / 100 = 30 seconds

        meaning at {GOAL} the creature will hatch with a size of {BABY_SIZE} meters

        so, how much increase per second?

        1s = MATURITY_LENGTH / GOAL = 2

        BABY_SIZE * (MATURITY_LENGTH / GOAL)

        1.2m (30s) --> ?m (60s)
        '''
        self.max_size           = self.min_size * (self.GEN_MATURITY_LENGTH / (self.GEN_MATURITY_LENGTH * self.GEN_BABY_MATURITY_LENGTH))

        self.min_energy         = circle_to_mass(self.min_size) * .2 # 20%
        self.max_energy         = circle_to_mass(self.max_size) * .2 # 20%
        
        self.max_speed          = self.GENE_SPEED
        self.max_health         = self.GENE_HEALTH

        self.pos                = start_pos
        self.angle              = random() * 2 * math.pi # radians
        self.speed              = 0 # m/s
        self.reproduction_urge  = 0
        self.dead               = False

        # this is nescessary because mature() will not run if 1
        # either way, if it did ran, it wouldn't change any of the values
        self.energy             = self.max_energy
        self.health             = self.max_health
        self.size_px            = meter_to_pixel(self.max_size)
        self.mass               = circle_to_mass(self.max_size)
        self.weight             = self.mass * self.world.gravity

        # print(f'size        | {self.min_size}m -> {self.max_size}m')
        # print(f'energy      | {self.min_energy} -> {self.max_energy}')
        # print(f'mass        | {self.mass}')
        # print(f'weight      | {self.weight}kg')
        # print(f'speed       | {self.GENE_SPEED}m/s')
        # print(f'consumption | {self.mass * .05}e/s')
        # print(f'consumption | {self.GENE_SPEED / 2 * self.mass * .05}e/s')
        # print(f'lifetime    | {self.max_energy/(self.mass * .05)}')

        # TODO: maybe combine this with fitness..????!
        # humans are programmed to love high calorie foods
        
        # TODO:
        '''
        a = pi * r * r
        if you make the adult size proportional to the baby size, then the parent size is always limited to that..
        unless: the baby size has no limit, cause it does now..
        add a gene that simulates old age.. for example
        curve the m value to be higher lower and lower higher
        baby__/\__adult
        '''

        '''
        a good method of generating energy capacity
        well, what happens is excess food to be converted to energy is stored as fat
        aka when the body doesn't need energy

        suppose we just start with a bunch of energy.. so how much, whats the limit??

        get the cost of living per second

        its proportional to how much mass enters the body, that mass has to go somewhere!
        so, stomach size is nescessary
        this will limit the amount of energy input cause of the stomach size limit
        from here, we can formulate 
        hm
        '''

        # generic values used by other proceses
        self.color              = self.GENE_COLOR
        self.species            = ""
        self.consumption        = 0

    def mature(self, delta):
        baby_maturity_length = self.GEN_MATURITY_LENGTH * self.GEN_BABY_MATURITY_LENGTH

        self.maturity += self.GEN_MATURITY_RATE * delta
        self.maturity = min(self.maturity, self.GEN_MATURITY_LENGTH)

        perc = self.maturity / self.GEN_MATURITY_LENGTH

        if perc > .85 and not self.is_baby():
            self.GENE_REP_URGE = self.genome.get_value(Genes.REPRODUCTION_URGE)

        if self.is_baby():      
            self.size_px = self.min_size
        else:  
            bby_perc = min(self.maturity / baby_maturity_length, baby_maturity_length)
            self.size_px = lerp(self.min_size, self.max_size, (self.maturity - bby_perc) / (self.GEN_MATURITY_LENGTH - bby_perc))

        self.mass       = circle_to_mass(self.size_px)
        self.size_px    = meter_to_pixel(self.size_px)
        self.weight     = self.mass * self.world.gravity
        self.max_speed  = self.GENE_SPEED * perc
        self.max_health = self.GENE_HEALTH * perc

    def baby_mature(self):
        # this gene is an exception, because it'll only activate when mature enough
        self.GENE_REP_URGE  = 0
        # this is not really nescessary cause when the baby stage ends, self.energy will be self.MIN_ENERGY regardless
        # self.energy       = lerp(self.MIN_ENERGY, self.MAX_ENERGY, self.maturity / self.GEN_MATURITY_LENGTH)
        self.energy         = self.min_energy
        self.health         = self.max_health
    
    def lay_egg(self, pop: list):
        genome = copy(self.genome)
        # genome.mutate(self.config.genome_config)
        genome.mutate_genes()
        self.drain_energy(self.min_energy)
        c = Creature(genome, self.config, self.pos, self.world, True)
        c.species = self.species
        pop.append(c)

    def tick(self, delta: float, pop: list = None):
        if self.dead:
            return ((), ())

        if self.maturity != self.GEN_MATURITY_LENGTH:
            self.mature(delta)
            if self.is_baby():
                self.baby_mature()
                return

        # how does metabolism affect digestion speed or energy consumption..?

        # print(len(self.genome.connections))

        fwd = (math.cos(self.angle), math.sin(self.angle))

        _creature_dist  = self.GENE_VIEW_RANGE
        _creature_angle = 0 
        _creature_count = 0 
        _crature_rgb    = (0, 0, 0)

        # NOTE: for eye quality, just blur the results more or less yk, and use lerp on the eye quality get the most accurate result!!

        # you can just use lerp and delta as t to smooth things out!
        # has more control rather than multiplying the value by delta!!

        if pop != None:
            _v = self.get_closest(fwd, self.GENE_VIEW_RANGE, pop)
            _creature_dist, _creature_angle, _crature_rgb, _creature_count, _ = _v

        _v = self.get_closest(fwd, self.GENE_VIEW_RANGE, self.world.food)
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
        _hungriness = self.energy / (self.max_energy * self.GENE_HUNGER) if self.energy / self.max_energy < self.GENE_HUNGER else 0

        # could have different methods, maybe not percent the input, and just send it in raw

        # mimic urge to reproduce:
        # could be a float that is added per tick aka 1 second
        # but for that we'd need think speed yk
        if pop and self.GENE_REP_URGE != 0:
            self.reproduction_urge += self.GENE_REP_URGE * delta
            self.reproduction_urge = min(self.reproduction_urge, 1)

        inputs = (
            # SENSES #

            # health
            percent(self.health, self.max_health),
            # hungriness
            round(_hungriness * 100),
            # speed %
            percent(self.speed, self.max_speed),
            # urge to reproduce
            self.reproduction_urge == 1,

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

        _out = self.network.activate(inputs)

        _go_forward         = _out[0] > .5
        _go_back            = _out[1] > .5
        _go_right           = _out[2] > .5
        _go_left            = _out[3] > .5
        _go_eat_food        = True#out[4] > .5
        _go_reproduce       = _out[5] > .5

        if _go_reproduce and pop:
            self.reproduction_urge = 0
            self.lay_egg(pop)

        self.speed = self.max_speed if _go_forward else self.max_speed / 1.5 if _go_back else 0

        # TODO: Using physics to move the creature
        '''
        testing: using physics to move the creature

        REMEMBER THAT DELTA IS DISTANCE!
        its like cut into 60 parts that completes a computation second? ish-
        once 60 frames are complete, that travels 1 meter
        aka 1 second
        aka 1m/s

        mass = self.max_energy / 50 # each kg will store 30 energy
        e=mc2
        energy from mass = 1m * 29.9792458**2 / 5
        mass from energy = 10e / (29.9792458**2 / 5)
        10 = x * 0.5
        10 / 0.5 = x

        Δ = change in
        a = Δv / Δt
        a = (v(f)−v(i)) / (t(f)−t(i))
        f = m * a

        find a way to use force instead of self.speed
        speed = some equation idk
        this is much better cause at move start, move costs more, but to maintain the movement, it costs less!
        or not cause we only simulating like legs or somethin

        work
        fd = force(Newtons) * distance(Meter)
        W = Fd = 1/2 * m * v^2
        v^2 = (Fd) / (1/2 * m)

        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        coef = 0.05
        distance = 1
        ffric = coef * self.weight * delta # gravity is now affected by delta

        vf = new_speed / 1 * delta
        vi = self.speed / 1 * delta
        # v = distance / time
        # kinetic energy
        # ke = 1/2 * m * v^2
        # add - cause we want to consume energy
        move_energy = -.5 * mass * self.speed**2

        force = mass * (vf - vi) / delta

        new_v = ((force - ffric) * distance) / (0.5 * mass)
        # no work will be done once the creature starts moving
        # new_speed = work / (0.5 * mass)

        new_speed += new_v * delta
        '''

        if _go_right: self.angle += math.pi / 2 * 4 * delta
        if _go_left: self.angle -= math.pi / 2 * 4 * delta
        if _go_forward > .5:
            self.pos = (
                max(-self.world.width,  min(self.world.width,  self.pos[0] + math.cos(self.angle) * meter_to_pixel(self.speed) * delta)), 
                max(-self.world.height, min(self.world.height, self.pos[1] + math.sin(self.angle) * meter_to_pixel(self.speed) * delta)))
        elif _go_back > .5:
            self.pos = (
                max(-self.world.width,  min(self.world.width,  self.pos[0] + math.cos(self.angle + math.pi) * meter_to_pixel(self.speed) * delta)), 
                max(-self.world.height, min(self.world.height, self.pos[1] + math.sin(self.angle + math.pi) * meter_to_pixel(self.speed) * delta)))

        # https://journals.biologists.com/jeb/article/208/9/1717/9377/Body-size-energy-metabolism-and-lifespan
        # speed cost
        self.consumption = self.speed / 2 * self.mass * delta * .05
        # metabolism
        self.consumption += self.mass * .05 * delta

        self.drain_energy(self.consumption)

        # maybe if the creature runs out of energy it can transform health -> energy
        # depending on how much it costs to regenerate health, could work out some constant for the conversion
        
        if self.energy <= 0:
            self.health = 0
            self.dead   = True
            return (inputs, _out)

        if _go_eat_food:
            if len(self.world.food) > 0:
                food: Food = self.world.food[_food_index]
                m = pixel_to_meter(self.size_px)
                if _food_dist - m < food.radius:
                    self.gain_energy(food.eat(m/3))

        return (inputs, _out)
    
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

    def gain_energy(self, energy: float):
        self.energy += energy
        self.energy = clamp(self.energy, 0, self.max_energy)

    def drain_energy(self, energy: float):
        self.energy -= energy
        self.energy = clamp(self.energy, 0, self.max_energy)

    def is_baby(self) -> bool:
        return self.maturity <= self.GEN_BABY_MATURITY_LENGTH * self.GEN_MATURITY_LENGTH
