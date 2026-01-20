# yt_dlp_mod Colab Script

Run this in Google Colab to search and download videos/audio directly to your local system.

```python
# @title yt_dlp_mod: Search and Download
# @markdown Enter your search query below. The script will download the first result (Video & Audio) and trigger a browser download.

search_query = "siya ram" # @param {type:"string"}

import os
import glob
import shutil
import base64
from google.colab import files

# 1. Install/Update yt-dlp-mod
!pip install -U git+https://github.com/IamDvis/yt-dlp-mod.git

# 2. Search and Download Video
print(f"Searching and downloading video for: {search_query}")
!python -m yt_dlp_mod video "ytsearch1:{search_query}" --quality 720p --format mp4

# 3. Search and Download Audio
print(f"Searching and downloading audio for: {search_query}")
!python -m yt_dlp_mod audio "ytsearch1:{search_query}" --format mp3

# 4. Identify downloaded files and trigger browser download
downloaded_files = glob.glob("*.mp4") + glob.glob("*.mp3")

if not downloaded_files:
    print("No files were downloaded. Check the output above for errors.")
else:
    print(f"Download complete. Triggering browser download for: {downloaded_files}")
    for file in downloaded_files:
        try:
            files.download(file)
        except Exception as e:
            print(f"Error triggering download for {file}: {e}")

print("\n--- Process Finished ---")
```
