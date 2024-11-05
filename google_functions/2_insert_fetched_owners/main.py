import psycopg2
import os
import json
import requests
import logging
from google.cloud import secretmanager

# Configurations
PROJECT_ID = os.getenv("PROJECT_ID", "githubtalent-434920")
GITHUB_SECRET_NAME = os.getenv("GITHUB_SECRET_NAME", "github-search-secret")
DB_SECRET_NAME = os.getenv("DB_SECRET_NAME", "database-crud-secret")

# Logger setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_secret_from_secret_manager(secret_name, version_id="latest"):
    """
    Retrieves a secret value from Google Cloud Secret Manager.
    """
    logging.info(f"Fetching secret: {secret_name}")
    client = secretmanager.SecretManagerServiceClient()
    name = f"projects/{PROJECT_ID}/secrets/{secret_name}/versions/{version_id}"
    response = client.access_secret_version(request={"name": name})
    return response.payload.data.decode("UTF-8")


def get_pat_from_secret_manager(version_id="latest"):
    """
    Retrieves GitHub PAT from Secret Manager.
    """
    return get_secret_from_secret_manager(GITHUB_SECRET_NAME, version_id)


def get_db_credentials_from_secret_manager(version_id="latest"):
    """
    Retrieves database credentials from Secret Manager.
    """
    return get_secret_from_secret_manager(DB_SECRET_NAME, version_id)


def db_connect(db_credentials):
    """
    Establishes a connection to the PostgreSQL database using provided credentials.
    """
    return psycopg2.connect(
        host=db_credentials['DB_HOST'],
        port=db_credentials['DB_PORT'],
        database=db_credentials['DB_NAME'],
        user=db_credentials['DB_USER'],
        password=db_credentials['DB_PASS']
    )


def select_all_repos_from_db(db_credentials):
    """
    Fetches all repositories from the database.
    """
    logging.info("Selecting all repositories from the database")
    try:
        with db_connect(db_credentials) as connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT * FROM github_repos;")
                return cursor.fetchall()
    except Exception as e:
        logging.error(f"Error selecting all repositories: {e}")
        return []


def get_recently_updated_owner_ids():
    """
    Retrieves unique profile IDs of recently updated owners.
    """
    logging.info("Fetching recently updated owner IDs")
    db_credentials = json.loads(get_db_credentials_from_secret_manager())

    try:
        with db_connect(db_credentials) as connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT * FROM github_repos")
                repo_results = cursor.fetchall()

        unique_profile_ids = {str(repo_result[13]) for repo_result in repo_results}
        return list(unique_profile_ids)
    except Exception as e:
        logging.error(f"Error fetching owner IDs: {e}")
        return []


def call_github_search_owners(pat, github_profile_number):
    """
    Fetches GitHub owner profile information using GitHub API.
    """
    logging.info(f"Fetching GitHub profile info for user: {github_profile_number}")
    url = f"https://api.github.com/user/{github_profile_number}"
    headers = {
        "Authorization": f"Bearer {pat}",
        "Accept": "application/vnd.github.v3+json"
    }

    response = requests.get(url, headers=headers)
    return response.json()


def insert_profiles_into_database(profile_info_pulled, pat):
    """
    Inserts or updates profiles into the `github_owners` table in the database.
    """
    logging.info("Inserting profiles into the database")
    db_credentials = json.loads(get_db_credentials_from_secret_manager())

    try:
        with db_connect(db_credentials) as connection:
            insertion_query = """
                INSERT INTO github_owners (
                    id, login, type, name, company, email, bio, 
                    followers, following, html_url, blog, 
                    twitter_username, updated_at
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
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

            profile_data_list = [
                (
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
                for profile_info in (
                    call_github_search_owners(pat, profile_id)
                    for profile_id in profile_info_pulled
                )
            ]

            with connection.cursor() as cursor:
                cursor.executemany(insertion_query, profile_data_list)
                connection.commit()
    except Exception as e:
        logging.error(f"Error inserting profiles into database: {e}")


def update_github_owners(request):
    """
    Main function to update GitHub owners in the database.
    """
    logging.info("Starting update_github_owners")

    try:
        pat_payload = json.loads(get_pat_from_secret_manager())
        pat = pat_payload["GITHUB_PAT"]
        owner_ids = get_recently_updated_owner_ids()
        insert_profiles_into_database(owner_ids, pat)
        return owner_ids
    except Exception as e:
        logging.error(f"Error updating GitHub owners: {e}")
        return None
