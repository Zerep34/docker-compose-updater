import yaml
import requests
import json
import os

from dotenv import load_dotenv

load_dotenv()  # take environment variables from .env

bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
bot_chat_id = os.getenv("TELEGRAM_BOT_CHAT_ID")
docker_compose_filepath = os.getenv("DOCKER_COMPOSE_FILEPATH")

def get_latest_tag(image, arch):
    if "/" not in image:
        namespace = "library"
        repo = image
    else:
        namespace, repo = image.split("/", 1)

    url = f"https://registry.hub.docker.com/v2/repositories/{namespace}/{repo}/tags?page_size=100"
    try:
        res = requests.get(url)
        res.raise_for_status()
        if arch != "":
            tags = [t["name"] for t in res.json()["results"] if arch in t["name"]]
        else:
            tags = [t["name"] for t in res.json()["results"]]
        return sorted(tags, reverse=True)
    except Exception as e:
        return []

def main():
    global arch
    with open(docker_compose_filepath) as f:
        compose = yaml.safe_load(f)

    print("🔍 Checking for image updates...\n")
    for svc, details in compose.get("services", {}).items():
        image_full = details.get("image")
        if not image_full:
            continue

        if ":" in image_full:
            image, current_tag = image_full.split(":")
            if "-" in current_tag:
                arch, version = current_tag.split("-")
            else:
                arch = ""
        else:
            image, current_tag = image_full, "latest"
            arch = ""
        tags = get_latest_tag(image, arch)
        if not tags:
            continue

        formatted_tags = [t for t in tags if same_format(t, current_tag)]

        latest = formatted_tags[0]

        if latest != current_tag:
            result = ""
            result += (f"🔹 {svc}: {image_full}\n")
            result += (f"  ⚠️  Update available: {current_tag} → {latest}\n")
            send_telegram_message(bot_token,  result, image, latest)
        #else:
            #print(f"  ✅ Up-to-date")

def normalize_format(s):
    # Replace digits with 'D', letters with 'A', others stay as-is
    result = ''
    for char in s:
        if char.isdigit():
            result += 'D'
        elif char.isalpha():
            result += 'A'
        else:
            result += char
    return result

def same_format(s1, s2):
    return normalize_format(s1) == normalize_format(s2)

def send_telegram_message(bot_token, message, image, version):
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"

    callback_data = '{"a":"approve", "i":"' + image + '","v":"' + version + '"}'

    payload = {
        "chat_id": bot_chat_id,
        "text": message,

        "reply_markup": json.dumps({
            "inline_keyboard": [
                [
                    {"text": "✅ Approve", "callback_data": callback_data},
                    {"text": "❌ Reject", "callback_data": "reject"}
                ]
            ]
        })
    }

    response = requests.post(url, data=payload)
    if response.status_code != 200:
        print(f"❌ Failed to send message: {response.text}")
    else:
        print("✅ Message sent successfully.")
if __name__ == "__main__":
    main()
