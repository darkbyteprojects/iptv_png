import os
import sys
import json
import requests
import urllib.parse

# Remote URL where your original playlist is hosted
REMOTE_JSON_URL = "https://allinonereborn2.online/sony/sliv3.json"
OUTPUT_JSON = "proxied_manifest_playlist.json"
OUTPUT_M3U = "playlist.m3u"

STREAM_PROXY_BASE = "https://allinonereborn2.online/livtest3/stream_proxy.php?url="
REFERER_BASE = "https://allinonereborn2.online/sony/ptest1.html?id="
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0"

def main():
    print("Step 1: Removing old files...")
    for old_file in [OUTPUT_JSON, OUTPUT_M3U]:
        if os.path.exists(old_file):
            os.remove(old_file)
            print(f" -> Removed old {old_file}")

    print(f"\nStep 2: Fetching playlist from {REMOTE_JSON_URL}...")
    try:
        # Added extra headers to look more like a real browser and bypass basic bot blocks
        headers = {
            "User-Agent": USER_AGENT,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1"
        }
        response = requests.get(REMOTE_JSON_URL, headers=headers, timeout=30)
        
        # If the server blocked us (e.g., 403 Forbidden), this will print the exact reason
        if response.status_code != 200:
            print(f"\nCRITICAL ERROR: Server rejected the request! Status Code: {response.status_code}")
            print(f"Response text: {response.text[:200]}...")
            sys.exit(1) # FORCE GITHUB ACTIONS TO FAIL PROPERLY
            
        playlist_data = response.json()
        print(" -> Fetch successful!")
        
    except json.JSONDecodeError:
        print("\nCRITICAL ERROR: The server did not return valid JSON. You may be blocked by Cloudflare.")
        sys.exit(1)
    except Exception as e:
        print(f"\nCRITICAL ERROR fetching remote playlist: {e}")
        sys.exit(1) # FORCE GITHUB ACTIONS TO FAIL PROPERLY

    print("\nStep 3: Processing and wrapping stream URLs with PHP proxy & Referers...")
    
    m3u_lines = ["#EXTM3U"]

    def process_channel(ch_id, ch_info):
        if not isinstance(ch_info, dict) or "m3u8" not in ch_info:
            return
            
        title = ch_info.get("title", ch_info.get("name", "Unknown Channel"))
        logo = ch_info.get("logo", "")
        genre = ch_info.get("genre", "SONY NETWORK")
        original_url = ch_info["m3u8"]
        
        if not original_url.startswith("https://allinonereborn2.online/livtest3/stream_proxy.php"):
            proxied_url = f"{STREAM_PROXY_BASE}{urllib.parse.quote(original_url, safe='')}"
            ch_info["m3u8"] = proxied_url
        else:
            proxied_url = original_url
            
        actual_id = ch_info.get("id", ch_id) 
        referer_url = f"{REFERER_BASE}{actual_id}"
        
        stream_url_with_headers = f"{proxied_url}|Referer={referer_url}&User-Agent={USER_AGENT}"
        
        extinf = f'#EXTINF:-1 group-title="{genre}" tvg-logo="{logo}",{title}'
        m3u_lines.append(extinf)
        m3u_lines.append(stream_url_with_headers)

    if isinstance(playlist_data, dict):
        for channel_id, channel_info in playlist_data.items():
            process_channel(channel_id, channel_info)
    elif isinstance(playlist_data, list):
        for channel_info in playlist_data:
            ch_id = channel_info.get("id", "unknown-id")
            process_channel(ch_id, channel_info)

    print("\nStep 4: Writing new files...")
    
    if len(m3u_lines) <= 1:
        print("CRITICAL ERROR: No channels were parsed. M3U is empty. Aborting.")
        sys.exit(1)

    with open(OUTPUT_M3U, "w", encoding="utf-8") as f:
        f.write("\n".join(m3u_lines) + "\n")
    print(f" -> Successfully generated fresh {OUTPUT_M3U}!")

    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(playlist_data, f, indent=4, ensure_ascii=False)
    print(f" -> Successfully generated fresh {OUTPUT_JSON}!")

if __name__ == "__main__":
    main()
