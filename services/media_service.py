"""
Media approval service.
"""
import asyncio
import logging
from telegram import Bot, InlineKeyboardMarkup, InlineKeyboardButton
from services.state_manager import state, PendingMedia
from config.settings import MEDIA_APPROVAL_TIMEOUT

logger = logging.getLogger(__name__)


def build_approval_keyboard(approval_id: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("\u2705 Lihat Media", callback_data=f"approve_media:{approval_id}"),
            InlineKeyboardButton("\u274c Tolak", callback_data=f"reject_media:{approval_id}"),
        ]
    ])


async def send_media_to_receiver(bot: Bot, pending: PendingMedia) -> bool:
    """Kirim media dari file_id ke receiver setelah disetujui."""
    try:
        if pending.media_type == "photo":
            await bot.send_photo(
                chat_id=pending.receiver_id,
                photo=pending.file_id,
                caption=pending.caption,
            )
        elif pending.media_type == "video":
            await bot.send_video(
                chat_id=pending.receiver_id,
                video=pending.file_id,
                caption=pending.caption,
            )
        elif pending.media_type == "animation":
            await bot.send_animation(
                chat_id=pending.receiver_id,
                animation=pending.file_id,
                caption=pending.caption,
            )
        elif pending.media_type == "document":
            await bot.send_document(
                chat_id=pending.receiver_id,
                document=pending.file_id,
                caption=pending.caption,
            )
        return True
    except Exception as e:
        logger.error(f"Gagal mengirim media: {e}")
        return False


async def cleanup_expired_media(bot: Bot):
    """Background task untuk membersihkan media yang kadaluarsa."""
    while True:
        await asyncio.sleep(10)
        try:
            expired_list = await state.get_expired_media()
            for pending in expired_list:
                logger.info(f"Media expired: {pending.approval_id}")
                try:
                    await bot.send_message(
                        chat_id=pending.sender_id,
                        text=(
                            "\u23f0 *Media kamu kadaluarsa.*\n"
                            f"Lawan bicara tidak merespons dalam {MEDIA_APPROVAL_TIMEOUT} detik. "
                            "Media tidak terkirim."
                        ),
                        parse_mode="Markdown",
                    )
                except Exception:
                    pass
                try:
                    await bot.send_message(
                        chat_id=pending.receiver_id,
                        text=(
                            "\u23f0 *Permintaan media kadaluarsa.*\n"
                            "Kamu tidak merespons dalam waktu yang ditentukan."
                        ),
                        parse_mode="Markdown",
                    )
                except Exception:
                    pass
        except Exception as e:
            logger.error(f"Error cleanup expired media: {e}")
