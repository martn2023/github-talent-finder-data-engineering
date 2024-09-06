import os # need it for saving files
import json # required for exporting json info
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

    fetched_repos_array = []
    page_number = 1
    fetched_repos_array_per_page = 100  # Number of fetched_repos_arrayitories per page

    while len(fetched_repos_array) < max_results:
        print(f"loop iteration starting, and this is LENGTH OF REPOS: {len(fetched_repos_array)} vs max {max_results} ")

        # GitHub Search API for fetched_repos_arrayitories
        params = {
            'q': query,  # Combined query parameters
            'per_page': fetched_repos_array_per_page,  # per_page is a term set by GitHub's team, fetched_repos_array_per_page is my custom term
            'page': page_number # page_number came from me, and page came from GitHub Search API's design
        }

        response = requests.get(f"{BASE_URL}/search/repositories", headers=headers, params=params)
        print(f"url created: {response.url}")

        if response.status_code == 200:
            print("some response found!")
            result = response.json()

            total_count = result.get('total_count', 0)
            print(f"Total number of repositories: {total_count}")

            items = result.get('items', [])
            fetched_repos_array.extend(items)

            if len(fetched_repos_array) >= max_results:
                # Trim the list to max_results and stop fetching
                fetched_repos_array = fetched_repos_array[:max_results]
                break

            # Check if we've reached the end (fewer results than requested per page)
            if len(items) < fetched_repos_array_per_page:
                break
        else:
            print(f"Failed to fetch fetched_repos_array: {response.status_code}, {response.text}")
            break

        page_number += 1

    return fetched_repos_array


filtered_fetched_repos_array = get_filtered_repos(max_results=500)

'''
if filtered_fetched_repos_array:
    print(f"filtered_fetched_repos_array LENGTH: {len(filtered_fetched_repos_array)}")
    for single_repo in filtered_fetched_repos_array:
        repo_name = single_repo['name']
        owner_login = single_repo['owner']['login']
        stars = single_repo['stargazers_count']
        updated_at = single_repo['updated_at']
        print(f"Repository: {repo_name}, Author: {owner_login}, Stars: {stars}, Updated At: {updated_at}")
else:
    print("never saw filtered fetched_repos_array")
'''

def save_to_file(data, directory="sample_data_pulls_github_api", filename="most_recent_pull.json"):
    if not os.path.exists(directory):
        os.makedirs(directory) # Create directory if it does not exist

    filepath = os.path.join(directory, filename)

    with open(filepath, 'w') as json_file:
        json.dump(data, json_file, indent=4)

    print(f"JSON successfully saved to {filepath}")

if filtered_fetched_repos_array:
    print(f"ENUM ATTEMPT filtered_fetched_repos_array LENGTH: {len(filtered_fetched_repos_array)}")

    '''
    for index_pos, single_repo in enumerate(filtered_fetched_repos_array):
        repo_name = single_repo['name']
        owner_login = single_repo['owner']['login']
        stars = single_repo['stargazers_count']
        updated_at = single_repo['updated_at']
        print(f"Index_pos{index_pos} Repository: {repo_name}, Author: {owner_login}, Stars: {stars}, Updated At: {updated_at}")
    '''

    save_to_file(filtered_fetched_repos_array)

else:
    print("never saw filtered fetched_repos_array")
