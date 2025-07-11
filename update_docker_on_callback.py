import json
import sys

import requests
import yaml
import os
import subprocess

def read_offset(offset_filepath):
    if os.path.exists(offset_filepath):
        with open(offset_filepath, "r") as f:
            return int(f.read().strip())
    return None

def save_offset(offset_filepath, offset):
    with open(offset_filepath, "w") as f:
        f.write(str(offset))

def get_updates(offset, api_url):
    url = f"{api_url}/getUpdates"
    params = {
        "timeout": 30,
        "offset": offset
    }
    res = requests.get(url, params=params)
    return res.json()

def handle_callback(callback, api_url):
    query_id = callback["id"]
    user = callback["from"]["username"]
    data = json.loads(callback["data"])

    print(f"📥 Button pressed by @{user}: {data}")

    # Respond to Telegram to remove spinner
    requests.post(f"{api_url}/answerCallbackQuery", data={
        "callback_query_id": query_id,
        "text": f"✅ You clicked: {data}",
        "show_alert": False
    })

    # Example: take action depending on button
    if data["a"] == "approve":
        print("🔧 Approved action triggered.")
        return data["i"], data["v"]
    elif data["a"] == "reject":
        print("❌ Rejection action triggered.")
        return None, None

def update_image_version(service_name, new_image, new_version, docker_compose_filepath):
    print(docker_compose_filepath)
    with open(docker_compose_filepath, 'r') as f:
        data = yaml.safe_load(f)

    # Compose l'image complète
    full_image = f"{new_image}:{new_version}"

    # Vérifie que le service existe
    if service_name in data.get('services', {}):
        data['services'][service_name]['image'] = full_image
    else:
        print(f"⚠️ Service '{service_name}' non trouvé dans le fichier.")

    # Écrit le fichier modifié
    with open(docker_compose_filepath, 'w') as f:
        yaml.safe_dump(data, f, sort_keys=False)

    print(f"✅ Service '{service_name}' mis à jour avec l'image {full_image}")

def run_docker_compose(currentDirectory):
    try:
        # Start the process without waiting for it to finish
        process = subprocess.Popen(
            ["docker", "compose", "up", "-d"],
            cwd=currentDirectory,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            shell=False
        )
        print(process.pid)
        print("▶️ Docker Compose command started asynchronously.")
    except Exception as e:
        print(f"❌ Failed to start docker-compose: {e}")

def update_docker(currentDirectory, offsetFilepath, dockerComposeFilepath, apiUrl):
    print("🤖 Listening for button clicks...")
    offset = read_offset(offsetFilepath)

    updates = get_updates(offset, apiUrl)

    for update in updates.get("result", []):
        offset = update["update_id"] + 1
        save_offset(offsetFilepath, offset)  # Save offset immediately after processing each update

        if "callback_query" in update:
            image, version = handle_callback(update["callback_query"], apiUrl)

            update_image_version(image , image, version, dockerComposeFilepath)

            run_docker_compose(currentDirectory)

if __name__ == "__main__":
    current_directory = sys.argv[1]
    offset_filepath = f"{sys.argv[1]}/{sys.argv[2]}"
    docker_compose_filepath = f"{sys.argv[1]}/docker-compose.yml"
    bot_token = sys.argv[3]
    api_url = f"https://api.telegram.org/bot{bot_token}"

    update_docker(current_directory, offset_filepath, docker_compose_filepath, api_url)
