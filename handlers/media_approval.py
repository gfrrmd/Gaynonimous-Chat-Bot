"""
Callback handler untuk approve/reject media.
"""
import logging
from telegram import Update
from telegram.ext import ContextTypes
from services.state_manager import state
from services.media_service import send_media_to_receiver
from utils.messages import (
    MEDIA_APPROVED_SENDER, MEDIA_REJECTED_SENDER,
    MEDIA_APPROVED_RECEIVER, MEDIA_REJECTED_RECEIVER,
)

logger = logging.getLogger(__name__)


async def media_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data
    user_id = query.from_user.id

    if data.startswith("approve_media:"):
        approval_id = data.split(":", 1)[1]
        pending = await state.remove_pending_media(approval_id)

        if not pending:
            await query.edit_message_text("\u23f0 *Permintaan media sudah kadaluarsa atau tidak ditemukan.*", parse_mode="Markdown")
            return

        if pending.is_expired():
            await query.edit_message_text("\u23f0 *Media ini sudah kadaluarsa.*", parse_mode="Markdown")
            try:
                await context.bot.send_message(
                    chat_id=pending.sender_id,
                    text="\u23f0 *Media kamu sudah kadaluarsa sebelum diterima.*",
                    parse_mode="Markdown",
                )
            except Exception:
                pass
            return

        if user_id != pending.receiver_id:
            await query.answer("\u274c Bukan untukmu!", show_alert=True)
            return

        success = await send_media_to_receiver(context.bot, pending)
        if success:
            await query.edit_message_text(MEDIA_APPROVED_RECEIVER, parse_mode="Markdown")
            try:
                await context.bot.send_message(
                    chat_id=pending.sender_id,
                    text=MEDIA_APPROVED_SENDER,
                    parse_mode="Markdown",
                )
            except Exception:
                pass
        else:
            await query.edit_message_text("\u274c Gagal mengirimkan media. Coba lagi.", parse_mode="Markdown")

    elif data.startswith("reject_media:"):
        approval_id = data.split(":", 1)[1]
        pending = await state.remove_pending_media(approval_id)

        if not pending:
            await query.edit_message_text("\u23f0 *Permintaan media sudah kadaluarsa.*", parse_mode="Markdown")
            return

        if user_id != pending.receiver_id:
            await query.answer("\u274c Bukan untukmu!", show_alert=True)
            return

        await query.edit_message_text(MEDIA_REJECTED_RECEIVER, parse_mode="Markdown")
        try:
            await context.bot.send_message(
                chat_id=pending.sender_id,
                text=MEDIA_REJECTED_SENDER,
                parse_mode="Markdown",
            )
        except Exception:
            pass
