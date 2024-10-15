import psycopg2
import json
import requests
import logging
from google.cloud import secretmanager

def get_pat_from_secret_manager(version_id="latest"):
    secrets_name = "github-search-secret"
    client = secretmanager.SecretManagerServiceClient()
    project_id = "githubtalent-434920"
    name = f"projects/{project_id}/secrets/{secrets_name}/versions/{version_id}"
    http_response = client.access_secret_version(request={"name": name})
    json_payload = http_response.payload.data.decode("UTF-8")
    return json_payload

def get_db_credentials_from_secret_manager(version_id="latest"):
    secrets_name = "database-crud-secret"
    client = secretmanager.SecretManagerServiceClient()
    project_id = "githubtalent-434920"
    name = f"projects/{project_id}/secrets/{secrets_name}/versions/{version_id}"
    http_response = client.access_secret_version(request={"name": name})
    json_payload = http_response.payload.data.decode("UTF-8")
    return json_payload #this was validated in form by older script

def call_github_search(pat: str):
    url = "https://api.github.com/search/repositories?q=pushed%3A2024-09-01T00%3A00%3A00..2024-09-01T00%3A01%3A00+is%3Apublic+-fork%3Atrue&per_page=100&page=1"
    headers = {
        "Authorization": f"Bearer {pat}",
        "Accept": "application/vnd.github.v3+json"
    }
    http_response_object = requests.get(url, headers=headers) #WARNING, this is coming in as an HTTP response object, not a JSON just yet
    github_search_results_in_json = http_response_object.json()
    return github_search_results_in_json


def select_all_from_db(db_credentials):
    exposed_host = db_credentials['DB_HOST']
    exposed_port = db_credentials['DB_PORT']
    exposed_db_name = db_credentials['DB_NAME']
    exposed_user = db_credentials['DB_USER']
    exposed_password = db_credentials['DB_PASS']

    # WARNING, THE BELOW ARE RESERVED TERMS
    try:
        attempted_db_connection = psycopg2.connect(
            host = exposed_host,
            port = exposed_port,
            database = exposed_db_name, # term of art, can't use NAME
            user = exposed_user,
            password = exposed_password
        )

        cursor = attempted_db_connection.cursor() # need explanation here
        cursor.execute("SELECT * FROM github_repos;") # puts the data in the cursor, but still need to get it out
        rows_of_data = cursor.fetchall() #we cant rely on cursor anymore, because it demands open connection

        cursor.close() # ask why this is imperative
        attempted_db_connection.close() # ask why this is imperative

        return rows_of_data # this is a list of tuples

    except Exception as reported_error:
        return f"Connecting to database, due to {reported_error}"


def get_github_repos(request):
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
    # [reporting_length,ids_array] # not using for now

    db_credentials_payload = get_db_credentials_from_secret_manager()
    db_credentials_payload_json = json.loads(db_credentials_payload)

    connection = psycopg2.connect(
        host = db_credentials_payload_json['DB_HOST'],
        port = db_credentials_payload_json['DB_PORT'],
        database = db_credentials_payload_json['DB_NAME'],  # term of art, can't use NAME
        user = db_credentials_payload_json['DB_USER'],
        password = db_credentials_payload_json['DB_PASS']
    )

    cursor = connection.cursor()
    cursor.execute("SELECT * FROM github_repos")
    results = cursor.fetchall()
    cursor.close()
    connection.close()

    return {"DATA RESULTS FROM  TABLE": results}, 200


    #full_table_data = select_all_from_db(db_credentials)
    #return full_table_data
