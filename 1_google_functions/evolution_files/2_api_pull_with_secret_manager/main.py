import psycopg2
import random
import json
from google.cloud import secretmanager
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

