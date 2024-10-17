import psycopg2
import json
import requests
import logging
from google.cloud import secretmanager
from datetime import datetime, timedelta


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
    return json_payload  # this was validated in form by older script


def call_github_search(pat: str):
    url = "https://api.github.com/search/repositories?q=pushed%3A2024-09-02T00%3A00%3A00..2024-09-02T00%3A01%3A00+is%3Apublic+-fork%3Atrue&per_page=100&page=1"
    print(f"PRINTING default url: {url}")

    db_credentials_not_json = get_db_credentials_from_secret_manager()
    db_credentials = json.loads(db_credentials_not_json)
    print("PRINTING db_credentials")
    print(db_credentials)

    # intentionally leaving potentially duplicative code in here until I prove the automation works

    try:
        connection = psycopg2.connect(
            host=db_credentials['DB_HOST'],
            port=db_credentials['DB_PORT'],
            database=db_credentials['DB_NAME'],
            user=db_credentials['DB_USER'],
            password=db_credentials['DB_PASS']
        )

        print("PRINTING connection temporarily opened!")

    except:
        print("PRINTING connection FAILED creation")

    try:
        cursor = connection.cursor()
        print("PRINTING cursor opened!")
    except Exception as e:
        print("PRINTING cursor FAILED to formed!")
        print(f"Cursor failed to form: {e}")

    try:
        cursor.execute("SELECT last_call FROM task_scheduling WHERE function_name = %s;", ("scheduled_get_repos",))
        print("PRINTING cursor executed")
    except:
        print("PRINTING cursor FAILED to execute")

    try:
        # this is the part that will take the call time out of the 3rd table
        last_call_time = cursor.fetchone()[0]
        print("PRINTING time object pulled")
        print(last_call_time)
        print(type(last_call_time))
    except:
        print("PRINTING time object FAILED to yank")

    try:
        next_call_time = last_call_time + timedelta(minutes=1)
        start_time = last_call_time.strftime("%Y-%m-%dT%H:%M:%S")
        end_time = next_call_time.strftime(
            "%Y-%m-%dT%H:%M:%S")  # we are only adding 1 minute at a time to get ~70 results per search. If we had done a full hour, it would be 5000 hits, well over the 1000 result limit set by GitHub API
        print("PRINTING conversions done!")
    except:
        print("PRINTING time conversions FAILED")

    try:
        cursor.close()
        print("PRINTING cursor successfully closed")
    except:
        print("PRINTING cursor FAILED!")

    '''
    #last_call_time_string = "2024-10-13T00:00:00Z"
    #last_call_time = datetime.strptime(last_call_time_string, "%Y-%m-%dT%H:%M:%SZ")    
    '''

    connection.close()

    try:
        url = f"https://api.github.com/search/repositories?q=pushed%3A{start_time}..{end_time}+is%3Apublic+-fork%3Atrue&per_page=100&page=1"
        print("PRINTING url successfully changed!!!!!!")
    except:
        print("PRINTING exception, url unchanged")

    headers = {
        "Authorization": f"Bearer {pat}",
        "Accept": "application/vnd.github.v3+json"
    }
    http_response_object = requests.get(url,
                                        headers=headers)  # WARNING, this is coming in as an HTTP response object, not a JSON just yet
    github_search_results_in_json = http_response_object.json()
    return github_search_results_in_json


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
        host=db_credentials_payload_json['DB_HOST'],
        port=db_credentials_payload_json['DB_PORT'],
        database=db_credentials_payload_json['DB_NAME'],  # term of art, can't use NAME
        user=db_credentials_payload_json['DB_USER'],
        password=db_credentials_payload_json['DB_PASS']
    )

    cursor = connection.cursor()

    query = """
            INSERT INTO github_repos (id, name, owner_login, owner_id, fork, description, size, stargazers_count, watchers_count, updated_at, created_at, url, db_inserted_date, db_updated_date, topics, primary_coding_language)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, %s, %s)
            ON CONFLICT (id) DO UPDATE SET 
                name = EXCLUDED.name,
                owner_login = EXCLUDED.owner_login,
                owner_id = EXCLUDED.owner_id,
                fork = EXCLUDED.fork,
                description = EXCLUDED.description,
                size = EXCLUDED.size,
                stargazers_count = EXCLUDED.stargazers_count,
                watchers_count = EXCLUDED.watchers_count,
                updated_at = EXCLUDED.updated_at,
                url = EXCLUDED.url,
                db_updated_date = CURRENT_TIMESTAMP,
                topics = EXCLUDED.topics,
                primary_coding_language = EXCLUDED.primary_coding_language
            """

    repo_data_for_insertion = []
    for repo in repos_hash:
        repo_data = (
            repo['id'],
            repo['name'],
            repo['owner']['login'],
            repo['owner']['id'],
            repo['fork'],
            repo.get('description', 'No description'),
            repo['size'],
            repo['stargazers_count'],
            repo['watchers_count'],
            repo['updated_at'],
            repo['created_at'],
            repo['html_url'],
            repo['topics'],
            repo['language']
        )
        repo_data_for_insertion.append(repo_data)

    cursor.executemany(query, repo_data_for_insertion)  # attempt insertion

    connection.commit()  # not sure why

    # begin section on pulling data, after insertions were attempted
    cursor.execute("SELECT * FROM github_repos")
    results = cursor.fetchall()
    cursor.close()
    connection.close()

    return {"DATA RESULTS FROM  TABLE": results}, 200

    # full_table_data = select_all_from_db(db_credentials)
    # return full_table_data


''' this code is likely obsolete now but keep it for debugging purposes
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
'''