# Telegram bot to play Connect Four against

## Play

[t.me/COPHEE_X4_BOT](https://t.me/COPHEE_X4_BOT)

## Deploy
- ```sh
  git clone https://github.com/CHC0815/c4tb.git
  ```

- ```sh
  cd c4tb
  ```

- ```sh
  vim .env
  ```
- add BOT_TOKEN=YOURTOKEN

- ```
  sudo docker compose up -d
  ```

## Tech stack
- [python3.12](https://www.python.org/)
- [sqlite3](https://docs.python.org/3/library/sqlite3.html) for game persistence
- [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot) as telegram api wrapper
- [pillow](https://pillow.readthedocs.io/en/stable/) for image creation
