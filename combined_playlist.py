import requests
import json

# 1. Fetch the channel list (the one missing the cookies)
channels_url = "https://jjtvxweb.pages.dev/jstr4web.json" # e.g., the local file or raw URL
try:
    channels_response = requests.get(channels_url)
    channels_data = channels_response.json()
except Exception as e:
    print(f"Failed to load channels: {e}")
    exit(1)

# 2. Fetch the fresh master wildcard cookie
cookie_url = "https://allinonereborn2.online/jstrweb2/cookies.json"
try:
    cookie_response = requests.get(cookie_url, headers={"User-Agent": "Mozilla/5.0"})
    cookie_json = cookie_response.json()
    
    # Extract the cookie string (it is the second item in the array)
    fresh_cookie = cookie_json[1].get("cookie", "")
except Exception as e:
    print(f"Failed to load fresh cookie: {e}")
    fresh_cookie = ""

# 3. Inject the fresh cookie into every channel
if fresh_cookie:
    # Handle if the root is a list or a dict containing a 'channels' array
    channel_list = channels_data.get("channels", []) if isinstance(channels_data, dict) else channels_data
    
    for channel in channel_list:
        channel["cookie"] = fresh_cookie

# 4. Save the combined JSON to a new file for your app to read
with open("combined_playlist.json", "w") as f:
    json.dump(channels_data, f, indent=4)
    
print("Successfully merged fresh cookies into the playlist!")
