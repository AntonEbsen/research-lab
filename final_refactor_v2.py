import json
import os

notebook_path = r'C:\Users\Anton\research-lab-2\content\exchange_rate_dynamics.ipynb'

with open(notebook_path, 'r', encoding='utf-8') as f:
    nb = json.load(f)

# Helper to find all cells containing a snippet
def find_all_indices(nb, snippet):
    return [i for i, cell in enumerate(nb['cells']) if snippet in "".join(cell.get('source', []))]

# 1. Strip ALL previous setup cells
indices_to_remove = find_all_indices(nb, "JupyterLite Setup")
indices_to_remove.extend(find_all_indices(nb, "piplite.install"))
indices_to_remove.extend(find_all_indices(nb, "import piplite"))

for i in sorted(list(set(indices_to_remove)), reverse=True):
    nb['cells'].pop(i)

# 2. Inject NEW Setup cell at index 1
setup_cell = {
    "cell_type": "code",
    "execution_count": None,
    "metadata": {"trusted": True},
    "outputs": [],
    "source": [
        "# 1. Laboratory Environment Setup\n",
        "# This cell ensures all required interactive modules are loaded.\n",
        "try:\n",
        "    import ipyleaflet\n",
        "    import ipywidgets\n",
        "    print(\"✅ Platinum modules loaded successfully.\")\n",
        "except ImportError:\n",
        "    print(\"📦 Installing missing modules (this may take 30-60 seconds)...\")\n",
        "    import piplite\n",
        "    await piplite.install(['ipyleaflet', 'ipywidgets', 'openpyxl'])\n",
        "    print(\"✅ Installation complete. Please RESTART the kernel if modules are still not found.\")\n",
        "\n",
        "# 2. Local Dependency Check\n",
        "import os\n",
        "if os.path.exists('dstapi.py'):\n",
        "    print(\"✅ Local dstapi.py detected.\")\n",
        "else:\n",
        "    print(\"⚠️ Local dstapi.py missing. API fallback may rely on pre-installed versions.\")"
    ]
}
nb['cells'].insert(1, setup_cell)

# 3. Update the main import cell (usually around index 10-15)
# Find it by looking for 'import pandas as pd'
idx_imports = -1
for i, cell in enumerate(nb['cells']):
    if 'import pandas as pd' in "".join(cell.get('source', [])):
        idx_imports = i
        break

if idx_imports != -1:
    nb['cells'][idx_imports]['source'] = [
        "# 1. Import core packages\n",
        "import pandas as pd\n",
        "import numpy as np\n",
        "import matplotlib.pyplot as plt\n",
        "import ipywidgets as widgets\n",
        "from ipywidgets import interact\n",
        "\n",
        "# 2. Autoreload for local modules\n",
        "%load_ext autoreload\n",
        "%autoreload 2\n",
        "\n",
        "# 3. Import localized API helper\n",
        "try:\n",
        "    from dstapi import DstApi\n",
        "    print(\"✅ DstApi loaded from local source.\")\n",
        "except ImportError:\n",
        "    print(\"⚠️ DstApi local import failed. Checking environment...\")\n",
        "    try:\n",
        "        from dstapi.dstapi import DstApi # Fallback for some packaging styles\n",
        "    except ImportError:\n",
        "        print(\"❌ DstApi not found. Please ensure dstapi.py is in the same folder.\")"
    ]

with open(notebook_path, 'w', encoding='utf-8') as f:
    json.dump(nb, f, indent=1, ensure_ascii=False)

print('Successfully refactored notebook with localized dependencies and resilient setup.')
