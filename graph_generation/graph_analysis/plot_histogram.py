import argparse
import json
import matplotlib.pyplot as plt

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--path", type=str)
    args = parser.parse_args()
    
    with open(args.path, "r") as f:
        dictionary = json.load(f)
    
    keys = list(map(float, dictionary.keys()))
    values = list(dictionary.values())
    
    plt.hist(keys, weights=values, bins=len(dictionary))
    plt.xlabel('centrality')
    plt.ylabel('frequency')
    plt.show()