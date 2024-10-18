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
    repo_results = cursor.fetchall()  # this returns an array, not a JSON
    cursor.close()
    connection.close()

    unique_profile_ids = set()

    for repo_result in repo_results:
        profile_id = str(repo_result[
                             13])  # fragile code that assumes ordering of columns, where profile id is the 14th column and in integer format so we convert to string
        # github_username = repo_result[2] # using username and not the stable userID because github's API design
        unique_profile_ids.add(profile_id)

    unique_profile_ids = list(unique_profile_ids)
    return unique_profile_ids


# need to change this code so it calls for profiles/owners instead of the repos
def call_github_search_owners(pat: str, github_profile_number: str):
    print("NOW FINDING PROFILE INFO BY USERNAME")
    url = "https://api.github.com/user/" + str(github_profile_number)
    headers = {
        "Authorization": f"Bearer {pat}",
        "Accept": "application/vnd.github.v3+json"
    }
    http_response_object = requests.get(url,
                                        headers=headers)  # WARNING, this is coming in as an HTTP response object, not a JSON just yet
    github_search_results_in_json = http_response_object.json()
    return github_search_results_in_json


# Fairly sure this should stay, because it's a general entry into the DATABASE, not a specific TABLE

def insert_profiles_into_database(profile_info_pulled: list, pat: str):
    db_credentials_payload = get_db_credentials_from_secret_manager()
    db_credentials_payload_json = json.loads(db_credentials_payload)

    # 
    connection = psycopg2.connect(
        host=db_credentials_payload_json['DB_HOST'],
        port=db_credentials_payload_json['DB_PORT'],
        database=db_credentials_payload_json['DB_NAME'],  # term of art, can't use NAME
        user=db_credentials_payload_json['DB_USER'],
        password=db_credentials_payload_json['DB_PASS']
    )

    cursor = connection.cursor()

    # unconditional overwrites deliberately selected given the size of database and size of data in question
    # notice that there is no code here for timestamping updates, because that's taken care of by the database design
    insertion_query = """
        INSERT INTO github_owners (
            id, login, type, name, company, email, bio, followers, 
            following, html_url, blog, twitter_username, updated_at
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (id) DO UPDATE SET
            login = EXCLUDED.login,
            type = EXCLUDED.type,
            name = EXCLUDED.name,
            company = EXCLUDED.company,
            email = EXCLUDED.email,
            bio = EXCLUDED.bio,
            followers = EXCLUDED.followers,
            following = EXCLUDED.following,
            html_url = EXCLUDED.html_url,
            blog = EXCLUDED.blog,
            twitter_username = EXCLUDED.twitter_username,
            updated_at = EXCLUDED.updated_at;
        """

    # the imported data should be in list form

    profile_data_list = []
    for individual_profile_id in profile_info_pulled:
        profile_info = call_github_search_owners(pat, individual_profile_id)

        profile_data = (
            profile_info.get('id'),
            profile_info.get('login'),
            profile_info.get('type'),
            profile_info.get('name'),
            profile_info.get('company'),
            profile_info.get('email'),
            profile_info.get('bio'),
            profile_info.get('followers'),
            profile_info.get('following'),
            profile_info.get('html_url'),
            profile_info.get('blog'),
            profile_info.get('twitter_username'),
            profile_info.get('updated_at')
        )

        profile_data_list.append(profile_data)

    cursor.executemany(insertion_query, profile_data_list)
    connection.commit()

    return None


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
    insert_profiles_into_database(recently_updated_owner_ids, retrieved_pat)  # no need for a returned value

    return recently_updated_owner_ids

