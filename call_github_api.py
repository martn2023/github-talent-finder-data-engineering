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
    push_time_range = 'pushed:2024-09-01T00:00:00..2024-09-01T00:10:00'
    visibility = 'is:public'
    no_forks = '-fork:true'

    # Combine query parameters
    query = f'{push_time_range} {visibility} {no_forks}'

    repos = []
    page = 1
    repos_per_page = 100  # Number of repositories per page

    while len(repos) < max_results:
        print(f"loop iteration starting, and this is LENGTH OF REPOS: {len(repos)} vs max {max_results} ")

        # GitHub Search API for repositories
        params = {
            'q': query,  # Combined query parameters
            'per_page': repos_per_page,  # per_page is a term set by GitHub's team, repos_per_page is my custom term
            'page': page
        }

        response = requests.get(f"{BASE_URL}/search/repositories", headers=headers, params=params)
        print(f"url created: {response.url}")

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


filtered_repos = get_filtered_repos(max_results=500)

if filtered_repos:
    for single_repo in filtered_repos:
        repo_name = single_repo['name']
        owner_login = single_repo['owner']['login']
        stars = single_repo['stargazers_count']
        updated_at = single_repo['updated_at']
        print(f"Repository: {repo_name}, Author: {owner_login}, Stars: {stars}, Updated At: {updated_at}")
else:
    print("never saw filtered repos")
