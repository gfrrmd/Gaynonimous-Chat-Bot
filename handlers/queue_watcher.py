"""
Background task: watch queue dan auto-match user yang baru masuk.
Berjalan setiap 2 detik untuk mencocokkan pasangan di antrian.
"""
import asyncio
import logging
from telegram import Bot
from services.state_manager import state
from services.database import increment_chat_count, log_event
from utils.messages import PARTNER_FOUND
from utils.keyboards import chat_keyboard

logger = logging.getLogger(__name__)


async def queue_watcher(bot: Bot):
    """Terus-menerus mencoba mencocokkan user di antrian."""
    while True:
        await asyncio.sleep(2)
        try:
            async with state._lock:
                queue_copy = list(state._waiting_queue.keys())

            if len(queue_copy) < 2:
                continue

            matched_pairs = []
            used = set()

            for i, uid in enumerate(queue_copy):
                if uid in used:
                    continue
                blocked_by_uid = state._blocked.get(uid, set())
                for j in range(i + 1, len(queue_copy)):
                    vid = queue_copy[j]
                    if vid in used:
                        continue
                    if vid in blocked_by_uid:
                        continue
                    if uid in state._blocked.get(vid, set()):
                        continue
                    matched_pairs.append((uid, vid))
                    used.add(uid)
                    used.add(vid)
                    break

            for uid, vid in matched_pairs:
                async with state._lock:
                    state._waiting_queue.pop(uid, None)
                    state._waiting_queue.pop(vid, None)

                await state.start_chat(uid, vid)
                increment_chat_count(uid)
                increment_chat_count(vid)
                log_event("chat_start_queue", uid, f"partner={vid}")

                try:
                    await bot.send_message(
                        chat_id=uid,
                        text=PARTNER_FOUND,
                        parse_mode="Markdown",
                        reply_markup=chat_keyboard(),
                    )
                    await bot.send_message(
                        chat_id=vid,
                        text=PARTNER_FOUND,
                        parse_mode="Markdown",
                        reply_markup=chat_keyboard(),
                    )
                except Exception as e:
                    logger.error(f"Error notifikasi match: {e}")

        except Exception as e:
            logger.error(f"Error queue watcher: {e}")
