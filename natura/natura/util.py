import math
import random

# 1 pixel = 0.01 meters
# 100 pixels = 1 meter

def pixel_to_meter(pixels):
    return pixels / 100

def meter_to_pixel(meter):
    return meter * 100

def clamp(v: float, mi: float, mx: float):
    return max(mi, min(mx, v))

def dist(v1: tuple, v2: tuple):
    return math.sqrt((v1[0]-v2[0])**2+(v1[1]-v2[1])**2)

def lerp(a: float, b: float, t: float):
    return a + (b - a) * t
    
def rand_negpos(seed: float):
    random.seed(seed)
    return (random.random() - .5) * 2

def percent(a, b):
    if b == 0: return 0
    return round((a / b) * 100)

def rand_bool():
    return random.random() > .5

def normalize(v: tuple):
    d = norm(v)
    return div_vec(v, (d, d))

def angle_vec(v1, v2):
    try:
        return math.degrees(math.acos((v1[0]*v2[0] + v1[1]*v2[1])/(math.hypot(v1[0], v1[1])*math.hypot(v2[0], v2[1]))))
    except:
        return 0

def add_vec(v1: tuple, v2: tuple):
    return (v1[0] + v2[0], v1[1] + v2[1])

def sub_vec(v1: tuple, v2: tuple):
    return (v1[0] - v2[0], v1[1] - v2[1])

def mul_vec(v1: tuple, v2: tuple):
    return (v1[0] * v2[0], v1[1] * v2[1])

def div_vec(v1: tuple, v2: tuple):
    if v2[0] == 0 and v2[1] == 0: return (0, 0)
    elif v2[0] == 0: return (0, v1[1] / v2[1])
    elif v2[1] == 0: return (v1[0] / v2[0], 0)
    return (v1[0] / v2[0], v1[1] / v2[1])

def clamp_vec(v1: tuple, min: float, max: float):
    return (clamp(v1[0], min, max), clamp(v1[1], min, max))

def norm(v: tuple):
    return math.sqrt(v[0]*v[0]+v[1]*v[1])

# 50 energy per mass kg
ENERGY_MASS_CONSTANT = 20

def energy_to_mass(energy: float):
    return energy / ENERGY_MASS_CONSTANT

def mass_to_energy(energy: float):
    return energy * ENERGY_MASS_CONSTANT