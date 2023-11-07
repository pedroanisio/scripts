import os
## needed to work with shared folder
import sys
from pathlib import Path

import requests

# Add the 'shared' directory to the sys.path
current_dir = Path(__file__).parent
shared_dir = current_dir.parent / 'shared'
sys.path.append(str(shared_dir))
## 
from script_env_loader import ScriptEnvLoader

# Load environment variables
script_name = os.path.basename(__file__)
ScriptEnvLoader.load_env(script_name)

# Now you can use os.getenv to access your environment variables
username = os.getenv('GITHUB_USERNAME')
token = os.getenv('GITHUB_TOKEN')


## URL to get github token:
## https://github.com/settings/apps

def get_github_repos(username: str, token: str) -> str:
    """
    Fetches a list of all repositories (including private) for the given GitHub username
    and formats them in Markdown for a wiki page.

    Args:
        username (str): GitHub username.
        token (str): Personal access token for GitHub API.

    Returns:
        str: A string in Markdown format listing the repositories and their descriptions.
    """
    repos = []
    url = f"https://api.github.com/users/{username}/repos"
    headers = {'Authorization': f'token {token}'}

    while url:
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()

            for repo in response.json():
                repo_name = repo['name']
                repo_description = repo['description'] or 'No description'
                repos.append(f"- [{repo_name}](https://github.com/{username}/{repo_name}): {repo_description}")
            
            if 'next' in response.links:
                url = response.links['next']['url']
            else:
                url = None
        except requests.exceptions.HTTPError as errh:
            return f"Http Error: {errh}"
        except requests.exceptions.ConnectionError as errc:
            return f"Error Connecting: {errc}"
        except requests.exceptions.Timeout as errt:
            return f"Timeout Error: {errt}"
        except requests.exceptions.RequestException as err:
            return f"Oops: Something Else: {err}"

    return '\n'.join(repos)

markdown_output = get_github_repos(username, token)
print(markdown_output)
