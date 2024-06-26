import re, sys

def get(name, default):
    for i in range(1, len(sys.argv)):
        m = re.findall("(?<=--)\w+", sys.argv[i])
        if len(m) == 1 and m[0] == name:
            return sys.argv[i+1]
    return default

def has(name):
    for i in range(1, len(sys.argv)):
        m = re.findall("(?<=--)\w+", sys.argv[i])
        if len(m) == 1 and m[0] == name:
            return True
    return False
