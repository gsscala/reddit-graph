import json

with open("centrality.json", "r") as f:
    dictionary = json.load(f)

# Convert keys to floats for numerical sorting
to_sort = [[float(key), val] for key, val in dictionary.items()]
to_sort.sort(key=lambda x: x[0])  # Sort by numerical key

# Compute cumulative sum
for i in range(1, len(to_sort)):
    to_sort[i][1] += to_sort[i-1][1]

# Convert back to dictionary with STRING keys
result = {str(key): val for key, val in to_sort}

with open("accumulated_centrality.json", "w") as f:
    json.dump(result, f, indent=2)
