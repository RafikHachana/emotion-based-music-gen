import pandas as pd

df = pd.read_csv("matched.csv")

result = df.drop_duplicates(subset=['track_id'])

print(result.head)

result.to_csv("matched_distinct.csv")