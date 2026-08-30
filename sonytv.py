import json
import requests

# Put the URL of your raw JSON playlist here
SOURCE_JSON_URL = "https://allinonereborn2.online/sony/sliv3.json" 

PROXY_PREFIX = "https://allinonereborn2.online/livtest3/stream_proxy.php?url="

def main():
    print("Fetching original playlist...")
    try:
        response = requests.get(SOURCE_JSON_URL, timeout=30)
        response.raise_for_status()
        playlist_data = response.json()
    except Exception as e:
        print(f"Error fetching network playlist: {e}")
        # Fallback: if network fails, try reading a local file named 'source.json'
        try:
            with open("source.json", "r", encoding="utf-8") as f:
                playlist_data = json.load(f)
        except Exception as local_e:
            print(f"Fatal Error - Could not load local or network JSON: {local_e}")
            return

    print("Injecting PHP proxy into stream URLs...")
    
    # Handle Dictionary-based JSON (like your "sony-hd" example)
    if isinstance(playlist_data, dict):
        for channel_id, channel_info in playlist_data.items():
            if isinstance(channel_info, dict) and "m3u8" in channel_info:
                original_url = channel_info["m3u8"]
                # Only prepend if it hasn't been added yet
                if not original_url.startswith(PROXY_PREFIX):
                    channel_info["m3u8"] = f"{PROXY_PREFIX}{original_url}"
                    
    # Handle Array-based JSON (just in case your format changes)
    elif isinstance(playlist_data, list):
        for channel_info in playlist_data:
            if isinstance(channel_info, dict) and "m3u8" in channel_info:
                original_url = channel_info["m3u8"]
                if not original_url.startswith(PROXY_PREFIX):
                    channel_info["m3u8"] = f"{PROXY_PREFIX}{original_url}"

    # Save the finalized, proxied playlist
    output_filename = "sonytv.json"
    with open(output_filename, "w", encoding="utf-8") as f:
        json.dump(playlist_data, f, indent=4, ensure_ascii=False)
        
    print(f"Success! Proxy links generated and saved to {output_filename}")

if __name__ == "__main__":
    main()
