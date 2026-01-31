import json
import os

notebook_path = r'C:\Users\Anton\research-lab-2\content\exchange_rate_dynamics.ipynb'

with open(notebook_path, 'r', encoding='utf-8') as f:
    nb = json.load(f)

# Fix HTML import in Collaboration Hub cell
for cell in nb['cells']:
    if 'Collaboration Hub' in "".join(cell.get('source', [])):
        # Check the code cell following it
        continue
    if 'import ipywidgets as widgets' in "".join(cell.get('source', [])) and 'comment_feed' in "".join(cell.get('source', [])):
        source = "".join(cell.get('source', []))
        if 'from IPython.display import display, clear_output, Javascript, HTML' not in source:
            source = source.replace('from IPython.display import display, clear_output, Javascript', 
                                    'from IPython.display import display, clear_output, Javascript, HTML')
            cell['source'] = [line + '\n' for line in source.split('\n')]
            if cell['source'][-1] == '\n':
                cell['source'].pop()
            print("Fixed HTML import in Hub cell.")

with open(notebook_path, 'w', encoding='utf-8') as f:
    json.dump(nb, f, indent=1, ensure_ascii=False)

print('Updated notebook with missing imports.')
