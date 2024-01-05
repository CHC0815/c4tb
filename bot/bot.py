import logging
import os
from io import BytesIO

from PIL import Image, ImageDraw, ImageFont
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

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)


def render_board(n):
    w, h = 400, 400
    img = Image.new("RGB", (w, h), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    draw.text((10, 10), f"{n}", fill="#888888")
    draw.rectangle(((20, 20), (380, 380)), fill="#000000", outline="red")
    bio = BytesIO()
    img.save(bio, "JPEG")
    bio.seek(0)
    return bio


async def start(update: Update, context: ContextTypes) -> None:
    assert update.message is not None
    await update.message.reply_text("Hello, let's play some connect four!")


async def start_game(update: Update, context: ContextTypes) -> None:
    assert update.message is not None
    keyboard = [[InlineKeyboardButton("⬆️", callback_data=f"{i}") for i in range(7)]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_photo(render_board(-2), reply_markup=reply_markup)


async def button(update: Update, context: ContextTypes) -> None:
    query = update.callback_query
    assert query is not None
    await query.answer()

    keyboard = [[InlineKeyboardButton("⬆️", callback_data=f"{i}") for i in range(7)]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_media(
        media=InputMediaPhoto(
            media=render_board(query.data or -1),
        ),
        reply_markup=reply_markup,
    )


def run():
    application = Application.builder().token(os.environ.get("BOT_TOKEN") or "").build()

    application.add_handler(CommandHandler("start", start))  # tpye: ignore
    application.add_handler(CommandHandler("start_game", start_game))
    application.add_handler(CallbackQueryHandler(button))

    application.run_polling(allowed_updates=Update.ALL_TYPES)
