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


def get_filtered_repos(max_results=500):
    print("get_filtered_repos started", "max results:", max_results)


    # Search query parameters
    push_time_range = 'pushed:2024-09-01T00:00:00..2024-09-01T00:01:00'
    visibility = 'is:public'

    # Combine query parameters
    query = f'{push_time_range} {visibility}'

    repos = []
    page = 1
    repos_per_page = 100  # Number of repositories per page

    while len(repos) < max_results:
        print("loop iteration starting")
        # GitHub search API for repositories
        url = f"{BASE_URL}/search/repositories?q={query}&repos_per_page={repos_per_page}&page={page}"
        print(f"url created: {url}")

        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            print("some response found!")
            result = response.json()

            total_count = result.get('total_count', 0)
            print(f"Total number of repositories: {total_count}")

            items = result.get('items', [])
            repos.extend(items)

            if len(repos) >= max_results:
                # Trim the list to max_results and stop fetching
                repos = repos[:max_results]
                break

            # Check if we've reached the end (fewer results than requested per page)
            if len(items) < repos_per_page:
                break
        else:
            print(f"Failed to fetch repos: {response.status_code}, {response.text}")
            break

        page += 1

    return repos


'''
def save_to_json(data):
    """Save the fetched repositories to a JSON file in the specified folder"""
    directory = "sample_data_pulls_github_api"
    if not os.path.exists(directory):
        os.makedirs(directory)  # Create directory if it doesn't exist
    file_path = os.path.join(directory, 'repos_results.json')

    with open(file_path, 'w') as f:
        json.dump(data, f, indent=4)
    print(f"Results saved to {file_path}")

'''

filtered_repos = get_filtered_repos(max_results=500)

if filtered_repos:
    #save_to_json(filtered_repos)
    for single_repo in filtered_repos:
        print(
            f"Repository: {single_repo['name']}, Stars: {single_repo['stargazers_count']}, Updated At: {single_repo['updated_at']}")

else:
    print("never saw filtered repos")