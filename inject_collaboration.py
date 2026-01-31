import json
import os

notebook_path = r'C:\Users\Anton\research-lab-2\content\exchange_rate_dynamics.ipynb'

with open(notebook_path, 'r', encoding='utf-8') as f:
    nb = json.load(f)

# Helper to find all cells containing a snippet
def find_all_indices(nb, snippet):
    return [i for i, cell in enumerate(nb['cells']) if snippet in "".join(cell.get('source', []))]

# 1. Strip previous collaboration cells to avoid duplication
indices_to_remove = find_all_indices(nb, "Collaboration Hub")
indices_to_remove.extend(find_all_indices(nb, "Collaboration Configuration"))
for i in sorted(list(set(indices_to_remove)), reverse=True):
    nb['cells'].pop(i)

# 2. Inject Configuration Cell (at the end of setup)
# Find index of setup cell injected previously
idx_setup = -1
for i, cell in enumerate(nb['cells']):
    if 'Laboratory Environment Setup' in "".join(cell.get('source', [])):
        idx_setup = i
        break

config_cell = {
    "cell_type": "code",
    "execution_count": None,
    "metadata": {"trusted": True},
    "outputs": [],
    "source": [
        "# 3. Collaboration Configuration\n",
        "# Enter your credentials here to enable Platinum features.\n",
        "# These are stored only in your browser session.\n",
        "GITHUB_PAT = '' # Leave empty to use widget input\n",
        "SUPABASE_URL = '' # e.g., 'https://your-project.supabase.co'\n",
        "SUPABASE_KEY = 'sb_publishable_90Wduiy5UCIhloX-7PPTkw_U5vq95wz'\n",
        "\n",
        "from collaboration_utils import CollaborationHub\n",
        "hub = CollaborationHub(github_token=GITHUB_PAT, supabase_url=SUPABASE_URL, supabase_key=SUPABASE_KEY)\n",
        "print(\"✅ Collaboration Hub initialized.\")"
    ]
}

if idx_setup != -1:
    nb['cells'].insert(idx_setup + 1, config_cell)
else:
    nb['cells'].insert(1, config_cell)

# 3. Inject Collaboration Hub (at the very end)
hub_md = {
    "cell_type": "markdown",
    "metadata": {},
    "source": [
        "## 15. <a id='collaboration'></a>[Platinum: Collaboration Hub](#tableofcontents)\n",
        "\n",
        "Use this section to share your research or leave a legacy. \n",
        "\n",
        "> [!NOTE]\n",
        "> **Gist Export**: Saves the current state of this notebook to your GitHub account.\n",
        "> **Live Commentary**: Share insights with other visitors using the Supabase-backed feed."
    ]
}

hub_code = {
    "cell_type": "code",
    "execution_count": None,
    "metadata": {"trusted": True},
    "outputs": [],
    "source": [
        "import ipywidgets as widgets\n",
        "from IPython.display import display, clear_output, Javascript\n",
        "\n",
        "# --- Gist Export UI ---\n",
        "token_input = widgets.Password(description='GitHub PAT:', placeholder='Enter PAT to enable export')\n",
        "save_button = widgets.Button(description='Save to Gist', button_style='primary', icon='github')\n",
        "gist_output = widgets.Output()\n",
        "\n",
        "def on_save_clicked(b):\n",
        "    with gist_output:\n",
        "        clear_output()\n",
        "        if token_input.value:\n",
        "            hub.github_token = token_input.value\n",
        "        \n",
        "        if not hub.github_token:\n",
        "            print(\"❌ Please provide a GitHub Personal Access Token.\")\n",
        "            return\n",
        "            \n",
        "        print(\"⏳ Exporting to Gist...\")\n",
        "        # In JupyterLite, we can't easily get the current cell content, \n",
        "        # but we can try to prompt the user or use a pre-set version.\n",
        "        # For now, we'll export the file content if possible.\n",
        "        try:\n",
        "            with open('exchange_rate_dynamics.ipynb', 'r') as f:\n",
        "                nb_data = json.load(f)\n",
        "            res = hub.save_to_gist(nb_data)\n",
        "            if 'url' in res:\n",
        "                print(f\"✅ Successfully exported! View here: {res['url']}\")\n",
        "            else:\n",
        "                print(f\"❌ Error: {res['error']}\")\n",
        "        except Exception as e:\n",
        "            print(f\"❌ Error reading notebook: {e}\")\n",
        "\n",
        "save_button.on_click(on_save_clicked)\n",
        "\n",
        "# --- Commentary UI ---\n",
        "name_input = widgets.Text(description='Name:', placeholder='Your name')\n",
        "comment_input = widgets.Textarea(description='Comment:', placeholder='Enter your analysis...')\n",
        "post_button = widgets.Button(description='Post Comment', button_style='success')\n",
        "comment_feed = widgets.Output()\n",
        "\n",
        "def refresh_comments(b=None):\n",
        "    with comment_feed:\n",
        "        clear_output()\n",
        "        comments = hub.fetch_comments()\n",
        "        if not comments:\n",
        "            print(\"No comments yet. Be the first!\")\n",
        "        for c in comments:\n",
        "            display(HTML(f\"<b>{c['user_name']}</b> <small>({c['created_at'][:10]})</small><br/>{c['comment']}<hr/>\"))\n",
        "\n",
        "def on_post_clicked(b):\n",
        "    if not name_input.value or not comment_input.value:\n",
        "        return\n",
        "    res = hub.post_comment(name_input.value, comment_input.value)\n",
        "    if 'success' in res:\n",
        "        comment_input.value = ''\n",
        "        refresh_comments()\n",
        "    else:\n",
        "        with comment_feed: print(f\"Error: {res.get('error')}\")\n",
        "\n",
        "post_button.on_click(on_post_clicked)\n",
        "\n",
        "# Display Layout\n",
        "display(HTML(\"<h3>📤 Export Research</h3>\"))\n",
        "display(widgets.HBox([token_input, save_button]))\n",
        "display(gist_output)\n",
        "display(HTML(\"<br/><h3>💬 Live Commentary</h3>\"))\n",
        "display(widgets.VBox([name_input, comment_input, post_button]))\n",
        "display(comment_feed)\n",
        "refresh_comments()"
    ]
}

nb['cells'].append(hub_md)
nb['cells'].append(hub_code)

with open(notebook_path, 'w', encoding='utf-8') as f:
    json.dump(nb, f, indent=1, ensure_ascii=False)

print('Successfully injected Collaboration Hub.')
