import math
import neat

from genes import *
from tools import *
from world import *

# energy to mass and vice versa convert value

class Creature():
    def __init__(self, genome: neat.DefaultGenome, genes: Genes, network: neat.nn.FeedForwardNetwork, start_x: int, start_y: int):
        self.genome = genome
        self.genes = genes
        self.network = network
        self.pos = (start_x, start_y)
        self.speed = 0 # m/s
        self.angle = random.random() * 2 * math.pi # radians
        self.fov = genes.get(Genes.FOV) # deg
        self.energy = genes.get(Genes.MAX_ENERGY)
        self.health = genes.get(Genes.MAX_HEALTH)
        self.mass = 0 # mass
        self.weight = 0 # mass * GRAVITY

        self.max_waste = energy_to_mass(genes.get(Genes.MAX_ENERGY) / 3) # mass
        self.mass_waste = 0 # mass

        self.size_px = energy_to_mass(self.genes.get(Genes.MAX_ENERGY)) * 8

        self.do_eat_food = False
        self.do_release_waste = False
    
    def tick(self, world: World, delta: float):
        self.mass = energy_to_mass(self.genes.get(Genes.MAX_ENERGY)) + self.mass_waste
        self.weight = self.mass * GRAVITY

        # maybe if the creature runs out of energy it can transform health -> energy
        # depending on how much it costs to regenerate health, could work out some constant for the conversion
        if self.health <= 0:
            # food = Food(self.pos, mass_to_energy(self.mass - self.waste) * 4, TYPE_MEAT)
            # world.set_food(food)
            return ((), ())

        # energy spent per second
        # print((self.genes.max_speed / 2 * self.mass) + (self.mass / 0.733), 'e/s')

        # how does metabolism affect digestion speed or energy consumption..?

        # print(len(self.genome.connections))

        move_dir = (math.cos(self.angle), math.sin(self.angle))

        in_food_dist = meter_to_pixel(self.genes.get(Genes.MAX_SEE_RANGE))
        in_food_angle = 0
        food_arr_index = 0
        food_count_in_sight = 0

        if self.do_eat_food:        
            for i, food in enumerate(world.food):
                angle = angle_vec(move_dir, sub_vec(food.pos, self.pos))
                if angle > self.fov: continue

                food_count_in_sight += 1

                _dist = dist(food.pos, self.pos)
                if in_food_dist < _dist: continue

                right = (math.cos(self.angle + math.pi / 2), math.sin(self.angle + math.pi / 2))
                angle_right = angle_vec(right, sub_vec(food.pos, self.pos))
                
                if angle_right > 90: angle *= -1

                in_food_angle = math.radians(angle)
                in_food_dist = _dist
                food_arr_index = i

        # A observer class inherit from sense, returns info from external information
        # A sense base class goes in input and returns info from myself (creature)
        # These are hidden in the code, eg: food.pos, see, where did i get that.. not from myself ofc

        # energy intake class, how well it converts food to energy, or what food it prefers..?
        # Sense class as object?? maybe lol
        # returns a name and value to change
        # gets put in sense input node
        # or a memory node, returns a val when requested OH, same as actual neuron
        bias = .5 # TODO: This could be a mutable factor
        # 0 - 100% value on how hungry the creature is if energy / max < bias
        in_hungriness = self.energy / (self.genes.get(Genes.MAX_ENERGY) * bias) if self.energy / self.genes.get(Genes.MAX_ENERGY) < bias else 0
        
        # note, in distance is currently pixels, not meters
        inputs = (
            # hungriness %
            round(in_hungriness * 100),
            # health  %
            round((self.health / self.genes.get(Genes.MAX_HEALTH)) * 100),
            # speed %
            round((self.speed / self.genes.get(Genes.MAX_SPEED)) * 100),
            # flush waste?
            self.mass_waste >= self.max_waste,
            # angle to food
            in_food_angle,
            # distance to food
            in_food_dist,
            # food count in sight
            food_count_in_sight
            # maturity
            # distance to closest creature seen
            # angle
            # number of creatures seen
            # number of food seen
            # rgb of seen creature
        )

        out = self.network.activate(inputs)

        # output = lambda i : out[i] > .5

        self.do_eat_food = out[4] > .5
        # self.do_release_waste = out[5] > .5

        self.speed = self.genes.get(Genes.MAX_SPEED) if out[0] > .5 else self.genes.get(Genes.MAX_SPEED) / 3 if out[1] > .5 else 0

        # if self.do_release_waste: 
        #     self.speed = 0

        # region testing
        # testing: using physics to move the creature

        # REMEMBER THAT DELTA IS DISTANCE!
        # its like cut into 60 parts that completes a computation second? ish-
        # once 60 frames are complete, that travels 1 meter
        # aka 1 second
        # aka 1m/s

        # mass = self.genes.max_energy / 50 # each kg will store 30 energy
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
                max(-WORLD_WIDTH,  min(WORLD_WIDTH,  self.pos[0] + math.cos(self.angle) * meter_to_pixel(self.speed) * delta)), 
                max(-WORLD_HEIGHT, min(WORLD_HEIGHT, self.pos[1] + math.sin(self.angle) * meter_to_pixel(self.speed) * delta)))
        elif out[1] > .5:
            self.pos = (
                max(-WORLD_WIDTH,  min(WORLD_WIDTH,  self.pos[0] + math.cos(self.angle + math.pi) * meter_to_pixel(self.speed) * delta)), 
                max(-WORLD_HEIGHT, min(WORLD_HEIGHT, self.pos[1] + math.sin(self.angle + math.pi) * meter_to_pixel(self.speed) * delta)))

        self.drain_energy(self.speed / 2 * self.mass * delta)
        # https://journals.biologists.com/jeb/article/208/9/1717/9377/Body-size-energy-metabolism-and-lifespan
        self.drain_energy(self.mass / 0.733 * delta) # metabolic rate 0.666 - 0.8

        if self.energy <= 0:
            self.health = 0
            return (inputs, out)

        if self.do_eat_food:
            food = world.food[food_arr_index]
            if in_food_dist - self.size_px < food.size:
                self.eat_food(food)

        # if self.do_release_waste: 
        #     self.release_waste(world)

        return (inputs, out)

    def draw(self, camera: Camera):
        camera.draw_circle(self.genes.get(Genes.COLOR), self.pos, self.size_px)
        rad = math.radians(self.fov/1.5)
        camera.draw_circle((0,0,0), (
                self.pos[0] + math.cos(self.angle-rad) * self.size_px, 
                self.pos[1] + math.sin(self.angle-rad) * self.size_px), self.size_px / 4)
        camera.draw_circle((0,0,0), (
                self.pos[0] + math.cos(self.angle+rad) * self.size_px, 
                self.pos[1] + math.sin(self.angle+rad) * self.size_px), self.size_px / 4)

    def eat_food(self, food: Food):
        # make a vault for the food, when full, it means it has to poop
        # a min max capacity, when the first fill (max1) + next fill reach global max, then poop inminent
        # like humans
        # its not like you can poop whenever, only when the vault is fool
        # aka intestines
        # if self.mass_waste >= self.max_waste:
        #     # pooping takes time depending on the amount to release
        #     return

        #TODO: here 0.3 can be how well it compresses its shit lol
        # quality = 0.6
        # self.mass_waste += self.max_waste * quality

        self.gain_energy(food.eat(self.max_waste))

    def gain_energy(self, energy: float):
        self.energy += energy
        self.energy = clamp(self.energy, 0, self.genes.get(Genes.MAX_ENERGY))

    def drain_energy(self, energy: float):
        self.energy -= energy
        self.energy = clamp(self.energy, 0, self.genes.get(Genes.MAX_ENERGY))

    # def release_waste(self, world: World):
    #     self.mass_waste = 0
    #     world.add_poop(self.pos)