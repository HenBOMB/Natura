import pickle

class Population():
    def __init__(self):
        self.population = []

    def save(self, path: str):
        with open(path, 'wb') as f:
            pickle.dump(self.population, f)
            print(f"Saved population of {len(self.population)} to {path}")

    def load(self, path: str):
        with open(path, 'rb') as f:
            self.population = pickle.load(f)
            print(f"Loaded population of {len(self.population)} from {path}")