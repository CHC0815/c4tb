import logging
import os
import sqlite3

from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InputFile,
    InputMedia,
    InputMediaPhoto,
    PhotoSize,
    Update,
)
from telegram.ext import Application, CallbackQueryHandler, CommandHandler, ContextTypes

from bot.Game import ConnectFour, GameState

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)


def update_leaderboard(user_id, name, win, draw, winner) -> None:
    logger.info(f"Updating leaderboard for {user_id} ({name}) with win={win}, draw={draw}")
    db: sqlite3.Connection = sqlite3.connect("connectfourbot.db")
    db.cursor().execute(
        "INSERT OR IGNORE INTO leaderboard (id, name, wins, losses, draws) VALUES (?, ?, ?, ?, ?)",
        (user_id, name, 0, 0, 0),
    )
    if draw:
        db.cursor().execute(f"UPDATE leaderboard SET draws = draws + 1 WHERE id = ?", (user_id,))
    elif win:
        if winner == 1:
            db.cursor().execute("UPDATE leaderboard SET wins = wins + 1 WHERE id = ?", (user_id,))
        else:
            db.cursor().execute(
                "UPDATE leaderboard SET losses = losses + 1 WHERE id = ?", (user_id,)
            )
    db.commit()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    assert update.message is not None
    await update.message.reply_text("Hello, let's play some connect four!")


async def start_game(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    assert update.message is not None
    keyboard = [[InlineKeyboardButton("⬆️", callback_data=f"{i}") for i in range(7)]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    game = ConnectFour(update.message.chat_id)
    game.save()

    await update.message.reply_photo(game.render(), reply_markup=reply_markup)


async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    assert query is not None
    assert query.message is not None
    assert update.effective_chat is not None
    await query.answer()

    keyboard = [[InlineKeyboardButton("⬆️", callback_data=f"{i}") for i in range(7)]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    game = ConnectFour.load(query.message.chat_id)
    state: GameState = game.step(int(query.data or 0))

    if state.draw:
        await update.effective_chat.send_message("Draw!")
    elif state.win:
        await update.effective_chat.send_message(f"{state.winner} won!")
    game.save()

    if state.draw or state.win:
        assert update.effective_user is not None
        update_leaderboard(
            update.effective_user.id,
            update.effective_user.name,
            state.win,
            state.draw,
            state.winner,
        )

    await query.edit_message_media(
        media=InputMediaPhoto(
            media=game.render(),
        ),
        reply_markup=reply_markup if not state.draw and not state.win else None,
    )


async def top(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    assert update.message is not None
    assert update.effective_user is not None
    db: sqlite3.Connection = sqlite3.connect("connectfourbot.db")
    rows = db.cursor().execute("SELECT * FROM leaderboard ORDER BY wins DESC LIMIT 10").fetchall()
    s = ""
    for i, row in enumerate(rows):
        s += f"{i+1}. {row[1]}: w{row[2]} l{row[3]} d{row[4]}\n"

    you = (
        db.cursor()
        .execute(f"SELECT * FROM leaderboard WHERE id = {update.effective_user.id}")
        .fetchone()
    )
    if you is not None:
        s += f"\nYou: {you[2]}"
    await update.message.reply_text("Top 10 players:\n" + s)


def run():
    db: sqlite3.Connection = sqlite3.connect("connectfourbot.db")
    db.cursor().executescript(open("bot/setup.sql", "r").read())

    application = Application.builder().token(os.environ.get("BOT_TOKEN") or "").build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("start_game", start_game))
    application.add_handler(CallbackQueryHandler(button))
    application.add_handler(CommandHandler("top", top))

    application.run_polling(allowed_updates=Update.ALL_TYPES)
