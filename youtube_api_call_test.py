from config import youtube_api_key #coming in as a string value
import urllib.parse # need this to get rid of spaces in keyword terms so urls will be in valid format


#TEMPORARY VARIABLES
searched_keyword_string = "Taylor Swift"
max_results_integer = 50 # Google's default 25, but ChatGPT claims it can be 50


# This came from https://developers.google.com/youtube/v3/docs/search/list
api_base_url = "https://www.googleapis.com/youtube/v3/search"

# This is the part of the snippet a.k.a. the fields we want to GET
part_url = "?part=snippet"

query_url = "&" + "q=" + urllib.parse.quote(searched_keyword_string)

max_results_url = s"&" + "maxResults=" + str(max_results_integer)

api_key_url = "&" + "key=" + youtube_api_key

final_api_url = api_base_url + part_url + query_url + max_results_url + api_key_url

print(final_api_url)