# Sample owner IDs for testing GitHub API calls
# owner_id_1 = 129706771  # Sample Owner 1
# owner_id_2 = 3303018    # Sample Owner 2
# owner_id_3 = 89064991   # Sample Owner 3

# These IDs will be used to test our GitHub API calls

import json #this is not in the requirements.txt because it's part of python, but it's like a knife in a pre-populated kitchen where you still need to open the drawer to access tools
from google.cloud import secretmanager


def hello_http(request):
    return "Hello, world"