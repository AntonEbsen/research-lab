import json
import os

notebook_path = r'C:\Users\Anton\research-lab-2\content\exchange_rate_dynamics.ipynb'

with open(notebook_path, 'r', encoding='utf-8') as f:
    nb = json.load(f)

# Helper to replace strings in code cells
def replace_in_cells(nb, old, new):
    count = 0
    for cell in nb['cells']:
        if cell['cell_type'] == 'code':
            source = "".join(cell.get('source', []))
            if old in source:
                new_source = source.replace(old, new)
                cell['source'] = [line + '\n' for line in new_source.split('\n')]
                # Remove last empty newline if split added one
                if cell['source'][-1] == '\n':
                    cell['source'].pop()
                count += 1
    return count

# Update data loading to prefer parquet
# We'll use a helper function in the notebook for this
parquet_helper = """
def load_data_resilient(filename):
    \"\"\"Attempts to load parquet, then falls back to csv/xlsx.\"\"\"
    base, _ = os.path.splitext(filename)
    parquet_path = f"data/{base}.parquet"
    csv_path = f"data/{base}.csv"
    xlsx_path = f"data/{base}.xlsx"
    
    if os.path.exists(parquet_path):
        print(f"✅ Loading optimized Parquet: {parquet_path}")
        return pd.read_parquet(parquet_path)
    elif os.path.exists(csv_path):
        print(f"⚠️ Falling back to CSV: {csv_path}")
        return pd.read_csv(csv_path)
    elif os.path.exists(xlsx_path):
        print(f"⚠️ Falling back to Excel: {xlsx_path}")
        return pd.read_excel(xlsx_path)
    else:
        raise FileNotFoundError(f"Could not find {filename} in data/ folder.")
"""

# Inject the helper into the setup cell or the first import cell
for i, cell in enumerate(nb['cells']):
    if 'import pandas as pd' in "".join(cell.get('source', [])):
        cell['source'].append("\n")
        cell['source'].append("# High-performance data loader\n")
        cell['source'].extend([line + '\n' for line in parquet_helper.strip().split('\n')])
        break

# Now replace specific loading calls
replace_in_cells(nb, "pd.read_csv('data/Danish_Inflation.csv')", "load_data_resilient('Danish_Inflation')")
replace_in_cells(nb, "pd.read_csv(\"data/Danish_Inflation.csv\")", "load_data_resilient('Danish_Inflation')")
replace_in_cells(nb, "pd.read_csv('data/Eurozone_Inflation.csv')", "load_data_resilient('Eurozone_Inflation')")
replace_in_cells(nb, "pd.read_csv(\"data/Eurozone_Inflation.csv\")", "load_data_resilient('Eurozone_Inflation')")
replace_in_cells(nb, "pd.read_excel('data/dataVA.xlsx')", "load_data_resilient('dataVA')")
replace_in_cells(nb, "pd.read_excel(\"data/dataVA.xlsx\")", "load_data_resilient('dataVA')")

with open(notebook_path, 'w', encoding='utf-8') as f:
    json.dump(nb, f, indent=1, ensure_ascii=False)

print('Successfully updated notebook with Parquet support.')
