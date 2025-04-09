from redundant.scrip import ClockifyAPI
from pprint import pprint
from datetime import datetime, timedelta
from datetime import datetime, timedelta, UTC

# time_entries = ClockifyAPI.get_time_entries()

# # print only the description and start time end time and duration
# for entry in time_entries:
#     print(
#         entry["description"],
#         entry["timeInterval"]["start"],
#         entry["timeInterval"]["end"],
#         entry["timeInterval"]["duration"],
#     )

days = 14
end_time = datetime.now()
start_time = end_time - timedelta(days=days)
start_time_str = start_time.strftime("%Y-%m-%dT%H:%M:%SZ")
end_time_str = end_time.strftime("%Y-%m-%dT%H:%M:%SZ")

print(start_time_str, "/////", end_time_str)
