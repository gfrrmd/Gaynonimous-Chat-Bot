"""
Handler utama chat anonim:
- Cari Partner
- Next Partner
- Stop Chat
"""
import logging
from telegram import Update
from telegram.ext import ContextTypes
from services.database import (
    get_or_create_user, is_user_banned, log_event, add_report,
    increment_chat_count
)
from services.state_manager import state
from utils.keyboards import main_keyboard, chat_keyboard, waiting_keyboard, admin_keyboard
from utils.messages import (
    SEARCHING, PARTNER_FOUND, PARTNER_LEFT, CHAT_ENDED_BY_YOU,
    NEXT_SEARCHING, ALREADY_IN_QUEUE, ALREADY_IN_CHAT, NOT_IN_CHAT,
    BANNED_MESSAGE
)
from config.settings import ADMIN_IDS

logger = logging.getLogger(__name__)


def get_main_keyboard(user_id: int):
    """Kembalikan keyboard yang sesuai (admin atau user biasa)."""
    if user_id in ADMIN_IDS:
        return admin_keyboard()
    return main_keyboard()


async def find_partner(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if is_user_banned(user.id):
        await update.message.reply_text(BANNED_MESSAGE, parse_mode="Markdown")
        return

    if await state.is_in_chat(user.id):
        await update.message.reply_text(ALREADY_IN_CHAT, parse_mode="Markdown")
        return

    if await state.is_in_queue(user.id):
        await update.message.reply_text(ALREADY_IN_QUEUE, parse_mode="Markdown")
        return

    partner_id = await state.find_partner(user.id)

    if partner_id:
        await state.start_chat(user.id, partner_id)
        increment_chat_count(user.id)
        increment_chat_count(partner_id)
        log_event("chat_start", user.id, f"partner={partner_id}")

        await update.message.reply_text(
            PARTNER_FOUND, parse_mode="Markdown", reply_markup=chat_keyboard()
        )
        await context.bot.send_message(
            chat_id=partner_id,
            text=PARTNER_FOUND,
            parse_mode="Markdown",
            reply_markup=chat_keyboard(),
        )
    else:
        await state.add_to_queue(user.id)
        await update.message.reply_text(
            SEARCHING, parse_mode="Markdown", reply_markup=waiting_keyboard()
        )


async def stop_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    if await state.is_in_queue(user.id):
        await state.remove_from_queue(user.id)
        await update.message.reply_text(
            "\U0001f6d1 *Pencarian dibatalkan.*\nTekan *Cari Partner* kapan saja.",
            parse_mode="Markdown",
            reply_markup=get_main_keyboard(user.id),
        )
        return

    partner_id = await state.end_chat(user.id)
    if partner_id:
        log_event("chat_end", user.id, f"partner={partner_id}")
        await update.message.reply_text(
            CHAT_ENDED_BY_YOU,
            parse_mode="Markdown",
            reply_markup=get_main_keyboard(user.id),
        )
        await context.bot.send_message(
            chat_id=partner_id,
            text=PARTNER_LEFT,
            parse_mode="Markdown",
            reply_markup=get_main_keyboard(partner_id),
        )
    else:
        await update.message.reply_text(
            NOT_IN_CHAT, parse_mode="Markdown", reply_markup=get_main_keyboard(user.id)
        )


async def next_partner(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    partner_id = await state.end_chat(user.id)
    if partner_id:
        log_event("chat_next", user.id, f"prev_partner={partner_id}")
        await context.bot.send_message(
            chat_id=partner_id,
            text=PARTNER_LEFT,
            parse_mode="Markdown",
            reply_markup=get_main_keyboard(partner_id),
        )

    new_partner = await state.find_partner(user.id)
    if new_partner:
        await state.start_chat(user.id, new_partner)
        increment_chat_count(user.id)
        increment_chat_count(new_partner)
        await update.message.reply_text(
            PARTNER_FOUND, parse_mode="Markdown", reply_markup=chat_keyboard()
        )
        await context.bot.send_message(
            chat_id=new_partner,
            text=PARTNER_FOUND,
            parse_mode="Markdown",
            reply_markup=chat_keyboard(),
        )
    else:
        await state.add_to_queue(user.id)
        await update.message.reply_text(
            NEXT_SEARCHING, parse_mode="Markdown", reply_markup=waiting_keyboard()
        )
