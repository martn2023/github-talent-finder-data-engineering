import psycopg2
import random
import json
import requests
from google.cloud import secretmanager


def get_pat_from_secret_manager(version_id="latest"):
    secrets_name = "github-search-secret"
    client = secretmanager.SecretManagerServiceClient()
    project_id = "githubtalent-434920"
    name = f"projects/{project_id}/secrets/{secrets_name}/versions/{version_id}"
    response = client.access_secret_version(request={"name": name})
    payload = response.payload.data.decode("UTF-8")
    return payload

def get_db_credentials_from_secret_manager(version_id="latest"):
    secrets_name = "database-crud-secret"
    client = secretmanager.SecretManagerServiceClient()
    project_id = "githubtalent-434920"
    name = f"projects/{project_id}/secrets/{secrets_name}/versions/{version_id}"
    response = client.access_secret_version(request={"name": name})
    payload = response.payload.data.decode("UTF-8")
    return payload

def call_github_search(pat: str):
    url = "https://api.github.com/search/repositories?q=pushed%3A2024-09-01T00%3A00%3A00..2024-09-01T00%3A01%3A00+is%3Apublic+-fork%3Atrue&per_page=100&page=1"

    headers = {
        "Authorization": f"Bearer {pat}",
        "Accept": "application/vnd.github.v3+json"
    }

    http_response_object = requests.get(url, headers=headers) #WARNING, this is coming in as an HTTP response object, not a JSON just yet
    github_search_results_in_json = http_response_object.json()
    return github_search_results_in_json


def select_all_from_db(credentials):



def get_github_repos(request):
    db_credentials = get_db_credentials_from_secret_manager()


    pat_payload = get_pat_from_secret_manager()
    pat_json = json.loads(pat_payload)
    retrieved_pat = pat_json["GITHUB_PAT"]
    github_repos_json = call_github_search(retrieved_pat)

    # looping through our findings, eventually to put in DB
    ids_array = []

    repos_hash = github_repos_json['items']
    for individual_repo_info in repos_hash:
        individual_repo_id = individual_repo_info['id']
        ids_array.append(individual_repo_id)

    reporting_length = len(ids_array)
    [reporting_length,ids_array]



    #select_all_from_db = #
    return db_credentials