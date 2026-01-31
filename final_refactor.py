import json
import os

notebook_path = r'C:\Users\Anton\research-lab-2\content\exchange_rate_dynamics.ipynb'

with open(notebook_path, 'r', encoding='utf-8') as f:
    nb = json.load(f)

# Helper to find all cells containing a snippet
def find_all_indices(nb, snippet):
    return [i for i, cell in enumerate(nb['cells']) if snippet in "".join(cell.get('source', []))]

# 1. Strip ALL instances of Platinum Map cells and piplite cells to start clean
indices_to_remove = []
indices_to_remove.extend(find_all_indices(nb, "trade-map"))
indices_to_remove.extend(find_all_indices(nb, "from ipyleaflet import Map"))
indices_to_remove.extend(find_all_indices(nb, "piplite.install"))

# Sort unique indices in reverse to pop safely
for i in sorted(list(set(indices_to_remove)), reverse=True):
    nb['cells'].pop(i)

# 2. Define the cells to inject
piplite_cell = {
    "cell_type": "code",
    "execution_count": None,
    "metadata": {},
    "outputs": [],
    "source": [
        "# JupyterLite Setup: Install dependencies in the browser runtime\n",
        "import piplite\n",
        "await piplite.install(['ipyleaflet', 'ipywidgets', 'openpyxl', 'pandas', 'matplotlib', 'numpy', 'scipy', 'dstapi'])"
    ]
}

map_md = {
    "cell_type": "markdown",
    "metadata": {},
    "source": [
        "### 14. <a id='trade-map'></a>[Platinum: Geospatial Trade Partner Map](#tableofcontents)\n"
    ]
}

map_code = {
    "cell_type": "code",
    "execution_count": None,
    "metadata": {},
    "source": [
        "from ipyleaflet import Map, Marker, FullScreenControl\n",
        "m = Map(center=(40, 20), zoom=2)\n",
        "m.add_control(FullScreenControl())\n",
        "partners = [\n",
        "    {'name': 'Danish Krone (Base)', 'location': [55.6761, 12.5683]},\n",
        "    {'name': 'Eurozone', 'location': [48.8566, 2.3522]},\n",
        "    {'name': 'USA', 'location': [38.9072, -77.0369]},\n",
        "    {'name': 'China', 'location': [39.9042, 116.4074]}\n",
        "]\n",
        "for p in partners:\n",
        "    m.add_layer(Marker(location=p['location'], draggable=False, title=p['name']))\n",
        "display(m)"
    ]
}

# 3. Inject piplite at index 1 (after title)
nb['cells'].insert(1, piplite_cell)

# 4. Locate Conclusion and inject map before it
def find_cell_index_by_content(nb, content_snippet):
    for i, cell in enumerate(nb['cells']):
        source = "".join(cell.get('source', []))
        if content_snippet in source:
            return i
    return -1

idx_conclusion = find_cell_index_by_content(nb, "Conclusion")
if idx_conclusion != -1:
    nb['cells'].insert(idx_conclusion, map_md)
    nb['cells'].insert(idx_conclusion+1, map_code)
else:
    nb['cells'].append(map_md)
    nb['cells'].append(map_code)

with open(notebook_path, 'w', encoding='utf-8') as f:
    json.dump(nb, f, indent=1, ensure_ascii=False)

print('Successfully refactored notebook structure.')
