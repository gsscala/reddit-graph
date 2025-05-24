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
        log = []
        for sentence in tqdm(self.data, desc=f"[{self.host} : {self.model}]"):
            start_time = time.perf_counter()
            log.append([self.prompt + "\n" + sentence["text"], "", 2, sentence["label"], 0])
            try:
                response = client.generate(self.model, self.prompt + "\n" + sentence["text"]).response
                log[-1][1] = response
                score = re.findall(r"-?\d+\.?\d*", response)
                sentiment = int(score[-1])
            except:
                sentiment = 2
            finish_time = time.perf_counter()
            elapsed_time = finish_time - start_time
            log[-1][2] = sentiment
            log[-1][4] = elapsed_time
            performance.append((abs(sentiment - sentence["label"]), elapsed_time))
        
        return performance, log

if __name__ == "__main__":
    import json
    ArgumentParser = argparse.ArgumentParser()
    ArgumentParser.add_argument("--host", type=str)
    ArgumentParser.add_argument("--model", type=str, nargs="+")
    ArgumentParser.add_argument("--data_path", type=str)
    ArgumentParser.add_argument("--prompt_path", type=str)
    args = ArgumentParser.parse_args()

    with open(args.data_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
    
    with open(args.prompt_path, "r") as file:
        prompt = file.read()

    for model in args.model:
        process = Processor(data, model, args.host, prompt)
        current, log = process.evaluate()
        cumulative_error = 0
        total_Time = 0
        assertiveness = 0
        for score, Time in current:
            cumulative_error += score
            total_Time += Time
            assertiveness += (score == 0)
        with open(f"./performance/{model}_performance.json", 'w') as f:
            json.dump([(f"assertiveness {assertiveness}", f"cumulative_error {cumulative_error}", f"total_Time {total_Time}"), current], f)
        with open (f"./log/{model}_log.json", "w") as f:
            json.dump(log, f)