"""Handler Report User dan Block."""
import logging
from telegram import Update
from telegram.ext import ContextTypes
from services.database import add_report, log_event
from services.state_manager import state
from utils.keyboards import main_keyboard, admin_keyboard
from utils.messages import REPORT_SENT, NOT_IN_CHAT, PARTNER_LEFT
from config.settings import ADMIN_IDS

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

    kb = admin_keyboard() if user.id in ADMIN_IDS else main_keyboard()
    await update.message.reply_text(REPORT_SENT, parse_mode="Markdown", reply_markup=kb)

    try:
        partner_kb = admin_keyboard() if partner_id in ADMIN_IDS else main_keyboard()
        await context.bot.send_message(
            chat_id=partner_id,
            text=PARTNER_LEFT,
            parse_mode="Markdown",
            reply_markup=partner_kb,
        )
    except Exception:
        pass
