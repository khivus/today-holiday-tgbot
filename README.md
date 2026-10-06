# Telegram Holiday Bot

A Telegram bot built using aiogram==3.0.0b7 and other modules listed in the `requirements.txt` file. The bot sends a daily list of today's holidays at specified hours and includes various other cool features.
You can use last version of bot [there](https://t.me/Kakoy_Prazdnik_bot).

## Features

- Daily holiday updates
- List of tomorrow's holidays
- Search holidays by day and month or name
- Personalized settings
- Admin command features
- Rule-based dates for popular Russian and international secular holidays

## Плавающие светские праздники

Даты рассчитываются по номеру дня недели в месяце, без таблиц дат для отдельных
лет. Все названия в сообщениях бота — на русском языке.

| Праздник | Правило |
| --- | --- |
| День матери в России | Последнее воскресенье ноября |
| День отца в России | Третье воскресенье октября |
| День Военно-Морского Флота России | Последнее воскресенье июля |
| День железнодорожника | Первое воскресенье августа |
| День строителя | Второе воскресенье августа |
| День физкультурника в России | Вторая суббота августа |
| День Воздушного Флота России | Третье воскресенье августа |
| День шахтера | Последнее воскресенье августа |
| День танкиста | Второе воскресенье сентября |
| День работников леса | Третье воскресенье сентября |
| День машиностроителя | Последнее воскресенье сентября |
| День работника сельского хозяйства и перерабатывающей промышленности в России | Второе воскресенье октября |
| День автомобилиста | Последнее воскресенье октября |
| День Мартина Лютера Кинга в США | Третий понедельник января |
| День президентов США | Третий понедельник февраля |
| День матери в США | Второе воскресенье мая |
| День памяти в США | Последний понедельник мая |
| День отца в США | Третье воскресенье июня |
| День труда в США и Канаде | Первый понедельник сентября |
| День благодарения в США | Четвёртый четверг ноября |
| День благодарения в Канаде | Второй понедельник октября |

Также добавлен День работника транспорта в России. У него фиксированная дата —
20 ноября, согласно [Министерству транспорта России](https://mintrans.gov.ru/press-center/news/9675).
Правила для государственных праздников США приведены на
[сайте OPM](https://www.opm.gov/policy-data-oversight/pay-leave/pay-administration/fact-sheets/holidays-work-schedules-and-pay/),
для канадских — на [сайте правительства Канады](https://www.canada.ca/en/library-archives/services/public/visit/holiday-closures.html).

При каждом запуске бот обновляет даты на текущий год до начала обработки
сообщений. Планировщик повторяет пересчёт при смене года по часовому поясу
`tzinfo` (по умолчанию UTC), перед первой рассылкой. Если бот был выключен на
Новый год, даты обновятся при следующем запуске. При ошибке планировщик повторяет
попытку. Команда администратора `/run_parser` также пересчитывает эти даты.
Повторный пересчёт заменяет прежние записи без создания дублей и сохраняет
остальные праздники. Новых религиозных праздников не добавлено; существующий
расчёт религиозных дат продолжает работать.

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

Temporary Telegram disconnections and DNS failures during polling are logged as
warnings and retried automatically with backoff. A `Connection established` log
confirms recovery. Scheduled sends also retry temporary network/server failures
and rate limits. Successful scheduled-send summaries use the INFO level and are
hidden by the default WARNING log level.

If Telegram returns `chat not found`, the inaccessible chat is removed from the
database. If it returns `TOPIC_CLOSED`, mailing is disabled while the chat's
settings are kept. Reopen the topic, then enable mailing again through
`/settings`. Other bad requests remain errors and keep the subscription intact.

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
