import pandas as pd

df = pd.read_csv('data.csv')

sampled_df = df.sample(n=1000, random_state=42)

sampled_df.to_json('reference_data_file.json', orient='records', lines=False)
