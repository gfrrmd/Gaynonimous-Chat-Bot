"""Handler /start."""
import logging
from telegram import Update
from telegram.ext import ContextTypes
from services.database import get_or_create_user, is_user_banned, log_event
from utils.keyboards import main_keyboard, admin_keyboard
from utils.messages import WELCOME, BANNED_MESSAGE
from config.settings import ADMIN_IDS

logger = logging.getLogger(__name__)


async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if not user:
        return

    db_user = get_or_create_user(user.id, user.username, user.first_name)
    log_event("start", user.id, f"username={user.username}")

    if db_user.is_banned:
        await update.message.reply_text(BANNED_MESSAGE, parse_mode="Markdown")
        return

    # Pilih keyboard: admin atau user biasa
    if user.id in ADMIN_IDS:
        kb = admin_keyboard()
    else:
        kb = main_keyboard()

    await update.message.reply_text(
        WELCOME,
        parse_mode="Markdown",
        reply_markup=kb,
    )
