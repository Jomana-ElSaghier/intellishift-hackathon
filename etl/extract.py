import pandas as pd

def extract_data(path):

    print("Reading CSV File...")

    df = pd.read_csv(path)

    print(f"Rows Loaded : {len(df)}")

    return df