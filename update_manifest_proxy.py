import os
import json
import requests
import urllib.parse

# Remote URL where your original playlist is hosted
REMOTE_JSON_URL = "https://allinonereborn2.online/sony/sliv3.json"
OUTPUT_JSON = "proxied_manifest_playlist.json"
OUTPUT_M3U = "playlist.m3u"

STREAM_PROXY_BASE = "https://allinonereborn2.online/livtest3/stream_proxy.php?url="
REFERER_BASE = "https://allinonereborn2.online/sony/ptest1.html?id="
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:154.0) Gecko/20100101 Firefox/154.0"

def main():
    # 1. Delete old files if they exist to ensure completely fresh generation
    for old_file in [OUTPUT_JSON, OUTPUT_M3U]:
        if os.path.exists(old_file):
            os.remove(old_file)
            print(f"Removed old {old_file}")

    print(f"\nFetching playlist directly from {REMOTE_JSON_URL}...")
    try:
        headers = {
            "User-Agent": USER_AGENT
        }
        response = requests.get(REMOTE_JSON_URL, headers=headers, timeout=30)
        response.raise_for_status()
        playlist_data = response.json()
    except Exception as e:
        print(f"Error fetching remote playlist: {e}")
        return

    print("Processing and wrapping stream URLs with PHP proxy & Referers...")
    
    m3u_lines = ["#EXTM3U"]

    # Helper function to process each channel and build the M3U lines
    def process_channel(ch_id, ch_info):
        if not isinstance(ch_info, dict) or "m3u8" not in ch_info:
            return
            
        title = ch_info.get("title", ch_info.get("name", "Unknown Channel"))
        logo = ch_info.get("logo", "")
        genre = ch_info.get("genre", "SONY NETWORK")
        original_url = ch_info["m3u8"]
        
        # 1. Wrap the m3u8 link with stream_proxy.php if not already wrapped
        if not original_url.startswith("https://allinonereborn2.online/livtest3/stream_proxy.php"):
            proxied_url = f"{STREAM_PROXY_BASE}{urllib.parse.quote(original_url, safe='')}"
            ch_info["m3u8"] = proxied_url # Update JSON data
        else:
            proxied_url = original_url
            
        # 2. Build the dynamic Referer using the channel ID
        actual_id = ch_info.get("id", ch_id) 
        referer_url = f"{REFERER_BASE}{actual_id}"
        
        # 3. Append headers to the stream link for M3U players
        stream_url_with_headers = f"{proxied_url}|Referer={referer_url}&User-Agent={USER_AGENT}"
        
        # 4. Construct M3U entry
        extinf = f'#EXTINF:-1 group-title="{genre}" tvg-logo="{logo}",{title}'
        m3u_lines.append(extinf)
        m3u_lines.append(stream_url_with_headers)

    # Parse based on dictionary-based JSON structure
    if isinstance(playlist_data, dict):
        for channel_id, channel_info in playlist_data.items():
            process_channel(channel_id, channel_info)
            
    # Handle array-based JSON structure (fallback)
    elif isinstance(playlist_data, list):
        for channel_info in playlist_data:
            # For lists, pull the 'id' field directly from the dict
            ch_id = channel_info.get("id", "unknown-id")
            process_channel(ch_id, channel_info)

    # Save the finalized M3U file
    with open(OUTPUT_M3U, "w", encoding="utf-8") as f:
        f.write("\n".join(m3u_lines) + "\n")
    print(f"Successfully generated fresh {OUTPUT_M3U}!")

    # Save the finalized JSON output file
    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(playlist_data, f, indent=4, ensure_ascii=False)
    print(f"Successfully generated fresh {OUTPUT_JSON}!")

if __name__ == "__main__":
    main()
