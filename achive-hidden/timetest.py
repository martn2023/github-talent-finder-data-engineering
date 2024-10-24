from datetime import datetime, timedelta

# Set last_call_time as a string, then convert it to a datetime object
last_call_time_string = "2024-10-13T00:00:00Z"
last_call_time = datetime.strptime(last_call_time_string, "%Y-%m-%dT%H:%M:%SZ")

# Increment by 1 minute for the next call
next_call_time = last_call_time + timedelta(minutes=1)

# Format start and end times
start_time = last_call_time.strftime("%Y-%m-%dT%H:%M:%S")
end_time = next_call_time.strftime("%Y-%m-%dT%H:%M:%S")

# Construct the URL
url = f"https://api.github.com/search/repositories?q=pushed%3A{start_time}..{end_time}+is%3Apublic+-fork%3Atrue&per_page=100&page=1"
print("Proposed URL:", url)

#https://api.github.com/search/repositories?q=pushed%3A2025-10-13T00:00:00..2025-10-13T00:01:00+is%3Apublic+-fork%3Atrue&per_page=100&page=1
#https://api.github.com/search/repositories?q=pushed%3A2024-09-01T00%3A00%3A00..2024-09-01T00%3A01%3A00+is%3Apublic+-fork%3Atrue&per_page=100&page=1
