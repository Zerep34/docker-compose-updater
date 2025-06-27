# Docker image updater

> This project aims to provide a simple way of updating docker compose services image, by using telegram buttons API


# Requirements

In order to run the project you must :
- Create a `telegram_offset.txt` fill with the integer 0
- Create the telegram bot, look at the section
- Create a `.env` file from `.env.tpl` with your custom informations
- Your docker-compose services must be named by the image name
  ```yaml
    linuxserver/deluge:
      image: linuxserver/deluge:arm64v8-2.2.0
  ```

# Telegram Bot Creation

### 🔧 1. Create a Bot on Telegram

1. Open Telegram
2. Search for `@BotFather`
3. Send `/newbot`
4. Follow the prompts — you'll get a **Bot Token** like:

   ```
   123456789:ABCdefGhIjkLMnoPQRsTuVwxyz123456789
   ```

### 🔧 2. Get Your Chat ID

The easiest way is to send a message to your bot, then visit:

```
https://api.telegram.org/bot<YOUR_TOKEN>/getUpdates
```

Look for `"chat": { "id": ... }` in the JSON. That’s your `CHAT_ID`.

---

# Cron jobs

```bash
# Run every day at 14:00
0 14 * * * /usr/bin/python3 ~/dev/docker-compose-updater/check_image_updates.py >> /path/to/logfile.log 2>&1
# Run every day at 14:30
30 14 * * * /usr/bin/python3 ~/dev/docker-compose-updater/check_image_updates.py >> /path/to/second.log 2>&1`
```