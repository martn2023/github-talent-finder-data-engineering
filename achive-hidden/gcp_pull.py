import psycopg2
import random
import json
from google.cloud import secretmanager
import requests
import logging


def access_secret_version(secrets_name, version_id="latest"):
    client = secretmanager.SecretManagerServiceClient()

    project_id = "githubtalent-434920"
    name = f"projects/{project_id}/secrets/{secrets_name}/versions/{version_id}"

    response = client.access_secret_version(request={"name": name})
    payload = response.payload.data.decode("UTF-8")

    return payload


def get_github_repos(request):
    secrets_name = "github-search-secret"
    secret_payload = access_secret_version(secrets_name)
    secret_json = json.loads(secret_payload)

    retrieved_pat = secret_json["GITHUB_PAT"]
    url = "https://api.github.com/search/repositories?q=pushed%3A2024-09-01T00%3A00%3A00..2024-09-01T00%3A01%3A00+is%3Apublic+-fork%3Atrue&per_page=100&page=1"  # hardcoded 1 minute range in
    headers = {
        "Authorization": f"Bearer {retrieved_pat}",
        "Accept": "application/vnd.github.v3+json"
    }

    response = requests.get(url, headers=headers)
    return response.json()
