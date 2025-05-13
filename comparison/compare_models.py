import ollama
import time
import argparse
from tqdm import tqdm
import re

class Processor:
    def __init__(self, data, model, host, prompt):
        self.data = data
        self.model = model
        self.host = host
        self.prompt = prompt

    def evaluate(self):
        client = ollama.Client(self.host)
        performance = []
        for sentence in tqdm(self.data, desc=f"[{self.host} : {self.model}]"):
            start_time = time.perf_counter()
            try:
                response = client.generate(self.model, self.prompt + "\n" + sentence["text"]).response
                score = re.findall(r"-?\d+\.?\d*", response)
                sentiment = float(score[-1])
            except:
                sentiment = 3
            performance.append((abs(sentiment - sentence["label"]), time.perf_counter() - start_time))
        
        return performance

if __name__ == "__main__":
    import json
    ArgumentParser = argparse.ArgumentParser()
    ArgumentParser.add_argument("--host", type=str)
    ArgumentParser.add_argument("--model", type=str, nargs="+")
    ArgumentParser.add_argument("--data_path", type=str)
    ArgumentParser.add_argument("--prompt_path", type=str)
    args = ArgumentParser.parse_args()

    with open(args.data_path, 'r', encoding='utf-8') as file:
        data = [json.loads(line) for line in file]
    
    with open(args.prompt_path, "r") as file:
        prompt = file.read()

    comparison = {}

    for model in args.model:
        process = Processor(data[:10], model, args.host, prompt)
        current = process.evaluate()
        cumulative_error = 0
        total_Time = 0
        assertiveness = 0
        for score, Time in current:
            cumulative_error += score
            total_Time += Time
            assertiveness += (score == 0)
        comparison[model] = [(f"assertiveness {assertiveness}", f"cumulative_error {cumulative_error}", f"total_Time {total_Time}"), current]
    
    with open("model_comparison.json", "w") as f:
        json.dump(comparison, f)