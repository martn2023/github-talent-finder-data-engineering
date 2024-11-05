import json
import logging
import os
from datetime import timedelta
from typing import Any

import psycopg2
import requests
from google.cloud import secretmanager

# Configurations
PROJECT_ID = os.getenv("PROJECT_ID", "githubtalent-434920")
GITHUB_SECRET_NAME = os.getenv("GITHUB_SECRET_NAME", "github-search-secret")
DB_SECRET_NAME = os.getenv("DB_SECRET_NAME", "database-crud-secret")

# Logger setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_secret(secret_name: str, version_id: str = "latest") -> str:
    """Retrieve a secret from Google Cloud Secret Manager."""
    client = secretmanager.SecretManagerServiceClient()
    name = f"projects/{PROJECT_ID}/secrets/{secret_name}/versions/{version_id}"
    response = client.access_secret_version(request={"name": name})
    return response.payload.data.decode("UTF-8")


def get_db_credentials() -> dict:
    """Get database credentials from Secret Manager."""
    db_credentials_not_json = get_secret(DB_SECRET_NAME)
    return json.loads(db_credentials_not_json)


def create_db_connection() -> Any:
    """Create a database connection using credentials stored in Secret Manager."""
    db_credentials = get_db_credentials()
    try:
        connection = psycopg2.connect(
            host=db_credentials['DB_HOST'],
            port=db_credentials['DB_PORT'],
            database=db_credentials['DB_NAME'],
            user=db_credentials['DB_USER'],
            password=db_credentials['DB_PASS']
        )
        logger.info("Connection successfully created")
        return connection
    except Exception as e:
        logger.error(f"Failed to create connection: {e}")
        raise


def update_task_schedule(cursor: Any, next_call_time: str) -> None:
    """Update the last call time for the scheduled task."""
    cursor.execute(
        "UPDATE task_scheduling SET last_call = %s WHERE function_name = %s;",
        (next_call_time, "scheduled_get_repos")
    )


def call_github_search(pat, start_time, end_time):
    """Call GitHub search API with the given PAT and time window."""
    url = f"https://api.github.com/search/repositories?q=pushed%3A{start_time}..{end_time}+is%3Apublic+-fork%3Atrue&per_page=100&page=1"
    headers = {
        "Authorization": f"Bearer {pat}",
        "Accept": "application/vnd.github.v3+json"
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()  # raise an exception for HTTP error responses
    return response.json()


def get_github_repos(request):
    try:
        pat_json = json.loads(get_secret(GITHUB_SECRET_NAME))
        retrieved_pat = pat_json["GITHUB_PAT"]

        connection = create_db_connection()
        cursor = connection.cursor()

        cursor.execute("SELECT last_call FROM task_scheduling WHERE function_name = %s;", ("scheduled_get_repos",))
        current_call_time = cursor.fetchone()[0]
        current_end_time = current_call_time + timedelta(minutes=1)  # Adjust as necessary
        start_time = current_call_time.strftime("%Y-%m-%dT%H:%M:%S")
        end_time = current_end_time.strftime("%Y-%m-%dT%H:%M:%S")
        next_call_time = current_call_time + timedelta(hours=1)  # Adjust as necessary

        update_task_schedule(cursor, next_call_time)
        connection.commit()

        github_repos_json = call_github_search(retrieved_pat, start_time, end_time)
        repos_hash = github_repos_json.get('items', [])

        repo_data_for_insertion = [
            (
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
                json.dumps(repo.get('topics', [])),  # Save as JSON string
                repo.get('language', 'Unknown')  # Adding a fallback value
            )
            for repo in repos_hash
        ]

        insert_query = """
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
        cursor.executemany(insert_query, repo_data_for_insertion)
        connection.commit()

        cursor.execute("SELECT * FROM github_repos")
        results = cursor.fetchall()
        cursor.close()
        connection.close()

        return {"DATA RESULTS FROM TABLE": results}, 200

    except Exception as e:
        logger.error(f"Error in get_github_repos: {e}")
        return {"Error": str(e)}, 500