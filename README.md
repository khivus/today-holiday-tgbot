# Telegram Holiday Bot

[![CodeFactor](https://www.codefactor.io/repository/github/khivus/today-holiday-tgbot/badge/main)](https://www.codefactor.io/repository/github/khivus/today-holiday-tgbot/overview/main)

A Telegram bot built using aiogram==3.0.0b7 and other modules listed in the `requirements.txt` file. The bot sends a daily list of today's holidays at specified hours and includes various other cool features.
You can use last version of bot [there](https://t.me/Kakoy_Prazdnik_bot).

## Features

- Daily holiday updates
- List of tomorrow's holidays
- Search holidays by day and month or name
- Personalized settings
- Admin command features 

## Installation

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
   - Create a `.env` file in the project root and add your token:

     ```
     API_TOKEN=your_token_here
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

Adjust the bot settings in the `config.py` file:
Make sure to configure the desired timezone and other settings within the `constants.py` file.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
