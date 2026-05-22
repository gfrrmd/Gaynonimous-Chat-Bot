"""Handler Bantuan."""
from telegram import Update
from telegram.ext import ContextTypes
from utils.messages import HELP
from services.state_manager import state
from utils.keyboards import main_keyboard, chat_keyboard


async def help_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    is_in_chat = await state.is_in_chat(user.id)
    kb = chat_keyboard() if is_in_chat else main_keyboard()
    await update.message.reply_text(HELP, parse_mode="Markdown", reply_markup=kb)
