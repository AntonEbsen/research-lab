import json
import requests
import base64
from IPython.display import display, HTML

class CollaborationHub:
    def __init__(self, github_token=None, supabase_url=None, supabase_key=None):
        self.github_token = github_token
        self.supabase_url = supabase_url
        self.supabase_key = supabase_key
        self.gist_id = None

    def save_to_gist(self, notebook_data, filename="Research_Lab_Analysis.ipynb"):
        """Saves the current notebook content to a GitHub Gist."""
        if not self.github_token:
            return {"error": "GitHub PAT missing. Please provide a token in the config."}

        headers = {
            "Authorization": f"token {self.github_token}",
            "Accept": "application/vnd.github.v3+json"
        }
        
        payload = {
            "description": "Ebsen Research Lab - Exported Analysis",
            "public": False,
            "files": {
                filename: {
                    "content": json.dumps(notebook_data, indent=2)
                }
            }
        }

        response = requests.post("https://api.github.com/gists", headers=headers, json=payload)
        
        if response.status_code == 201:
            self.gist_id = response.json()['id']
            return {"url": response.json()['html_url']}
        else:
            return {"error": f"Failed to save Gist: {response.status_code} - {response.text}"}

    def fetch_comments(self, notebook_id="exchange_rate_dynamics"):
        """Fetches comments from Supabase for the given notebook."""
        if not self.supabase_url or not self.supabase_key:
            return []

        headers = {
            "apikey": self.supabase_key,
            "Authorization": f"Bearer {self.supabase_key}"
        }
        
        params = {
            "notebook_id": f"eq.{notebook_id}",
            "order": "created_at.desc"
        }

        url = f"{self.supabase_url}/rest/v1/lab_comments"
        
        try:
            response = requests.get(url, headers=headers, params=params)
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Error fetching comments: {response.status_code}")
                return []
        except Exception as e:
            print(f"Connection error: {e}")
            return []

    def post_comment(self, user_name, comment_text, notebook_id="exchange_rate_dynamics"):
        """Posts a new comment to Supabase."""
        if not self.supabase_url or not self.supabase_key:
            return {"error": "Supabase configuration missing."}

        headers = {
            "apikey": self.supabase_key,
            "Authorization": f"Bearer {self.supabase_key}",
            "Content-Type": "application/json",
            "Prefer": "return=minimal"
        }
        
        data = {
            "notebook_id": notebook_id,
            "user_name": user_name,
            "comment": comment_text
        }

        url = f"{self.supabase_url}/rest/v1/lab_comments"
        
        try:
            response = requests.post(url, headers=headers, json=data)
            if response.status_code in [201, 204]:
                return {"success": True}
            else:
                return {"error": f"Failed to post: {response.status_code}"}
        except Exception as e:
            return {"error": str(e)}
