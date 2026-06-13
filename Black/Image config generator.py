import os
import json
import urllib.parse
import re

# Apne folder ka path yahan dalo
folder_path = r"C:\dev\WallPoint\Wallpoint Assets\Black"
# Jahan config.json save karni hai
output_file = r"C:\dev\WallPoint\Wallpoint Assets\Black\config.json"

# GitHub Repo ki details
github_user = "aliaminchohan456"
repo_name = "wallpoint-assets"
branch = "main"
folder_name_in_repo = "Black"

# Dummy data jo cycle hota rahega
aspect_ratios = [0.75, 1.0, 1.5]
sizes = ["1.2 MB", "1.3 MB", "1.4 MB", "1.5 MB", "1.6 MB", "1.7 MB", "1.8 MB", "1.9 MB", "1.1 MB"]

def natural_sort_key(s):
    # Ye function files ko sahi tarteeb mein lagata hai (1, 2, 3... 10, 11)
    return [int(text) if text.isdigit() else text.lower() for text in re.split(r'(\d+)', s)]

wallpapers = []

if os.path.exists(folder_path):
    # Sirf .jpg aur .png files ko uthana
    files = [f for f in os.listdir(folder_path) if f.lower().endswith(('.jpg', '.png'))]
    files.sort(key=natural_sort_key)

    for index, file_name in enumerate(files):
        # Space waghera ko URL format (%20) mein convert karna
        encoded_name = urllib.parse.quote(file_name)
        
        # CDN Link ban banana
        cdn_url = f"https://cdn.jsdelivr.net/gh/{github_user}/{repo_name}@{branch}/{folder_name_in_repo}/{encoded_name}"
        
        # IDs aur Titles generate karna (b001, b002)
        wall_id = f"b{(index + 1):03d}"
        title = f"Black Wallpaper {index + 1}"
        
        # Wallpaper ki entry banana
        wallpaper_entry = {
            "id": wall_id,
            "title": title,
            "photographer": "Zeenoo Art",
            "imageUrl": cdn_url,
            "aspectRatio": aspect_ratios[index % len(aspect_ratios)],
            "resolution": "2400x3200",
            "size": sizes[index % len(sizes)]
        }
        wallpapers.append(wallpaper_entry)

    # Final JSON structure
    final_data = {
        "category": "black",
        "wallpapers": wallpapers
    }

    # File mein save karna
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(final_data, f, indent=2, ensure_ascii=False)
    
    print(f"Zabardast! config.json automatically ban gayi hai {len(files)} links ke sath.")
else:
    print("Folder nahi mila bhai! Path check karo.")