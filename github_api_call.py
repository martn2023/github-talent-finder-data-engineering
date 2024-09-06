import json
import os
from config import github_pat  # imported as string format
import requests

GITHUB_TOKEN = github_pat

BASE_URL = "https://api.github.com"
headers = {
    "Authorization": f"Bearer {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}


def get_filtered_repos(max_results=10000):
    """Fetch repositories updated within a specific time window with various filters, capped at max_results"""

    # Search query parameters
    query = (
        'pushed:2024-09-01T00:00:00..2024-09-01T00:01:00'  # Time window
        '+fork:false'  # Exclude forks
        '+stars:1..10'  # Star count between 1 and 10
        '+topic:supervised-learning'  # Tagged with 'supervised-learning'
        '+archived:false'  # Exclude archived repos
        '+is:public'  # Only public repositories
    )

    repos = []
    page = 1
    per_page = 100  # Number of repositories per page

    while len(repos) < max_results:
        # GitHub search API for repositories
        url = f"{BASE_URL}/search/repositories?q={query}&per_page={per_page}&page={page}"

        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            result = response.json()
            items = result.get('items', [])
            repos.extend(items)

            # Check if we've reached the end (fewer results than requested per page)
            if len(items) < per_page:
                break
        else:
            print(f"Failed to fetch repos: {response.status_code}, {response.text}")
            break

        page += 1

        # Stop if we reach the max_results limit
        if len(repos) >= max_results:
            repos = repos[:max_results]  # Trim to max_results if exceeded
            break

    return repos


def save_to_json(data):
    """Save the fetched repositories to a JSON file in the specified folder"""
    directory = "sample_data_pulls_github_api"
    if not os.path.exists(directory):
        os.makedirs(directory)  # Create directory if it doesn't exist
    file_path = os.path.join(directory, 'repos_results.json')

    with open(file_path, 'w') as f:
        json.dump(data, f, indent=4)
    print(f"Results saved to {file_path}")


# Fetch filtered repositories with a maximum of 10,000 results
filtered_repos = get_filtered_repos(max_results=10000)

if filtered_repos:
    save_to_json(filtered_repos)
    for single_repo in filtered_repos:
        print(
            f"Repository: {single_repo['name']}, Stars: {single_repo['stargazers_count']}, Updated At: {single_repo['updated_at']}")
