# Docker image updater

> This project aims to provide a simple way of updating docker compose services image, by using telegram buttons API

# Cron jobs

0 14 * * * /usr/bin/python3 ~/dev/docker-compose-updater/check_image_updates.py >> /path/to/logfile.log 2>&1

5 14 * * * /usr/bin/python3 ~/dev/docker-compose-updater/check_image_updates.py >> /path/to/second.log 2>&1