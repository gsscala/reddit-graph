import random
import json

with open("./sst5/train.jsonl", "r") as f:
    data = [json.loads(line) for line in f]

with open("reference_data_file.json", "w") as f:
    json.dump(random.sample(data, 1000), f)