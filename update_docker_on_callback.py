import json

import requests
import yaml
import os
import subprocess

from dotenv import load_dotenv

load_dotenv()  # take environment variables from .env

bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
bot_chat_id = os.getenv("TELEGRAM_BOT_CHAT_ID")
docker_compose_filepath = os.getenv("DOCKER_COMPOSE_FILEPATH")

OFFSET_FILE = "telegram_offset.txt"

API_URL = f"https://api.telegram.org/bot{bot_token}"

def read_offset():
    if os.path.exists(OFFSET_FILE):
        with open(OFFSET_FILE, "r") as f:
            return int(f.read().strip())
    return None

def save_offset(offset):
    with open(OFFSET_FILE, "w") as f:
        f.write(str(offset))

def get_updates(offset=None):
    url = f"{API_URL}/getUpdates"
    params = {
        "timeout": 30,
        "offset": offset
    }
    res = requests.get(url, params=params)
    return res.json()

def handle_callback(callback):
    query_id = callback["id"]
    user = callback["from"]["username"]
    data = json.loads(callback["data"])

    print(f"📥 Button pressed by @{user}: {data}")

    # Respond to Telegram to remove spinner
    requests.post(f"{API_URL}/answerCallbackQuery", data={
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

def update_image_version(service_name, new_image, new_version):
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
        yaml.dump(data, f, sort_keys=False)

    print(f"✅ Service '{service_name}' mis à jour avec l'image {full_image}")

def run_docker_compose():
    try:
        # Run the command
        result = subprocess.run(
            ["docker", "compose", "up", "-d"],
            capture_output=True,
            text=True,
            check=True  # Raises CalledProcessError on failure
        )
        print("✅ Docker Compose started successfully:")
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print("❌ Error running docker-compose:")
        print(e.stderr)

def main():
    print("🤖 Listening for button clicks...")
    offset = read_offset()

    updates = get_updates(offset)
    for update in updates.get("result", []):
        offset = update["update_id"] + 1
        save_offset(offset)  # Save offset immediately after processing each update

        if "callback_query" in update:
            image, version = handle_callback(update["callback_query"])

            update_image_version(image , image, version)

            run_docker_compose()

if __name__ == "__main__":
    main()
