import psycopg2
import random
import json
from google.cloud import secretmanager


# Function to fetch the secret from Google Secret Manager
def access_secret_version(secret_id, version_id="latest"):
    client = secretmanager.SecretManagerServiceClient()

    # Hardcoded project ID based on your provided info
    project_id = "githubtalent-434920"
    name = f"projects/{project_id}/secrets/{secret_id}/versions/{version_id}"

    response = client.access_secret_version(request={"name": name})
    payload = response.payload.data.decode("UTF-8")

    return payload


# Cloud Function handler
def manage_repo_db(request):
    # Fetch the secret containing DB credentials
    secret_id = "database-crud-secret"
    secret_payload = access_secret_version(secret_id)

    # Parse the JSON secret
    secret_json = json.loads(secret_payload)

    # Connect using credentials from Secret Manager
    connection = psycopg2.connect(
        user=secret_json['DB_USER'],
        password=secret_json['DB_PASS'],
        host=secret_json['DB_HOST'],
        port=secret_json['DB_PORT'],
        database=secret_json['DB_NAME']
    )

    # Create a cursor to interact with the database
    cursor = connection.cursor()

    # Step 1: Randomly select an integer from 1 to 100
    random_int = random.randint(1, 100)

    # Step 2: Construct the insert/update SQL query
    repo_id = random_int
    repo_name = f'Repo{random_int}'
    owner_login = f'owner{random_int}'
    fork = random.choice([True, False])
    description = f'Description for Repo{random_int}'
    size = random.randint(50, 500)
    stargazers_count = random.randint(10, 200)
    watchers_count = random.randint(20, 250)
    updated_at = '2023-09-09'
    created_at = '2023-08-01'
    url = f'https://github.com/owner{random_int}/repo{random_int}'

    # SQL query to insert or update the data
    query = """
    INSERT INTO github_repos (id, name, owner_login, fork, description, size, stargazers_count, watchers_count, updated_at, created_at, url)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    ON CONFLICT (id) DO UPDATE SET 
        name = EXCLUDED.name,
        owner_login = EXCLUDED.owner_login,
        fork = EXCLUDED.fork,
        description = EXCLUDED.description,
        size = EXCLUDED.size,
        stargazers_count = EXCLUDED.stargazers_count,
        watchers_count = EXCLUDED.watchers_count,
        updated_at = EXCLUDED.updated_at,
        created_at = EXCLUDED.created_at,
        url = EXCLUDED.url;
    """

    # Execute the query with the new data
    cursor.execute(query, (
    repo_id, repo_name, owner_login, fork, description, size, stargazers_count, watchers_count, updated_at, created_at,
    url))

    # Commit the changes
    connection.commit()

    # Step 4: Select all data from the table to check results
    cursor.execute("SELECT * FROM github_repos")
    results = cursor.fetchall()

    # Close the connection
    connection.close()

    # Return the results in JSON format
    return {"data": results}, 200
