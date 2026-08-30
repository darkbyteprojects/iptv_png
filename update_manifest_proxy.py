import json
import requests
import urllib.parse

# Remote URL where your original playlist is hosted
REMOTE_JSON_URL = "https://allinonereborn2.online/sony/sliv3.json"
OUTPUT_JSON = "proxied_manifest_playlist.json"

STREAM_PROXY_BASE = "https://allinonereborn2.online/livtest3/stream_proxy.php?url="

def main():
    print(f"Fetching playlist directly from {REMOTE_JSON_URL}...")
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        response = requests.get(REMOTE_JSON_URL, headers=headers, timeout=30)
        response.raise_for_status()
        playlist_data = response.json()
    except Exception as e:
        print(f"Error fetching remote playlist: {e}")
        return

    print("Processing and wrapping stream URLs with PHP proxy...")
    
    # Handle dictionary-based JSON structure
    if isinstance(playlist_data, dict):
        for channel_id, channel_info in playlist_data.items():
            if isinstance(channel_info, dict) and "m3u8" in channel_info:
                original_url = channel_info["m3u8"]
                
                # Wrap the m3u8 link with stream_proxy.php if not already wrapped
                if not original_url.startswith("https://allinonereborn2.online/livtest3/stream_proxy.php"):
                    channel_info["m3u8"] = f"{STREAM_PROXY_BASE}{urllib.parse.quote(original_url, safe='')}"

    # Handle array-based JSON structure (fallback)
    elif isinstance(playlist_data, list):
        for channel_info in playlist_data:
            if isinstance(channel_info, dict) and "m3u8" in channel_info:
                original_url = channel_info["m3u8"]
                if not original_url.startswith("https://allinonereborn2.online/livtest3/stream_proxy.php"):
                    channel_info["m3u8"] = f"{STREAM_PROXY_BASE}{urllib.parse.quote(original_url, safe='')}"

    # Save the finalized output file so GitHub Actions can commit it
    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(playlist_data, f, indent=4, ensure_ascii=False)
        
    print(f"Successfully generated {OUTPUT_JSON} from remote source!")

if __name__ == "__main__":
    main()
