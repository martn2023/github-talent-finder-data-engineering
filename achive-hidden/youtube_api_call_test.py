import urllib.parse
from config import youtube_api_key  # coming in as a string value
from search_config import searched_keyword_string, start_date_and_time, time_window_hours, maximum_results_per_json


start_date_and_time_str = start_date_and_time.strftime('%Y-%m-%dT%H:%M:%SZ')

end_date_and_time = start_date_and_time + time_window_hours
end_date_and_time_str = end_date_and_time.strftime('%Y-%m-%dT%H:%M:%SZ')

# pulled from https://developers.google.com/youtube/v3/docs/search/list
api_base_url = 'https://www.googleapis.com/youtube/v3/search'

# Define the parameters as a dictionary
params = {
    'part': 'snippet',  # The fields we want to retrieve
    'q': searched_keyword_string,  # The search term from search_config.py
    'maxResults': maximum_results_per_json,
    'type': 'video',  # This will pull both normal videos and shorts; YT does not explicitly label shorts but it might be inferred by length + aspect ratio later
    'publishedAfter': start_date_and_time_str,  # Start date from search_config.py
    'publishedBefore': end_date_and_time_str,  # End date is start date + time window
    'order': 'viewCount',  # could have been by view count, upload data
    'key': youtube_api_key  # API key from config.py
}

encoded_params = urllib.parse.urlencode(params) # this will encode the variables into a workable URL e.g. converting spaces in keyword term
api_call_final_url = f"{api_base_url}?{encoded_params}"

print("final url")
print(api_call_final_url)

# Send the request to YouTube API
#response = requests.get(api_base_url, params=params)

# Print the constructed URL for verification
print("Constructed URL:")
#print(response.url)

# Print the JSON response from the API
#print("API Response:", response.json())
