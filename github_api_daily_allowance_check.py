import requests
from config import github_pat  # make sure this contains your GitHub token

GITHUB_TOKEN = github_pat
BASE_URL = "https://api.github.com"
headers = {
    "Authorization": f"Bearer {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}


def check_rate_limit():
    url = f"{BASE_URL}/rate_limit"
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        core_limit = data['rate']['limit']
        core_remaining = data['rate']['remaining']
        core_reset = data['rate']['reset']

        print(f"API Limit: {core_limit}")
        print(f"Remaining Requests: {core_remaining}")
        print(f"Rate Limit Resets At (UNIX timestamp): {core_reset}")
    else:
        print(f"Error: {response.status_code}")


check_rate_limit()
