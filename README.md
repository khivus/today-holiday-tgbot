# Telegram Holiday Bot

A Telegram bot built using aiogram==3.0.0b7 and other modules listed in the `requirements.txt` file. The bot sends a daily list of today's holidays at specified hours and includes various other cool features.
You can use last version of bot [there](https://t.me/Kakoy_Prazdnik_bot).

## Features

- Daily holiday updates
- List of tomorrow's holidays
- Search holidays by day and month or name
- Personalized settings
- Admin command features

## Installation

### Docker hosting

Requirements: Git, Docker Engine with the Docker Compose plugin, a Telegram bot
token from [BotFather](https://core.telegram.org/bots#botfather), and an existing
SQLite database backup compatible with this bot. The Docker entrypoint requires
a non-empty database; a backup is not included in the repository.

1. Clone the repository and create your configuration file:

   ```bash
   git clone https://github.com/khivus/today-holiday-tgbot.git
   cd today-holiday-tgbot
   cp .env.example .env
   ```

   Set `API_TOKEN` in `.env` to your bot token. Set `LOCAL_UID` and `LOCAL_GID`
   to the output of `id -u` and `id -g` for the user who owns the data directory.

2. Restore your database before starting the container:

   ```bash
   mkdir -p data/resources
   cp -n /path/to/your/backup.db data/resources/database.db
   ```

   Replace `/path/to/your/backup.db` with your backup's location. The configured
   user must have write access to `data/`, `data/resources/`, and the database
   file. Never replace the live database while the bot is running.

3. Set `ADMIN` in `src/constants.py` to your Telegram user ID. Open a chat with
   your bot and send `/start` before launching it so the bot can send its
   administrator notification during startup.

4. Build and start the bot:

   ```bash
   docker compose up -d --build
   docker compose logs -f --tail=100 bot
   ```

   If your account requires elevated permissions to access Docker, prefix these
   commands with `sudo`. Configure Docker to start on boot; on Linux hosts using
   systemd, run `sudo systemctl enable --now docker`.

The bot automatically restarts unless explicitly stopped. It uses Telegram long
polling, so no inbound ports, domain, or reverse proxy are needed. Run only one
instance per bot token. Scheduling uses UTC internally and the per-chat timezone
saved in the database.

Docker stores the database and `daily_stats.json` in `./data`, so they survive
container rebuilds and removal. This directory and `.env` are excluded from Git
and the Docker image.

To stop the bot, run `docker compose down`. After changing the token in `.env`,
run `docker compose up -d`. After changing source code, rebuild with
`docker compose up -d --build`.

For a consistent offline backup, stop the bot, copy `data/` to a safe location,
then start it again. Keep `data/` when updating the application.

### Without Docker

1. Clone the repository:

   ```bash
   git clone https://github.com/khivus/today-holiday-tgbot.git
   cd today-holiday-tgbot
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Set up your Telegram bot token:

   - Create a new bot on Telegram using [BotFather](https://core.telegram.org/bots#botfather).
   - Copy the generated token.
   - Export the token in your shell (the non-Docker application does not load `.env` automatically):

     ```
     export API_TOKEN=your_token_here
     ```

## Usage

Run the bot using the following command on Linux:

```bash
API_TOKEN=<your_token> python3 -m src
```
or using PowerShell:

```bash
$env:API_TOKEN = "<your_token>"
python -m src
```

## Configuration

The bot reads `API_TOKEN` from the environment through `src/config.py`.
Set the administrator ID (`ADMIN`) and review the default timezone (`tzinfo`)
in `src/constants.py`. Rebuild the Docker image after changing these files.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
