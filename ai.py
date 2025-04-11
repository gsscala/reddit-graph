import ollama

client = ollama.Client(host='http://localhost:1234')
response = client.generate('deepseek-r1:32b', 'Por que o céu é azul?')
print(response.response[response.response.find("</think>") + 8:])