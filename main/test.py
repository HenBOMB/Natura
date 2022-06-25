# import natura
# import neat

# config = neat.Config(
#     natura.Genome, neat.DefaultReproduction,
#     neat.DefaultSpeciesSet, neat.DefaultStagnation,
#     "./neat-config"
# )

# pop = neat.Population(config)

# genome: natura.Genome = pop.population[1]

# print(genome.connections)

print(None or 1)

'''
my goal is to slowly evolve the basics, and then add more and more inputs aka senses from the ground up

for example:
you cant just give the creature 100% eye quality when it doesn't even know how to eat or last more than 5 seconds being alive
so, start up with nothing but locomotion or upload a custom network using the editor to create and a genome method to upload
--

senses require a certain criteria to be met

current input senses:
- hunger
- health
- speed
- vision

current output tasks:
- simple locomotion
- look for food

we can make it so a sense has to origin from a mutation
but that would require modifying the inputs, which is not possible once the simulation is ran
so, i propose not being able to form connections to them when the sense has not been mutated yet!
'''