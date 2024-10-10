import psycopg2
import json
import requests
import logging
from google.cloud import secretmanager


# keep this code
def get_pat_from_secret_manager(version_id="latest"):
    secrets_name = "github-search-secret"
    client = secretmanager.SecretManagerServiceClient()
    project_id = "githubtalent-434920"
    name = f"projects/{project_id}/secrets/{secrets_name}/versions/{version_id}"
    http_response = client.access_secret_version(request={"name": name})
    json_payload = http_response.payload.data.decode("UTF-8")
    return json_payload


# keep this code
def get_db_credentials_from_secret_manager(version_id="latest"):
    secrets_name = "database-crud-secret"
    client = secretmanager.SecretManagerServiceClient()
    project_id = "githubtalent-434920"
    name = f"projects/{project_id}/secrets/{secrets_name}/versions/{version_id}"
    http_response = client.access_secret_version(request={"name": name})
    json_payload = http_response.payload.data.decode("UTF-8")
    return json_payload  # this was validated in form by older script


def get_recently_updated_owner_ids(request):
    # Initialize an empty set to store unique owner IDs
    recently_updated_owner_ids = set()

    # Get database credentials
    db_credentials = get_db_credentials_from_secret_manager()

    # Connect to the database
    connection = psycopg2.connect(
        host=db_credentials['DB_HOST'],
        port=db_credentials['DB_PORT'],
        database=db_credentials['DB_NAME'],
        user=db_credentials['DB_USER'],
        password=db_credentials['DB_PASS']
    )

    try:
        cursor = connection.cursor()

        # Query to find all repos updated in the last hour
        query = """
            SELECT owner_id 
            FROM github_repos 
            WHERE updated_at >= NOW() - INTERVAL '1 HOUR';
        """

        cursor.execute(query)
        updated_repos = cursor.fetchall()

        # Populate the set with owner_id values from the query results
        for row in updated_repos:
            recently_updated_owner_ids.add(row[0])  # row[0] is the owner_id

        cursor.close()
        connection.close()

        # Return the set as JSON for testing purposes
        return {"recently_updated_owner_ids": list(recently_updated_owner_ids)}, 200

    except Exception as e:
        if connection:
            connection.close()
        return {"error": str(e)}, 500


def get_recent_profile_ids():
    # Get DB credentials
    db_credentials = get_db_credentials_from_secret_manager()

    # Connect to the database
    connection = psycopg2.connect(
        host=db_credentials['DB_HOST'],
        port=db_credentials['DB_PORT'],
        database=db_credentials['DB_NAME'],
        user=db_credentials['DB_USER'],
        password=db_credentials['DB_PASS']
    )

    try:
        cursor = connection.cursor()

        # SQL query to get distinct owner_logins of repos updated in the last hour
        query = """
            SELECT DISTINCT owner_login 
            FROM github_repos 
            WHERE updated_at >= NOW() - INTERVAL '1 HOUR';
        """

        cursor.execute(query)
        recent_profiles = cursor.fetchall()

        # Convert list of tuples to a set of unique profile IDs
        profile_ids_set = {row[0] for row in recent_profiles}

        cursor.close()
        connection.close()

        return profile_ids_set

    except Exception as e:
        if connection:
            connection.close()
        return f"Error querying database: {e}"


# need to change this code so it calls for profiles/owners instead of the repos
def call_github_search(pat: str):
    url = "https://api.github.com/search/repositories?q=pushed%3A2024-09-01T00%3A00%3A00..2024-09-01T00%3A01%3A00+is%3Apublic+-fork%3Atrue&per_page=100&page=1"
    headers = {
        "Authorization": f"Bearer {pat}",
        "Accept": "application/vnd.github.v3+json"
    }
    http_response_object = requests.get(url,
                                        headers=headers)  # WARNING, this is coming in as an HTTP response object, not a JSON just yet
    github_search_results_in_json = http_response_object.json()
    return github_search_results_in_json


# Fairly sure this should stay, because it's a general entry into the DATABASE, not a specific TABLE
def select_all_from_db(db_credentials):
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


# new maestro
def update_github_owners(request):
    print("STARTING update_github_owners")

    pat_payload = get_pat_from_secret_manager()
    print("PRINTING pat_payload: ", pat_payload)

    pat_json = json.loads(pat_payload)  # initializes a dictionary
    print("PRINTING pat_payload in JSON: ", pat_json)

    retrieved_pat = pat_json["GITHUB_PAT"]  # RETRIEVES value from dictionary entry GITHUB_PAT
    print("PRINTING retrieved_pat in string format: ")
    print(retrieved_pat)

    github_repos_json = call_github_search(retrieved_pat)  # using the stringed PAT key, can we call the github search?
    print("ATTEMPTED github_repos_json")
    print(github_repos_json)

    '''
    db_credentials_payload = get_db_credentials_from_secret_manager()
    db_credentials_payload_json = json.loads(db_credentials_payload)

    connection = psycopg2.connect(
        host = db_credentials_payload_json['DB_HOST'],
        port = db_credentials_payload_json['DB_PORT'],
        database = db_credentials_payload_json['DB_NAME'],  # term of art, can't use NAME
        user = db_credentials_payload_json['DB_USER'],
        password = db_credentials_payload_json['DB_PASS']
    )

    '''

    return {"DATA RESULTS FROM TABLE": "No data"}, 200
