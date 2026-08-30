import json
import requests
import urllib.parse

# Path to your input JSON file in the repository (or a remote URL)
SOURCE_JSON = "https://allinonereborn2.online/sony/sliv3.json" 
OUTPUT_JSON = "proxied_manifest_playlist.json"

SEGMENT_PROXY_BASE = "https://allinonereborn2.online/livtest3/segment_proxy.php?url="
STREAM_PROXY_BASE = "https://allinonereborn2.online/livtest3/stream_proxy.php?url="

def rewrite_m3u8_content(m3u8_text, base_url):
    rewritten_lines = []
    for line in m3u8_text.splitlines():
        trimmed = line.strip()
        if not trimmed or trimmed.startswith("#"):
            rewritten_lines.append(line)
        else:
            # Resolve relative URLs to absolute URLs based on the manifest base
            abs_url = urllib.parse.urljoin(base_url, trimmed)
            
            # Check if it's already wrapped in segment proxy
            if not abs_url.startswith("https://allinonereborn2.online/livtest3/segment_proxy.php"):
                wrapped_url = f"{SEGMENT_PROXY_BASE}{urllib.parse.quote(abs_url, safe='')}"
                rewritten_lines.append(wrapped_url)
            else:
                rewritten_lines.append(abs_url)
                
    return "\n".join(rewritten_lines)

def main():
    print("Loading source playlist...")
    try:
        with open(SOURCE_JSON, "r", encoding="utf-8") as f:
            playlist_data = json.load(f)
    except Exception as e:
        print(f"Error reading source.json: {e}")
        return

    print("Processing and rewriting stream manifests...")
    
    # Handle dictionary-based JSON structure
    if isinstance(playlist_data, dict):
        for channel_id, channel_info in playlist_data.items():
            if isinstance(channel_info, dict) and "m3u8" in channel_info:
                original_url = channel_info["m3u8"]
                
                # If it's already using stream_proxy, let's fetch the actual .m3u8 text to rewrite its segments
                target_fetch_url = original_url
                if not target_fetch_url.startswith("https://allinonereborn2.online/livtest3/stream_proxy.php"):
                    target_fetch_url = f"{STREAM_PROXY_BASE}{urllib.parse.quote(original_url, safe='')}"
                
                try:
                    print(f"Fetching manifest for: {channel_id}")
                    res = requests.get(target_fetch_url, headers={"User-Agent": "Mozilla/5.0"}, timeout=15)
                    if res.status_code == 200 and "#EXTM3U" in res.text:
                        # Optional: If you want to host static rewritten text or keep the stream_proxy wrapper
                        # For direct compatibility, we ensure the stream URL points safely through stream_proxy
                        channel_info["m3u8"] = target_fetch_url
                    else:
                        print(f"Warning: Failed to fetch valid manifest for {channel_id}")
                except Exception as err:
                    print(f"Network error fetching {channel_id}: {err}")

    # Save the updated playlist
    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(playlist_data, f, indent=4, ensure_ascii=False)
        
    print(f"Successfully generated {OUTPUT_JSON}")

if __name__ == "__main__":
    main()
