import math
import random

def clamp(v, mi, mx):
    return max(mi, min(mx, v))

def dist(a, b):
    return math.sqrt((a[0]-b[0])**2+(a[1]-b[1])**2)

def lerp(a, b, t):
    return a + (b - a) * t
    
def rand_negpos(seed):
    random.seed(seed)
    return (random.random() - 0.5) * 2

def normalize(v):
    d = norm(v)
    return div_vec(v, (d, d))

def angle_vec(v1, v2):
    try:
        return math.degrees(math.acos((v1[0]*v2[0] + v1[1]*v2[1])/(math.hypot(v1[0], v1[1])*math.hypot(v2[0], v2[1]))))
    except:
        return 0

def add_vec(v1, v2):
    return (v1[0] + v2[0], v1[1] + v2[1])

def sub_vec(v1, v2):
    return (v1[0] - v2[0], v1[1] - v2[1])

def mul_vec(v1, v2):
    return (v1[0] * v2[0], v1[1] * v2[1])

def div_vec(v1, v2):
    if v2[0] == 0 and v2[1] == 0: return (0, 0)
    elif v2[0] == 0: return (0, v1[1] / v2[1])
    elif v2[1] == 0: return (v1[0] / v2[0], 0)
    return (v1[0] / v2[0], v1[1] / v2[1])

def clamp_vec(v1, min, max):
    return (clamp(v1[0], min, max), clamp(v1[1], min, max))

def norm(v):
    return math.sqrt(v[0]*v[0]+v[1]*v[1])

# 50 energy per mass kg
ENERGY_MASS_CONSTANT = 20

def energy_to_mass(energy):
    return energy / ENERGY_MASS_CONSTANT

def mass_to_energy(energy):
    return energy * ENERGY_MASS_CONSTANT