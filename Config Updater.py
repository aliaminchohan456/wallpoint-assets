import os
import json
import urllib.parse
import re
import subprocess  # Naya module git commands ke liye

# Base Directory Setup
base_dir = r"C:\dev\WallPoint\Wallpoint Assets"
root_config_path = os.path.join(base_dir, "configs.json")

# GitHub Repo Details
github_user = "aliaminchohan456"
repo_name = "wallpoint-assets"
branch = "main"

# Fixed Data for JSON
fixed_aspect_ratio = 0.5625
fixed_resolution = "2400x3200"
fixed_size = "1.2 MB"
photographer_name = "Wallpoint"

def natural_sort_key(s):
    return [int(text) if text.isdigit() else text.lower() for text in re.split(r'(\d+)', s)]

def load_existing_root_config():
    if os.path.exists(root_config_path):
        try:
            with open(root_config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return {"appVersion": "1.0", "categories": []}
    return {"appVersion": "1.0", "categories": []}

def push_to_github(repo_path):
    print("\n🚀 GitHub par changes push ho rahi hain... thora wait karo!")
    try:
        # Git add
        subprocess.run(["git", "add", "."], cwd=repo_path, check=True, capture_output=True)
        
        # Git commit (Agar koi nayi change nahi hogi toh ye error de sakta hai, isliye isko handle kiya hai)
        commit_process = subprocess.run(["git", "commit", "-m", "Auto-updated Wallpapers & Configs"], cwd=repo_path, capture_output=True)
        if "nothing to commit" in commit_process.stdout.decode():
            print("⚠️ Koi nayi file add nahi hui, sab pehle se updated hai.")
            return

        # Git push
        subprocess.run(["git", "push", "origin", "main"], cwd=repo_path, check=True, capture_output=True)
        print("✅ Lo bhai, saara data GitHub par successfully push ho gaya!")
        
    except subprocess.CalledProcessError as e:
        print("❌ Push karne mein koi masla aaya. Output check karo:\n", e.stderr.decode())

def main():
    root_config_data = load_existing_root_config()
    existing_categories = {cat["id"]: cat for cat in root_config_data.get("categories", [])}
    updated_categories_list = []

    for folder_name in os.listdir(base_dir):
        folder_path = os.path.join(base_dir, folder_name)
        
        if not os.path.isdir(folder_path) or folder_name.startswith('.'):
            continue

        category_id = folder_name.lower()
        
        # 1. READ & RENAME FILES
        images = [f for f in os.listdir(folder_path) if f.lower().endswith(('.jpg', '.png', '.jpeg', '.webp'))]
        if not images:
            continue

        pattern = re.compile(rf"^{category_id} \((\d+)\)\.(jpg|png|jpeg|webp)$", re.IGNORECASE)
        max_index = 0
        incorrect_files = []

        for img in images:
            match = pattern.match(img)
            if match:
                num = int(match.group(1))
                if num > max_index:
                    max_index = num
            else:
                incorrect_files.append(img)

        if incorrect_files:
            print(f"[{folder_name}] Renaming {len(incorrect_files)} new files...")
            incorrect_files.sort(key=natural_sort_key)
            for img in incorrect_files:
                max_index += 1
                ext = img.split('.')[-1]
                new_name = f"{category_id} ({max_index}).{ext}"
                old_path = os.path.join(folder_path, img)
                new_path = os.path.join(folder_path, new_name)
                os.rename(old_path, new_path)

        images = [f for f in os.listdir(folder_path) if f.lower().endswith(('.jpg', '.png', '.jpeg', '.webp'))]
        images.sort(key=natural_sort_key)

        # 2. GENERATE CONFIG.JSON
        wallpapers = []
        for index, file_name in enumerate(images):
            encoded_name = urllib.parse.quote(file_name)
            cdn_url = f"https://cdn.jsdelivr.net/gh/{github_user}/{repo_name}@{branch}/{folder_name}/{encoded_name}"
            
            wall_id = f"{category_id}{(index + 1):03d}"
            title = f"{folder_name.capitalize()} Wallpaper {index + 1}"
            
            wallpapers.append({
                "id": wall_id,
                "title": title,
                "photographer": photographer_name,
                "imageUrl": cdn_url,
                "aspectRatio": fixed_aspect_ratio,
                "resolution": fixed_resolution,
                "size": fixed_size
            })

        folder_json_data = {
            "category": category_id,
            "wallpapers": wallpapers
        }

        folder_config_path = os.path.join(folder_path, "config.json")
        with open(folder_config_path, 'w', encoding='utf-8') as f:
            json.dump(folder_json_data, f, indent=2, ensure_ascii=False)
        
        print(f"[{folder_name}] config.json updated with {len(images)} wallpapers.")

        # 3. UPDATE MASTER CONFIGS.JSON
        encoded_cover = urllib.parse.quote(images[0])
        cover_image_url = f"https://cdn.jsdelivr.net/gh/{github_user}/{repo_name}@{branch}/{folder_name}/{encoded_cover}"
        config_url = f"https://cdn.jsdelivr.net/gh/{github_user}/{repo_name}@{branch}/{folder_name}/config.json"

        if category_id in existing_categories:
            cat_entry = existing_categories[category_id]
            cat_entry["configUrl"] = config_url
            cat_entry["coverImage"] = cover_image_url
            updated_categories_list.append(cat_entry)
        else:
            updated_categories_list.append({
                "id": category_id,
                "name": f"{folder_name.capitalize()} Wallpapers",
                "iconName": "Wallpaper",
                "configUrl": config_url,
                "coverImage": cover_image_url
            })

    root_config_data["categories"] = updated_categories_list
    with open(root_config_path, 'w', encoding='utf-8') as f:
        json.dump(root_config_data, f, indent=2, ensure_ascii=False)
    
    print("\nMaster configs.json successfully updated!")

    # 4. PUSH TO GITHUB
    push_to_github(base_dir)

if __name__ == "__main__":
    main()