import psycopg2
import json
import requests
import logging
from google.cloud import secretmanager


# keep this code
def get_pat_from_secret_manager(version_id="latest"):
    print("STARTING get_pat_from_secret_manager")
    secrets_name = "github-search-secret"
    client = secretmanager.SecretManagerServiceClient()
    project_id = "githubtalent-434920"
    name = f"projects/{project_id}/secrets/{secrets_name}/versions/{version_id}"
    http_response = client.access_secret_version(request={"name": name})
    json_payload = http_response.payload.data.decode("UTF-8")
    return json_payload


# keep this code
def get_db_credentials_from_secret_manager(version_id="latest"):
    print("STARTING get_db_credentials_from_secret_manager")
    secrets_name = "database-crud-secret"
    client = secretmanager.SecretManagerServiceClient()
    project_id = "githubtalent-434920"
    name = f"projects/{project_id}/secrets/{secrets_name}/versions/{version_id}"
    http_response = client.access_secret_version(request={"name": name})
    json_payload = http_response.payload.data.decode("UTF-8")
    return json_payload  # this was validated in form by older script


def select_all_repos_from_db(db_credentials):
    print("STARTING select_all_repos_from_db")
    exposed_host = db_credentials['DB_HOST']
    exposed_port = db_credentials['DB_PORT']
    exposed_db_name = db_credentials['DB_NAME']
    exposed_user = db_credentials['DB_USER']
    exposed_password = db_credentials['DB_PASS']

    # WARNING, THE BELOW ARE RESERVED TERMS
    try:
        attempted_db_connection = psycopg2.connect(
            host=exposed_host,
            port=exposed_port,
            database=exposed_db_name,  # term of art, can't use NAME
            user=exposed_user,
            password=exposed_password
        )

        cursor = attempted_db_connection.cursor()  # need explanation here
        cursor.execute("SELECT * FROM github_repos;")  # puts the data in the cursor, but still need to get it out
        rows_of_data = cursor.fetchall()  # we cant rely on cursor anymore, because it demands open connection

        cursor.close()  # ask why this is imperative
        attempted_db_connection.close()  # ask why this is imperative

        return rows_of_data  # this is a list of tuples

    except Exception as reported_error:
        return f"Connecting to database, due to {reported_error}"


def get_recently_updated_owner_ids():
    print("STARTING get_recently_updated_owner_ids")

    db_credentials_payload = get_db_credentials_from_secret_manager()
    db_credentials_payload_json = json.loads(db_credentials_payload)

    connection = psycopg2.connect(
        host=db_credentials_payload_json['DB_HOST'],
        port=db_credentials_payload_json['DB_PORT'],
        database=db_credentials_payload_json['DB_NAME'],  # term of art, can't use NAME
        user=db_credentials_payload_json['DB_USER'],
        password=db_credentials_payload_json['DB_PASS']
    )
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM github_repos")
    repo_results = cursor.fetchall()
    cursor.close()
    connection.close()

    return repo_results
    return {}


# need to change this code so it calls for profiles/owners instead of the repos
def call_github_search_owners(pat: str):
    print("INCORRECTLY SEARCHING REPOS INSTEAD OF OWNERS")
    url = "https://api.github.com/search/repositories?q=pushed%3A2024-09-01T00%3A00%3A00..2024-09-01T00%3A01%3A00+is%3Apublic+-fork%3Atrue&per_page=100&page=1"  # this is wrong, it should hit owners
    headers = {
        "Authorization": f"Bearer {pat}",
        "Accept": "application/vnd.github.v3+json"
    }
    http_response_object = requests.get(url,
                                        headers=headers)  # WARNING, this is coming in as an HTTP response object, not a JSON just yet
    github_search_results_in_json = http_response_object.json()
    return github_search_results_in_json


# Fairly sure this should stay, because it's a general entry into the DATABASE, not a specific TABLE


# new maestro
def update_github_owners(request):
    print("STARTING update_github_owners")

    pat_payload = get_pat_from_secret_manager()
    print("PRINTING pat_payload: ", pat_payload)

    pat_json = json.loads(pat_payload)  # initializes a dictionary
    print("PRINTING pat_payload in JSON: ", pat_json)

    retrieved_pat = pat_json["GITHUB_PAT"]  # RETRIEVES value from dictionary entry GITHUB_PAT
    print("PRINTING retrieved_pat in string format: ", retrieved_pat)

    recently_updated_owner_ids = get_recently_updated_owner_ids()
    print("PRINTING recently_updated_owner_ids")
    print(recently_updated_owner_ids)

    '''synatically correct but strategically redundant. we need to pull repos this fROM SQL and pull OWNERS from github
    github_repos_json = call_github_search(retrieved_pat) #using the stringed PAT key, can we call the github search?
    print("ATTEMPTED github_repos_json")
    print(github_repos_json)
    '''

    return recently_updated_owner_ids
    return {"DATA RESULTS FROM TABLE": "No data"}, 200
