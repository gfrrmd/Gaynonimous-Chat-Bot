"""Handler Profil Saya."""
from telegram import Update
from telegram.ext import ContextTypes
from services.database import get_or_create_user
from utils.keyboards import main_keyboard
from utils.messages import profile_text


async def profile_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    db_user = get_or_create_user(user.id, user.username, user.first_name)
    member_since = db_user.created_at.strftime("%d %B %Y") if db_user.created_at else "Tidak diketahui"
    text = profile_text(user.id, db_user.total_chats, member_since)
    await update.message.reply_text(text, parse_mode="Markdown", reply_markup=main_keyboard())
