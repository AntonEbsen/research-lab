import pandas as pd
import os

data_dir = 'c:/Users/Anton/research-lab-2/content/data'
files = os.listdir(data_dir)

for f in files:
    try:
        if f.endswith('.csv'):
            path = os.path.join(data_dir, f)
            df = pd.read_csv(path)
            # Force object columns to strings for Arrow compatibility
            for col in df.select_dtypes(include=['object']).columns:
                df[col] = df[col].astype(str)
            new_path = path.replace('.csv', '.parquet')
            df.to_parquet(new_path, index=False)
            print(f"Converted {f} to Parquet.")
        elif f.endswith('.xlsx'):
            path = os.path.join(data_dir, f)
            df = pd.read_excel(path)
            for col in df.select_dtypes(include=['object']).columns:
                df[col] = df[col].astype(str)
            new_path = path.replace('.xlsx', '.parquet')
            df.to_parquet(new_path, index=False)
            print(f"Converted {f} to Parquet.")
    except Exception as e:
        print(f"Failed to convert {f}: {e}")
