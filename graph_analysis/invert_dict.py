from collections import defaultdict

class DictInverter:
    def __init__(self, dictionary: dict):
        self.new_dict = defaultdict(0)
        self.dictionary = dictionary
    def invert(self):
        for val in self.dictionary.values():
            self.new_dict[val] += 1
