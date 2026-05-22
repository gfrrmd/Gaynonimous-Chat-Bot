"""Handler Report User dan Block."""
import logging
from telegram import Update
from telegram.ext import ContextTypes
from services.database import add_report, log_event, is_user_banned
from services.state_manager import state
from utils.keyboards import main_keyboard
from utils.messages import REPORT_SENT, NOT_IN_CHAT

logger = logging.getLogger(__name__)


async def report_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    partner_id = await state.get_partner(user.id)

    if not partner_id:
        await update.message.reply_text(NOT_IN_CHAT, parse_mode="Markdown")
        return

    add_report(reporter_id=user.id, reported_id=partner_id, reason="User report from chat")
    log_event("report", user.id, f"reported={partner_id}")

    await state.block_user(user.id, partner_id)
    await state.end_chat(user.id)

    await update.message.reply_text(REPORT_SENT, parse_mode="Markdown", reply_markup=main_keyboard())

    try:
        from utils.messages import PARTNER_LEFT
        await context.bot.send_message(
            chat_id=partner_id,
            text=PARTNER_LEFT,
            parse_mode="Markdown",
            reply_markup=main_keyboard(),
        )
    except Exception:
        pass
