from datetime import datetime, timedelta

#TEMPORARY VARIABLES

searched_keyword_string = "Mark Zuckerberg"

# assume time is according to YouTube API at UTC 0, so 4 hours ahead of New York and 7 ahead of San Francisco
# A midnight pull the next day will be seen at 8PM in New York today

start_date_and_time = datetime(
    2024, #year
    9, #month
    4, #day of month
    3, # hour
    0, # minute
    0 #second
)

time_window_hours = timedelta(hours = 1)

maximum_results_per_json = 50 # Google docs default this to 25/JSON, was told that we can max it out to 50