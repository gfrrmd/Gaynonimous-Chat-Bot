"""
State manager - menyimpan semua state runtime di memori:
- waiting_queue: user yang menunggu partner
- active_chats: user yang sedang chat
- pending_media: media yang menunggu approval
- blocked_users: daftar blokir antar user
"""
import asyncio
import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Set, Tuple
from config.settings import MEDIA_APPROVAL_TIMEOUT

logger = logging.getLogger(__name__)


@dataclass
class PendingMedia:
    """Pending media approval."""
    approval_id: str
    sender_id: int
    receiver_id: int
    file_id: str
    media_type: str
    caption: Optional[str]
    created_at: datetime
    expires_at: datetime

    def is_expired(self) -> bool:
        return datetime.utcnow() >= self.expires_at


class StateManager:
    def __init__(self):
        self._waiting_queue: Dict[int, datetime] = {}
        self._active_chats: Dict[int, int] = {}
        self._pending_media: Dict[str, PendingMedia] = {}
        self._blocked: Dict[int, Set[int]] = {}
        self._lock = asyncio.Lock()
        self._approval_counter = 0

    async def add_to_queue(self, user_id: int) -> None:
        async with self._lock:
            self._waiting_queue[user_id] = datetime.utcnow()

    async def remove_from_queue(self, user_id: int) -> None:
        async with self._lock:
            self._waiting_queue.pop(user_id, None)

    async def is_in_queue(self, user_id: int) -> bool:
        async with self._lock:
            return user_id in self._waiting_queue

    async def find_partner(self, user_id: int) -> Optional[int]:
        async with self._lock:
            blocked_by_me = self._blocked.get(user_id, set())
            candidates = [
                uid for uid in self._waiting_queue
                if uid != user_id
                and uid not in blocked_by_me
                and user_id not in self._blocked.get(uid, set())
            ]
            if not candidates:
                return None
            partner_id = min(candidates, key=lambda uid: self._waiting_queue[uid])
            del self._waiting_queue[partner_id]
            self._waiting_queue.pop(user_id, None)
            return partner_id

    async def queue_count(self) -> int:
        async with self._lock:
            return len(self._waiting_queue)

    async def start_chat(self, user1: int, user2: int) -> None:
        async with self._lock:
            self._active_chats[user1] = user2
            self._active_chats[user2] = user1

    async def end_chat(self, user_id: int) -> Optional[int]:
        async with self._lock:
            partner = self._active_chats.pop(user_id, None)
            if partner is not None:
                self._active_chats.pop(partner, None)
            return partner

    async def get_partner(self, user_id: int) -> Optional[int]:
        async with self._lock:
            return self._active_chats.get(user_id)

    async def is_in_chat(self, user_id: int) -> bool:
        async with self._lock:
            return user_id in self._active_chats

    async def active_chat_count(self) -> int:
        async with self._lock:
            return len(self._active_chats) // 2

    async def create_pending_media(
        self,
        sender_id: int,
        receiver_id: int,
        file_id: str,
        media_type: str,
        caption: Optional[str] = None,
    ) -> str:
        async with self._lock:
            self._approval_counter += 1
            approval_id = f"media_{sender_id}_{self._approval_counter}"
            now = datetime.utcnow()
            pending = PendingMedia(
                approval_id=approval_id,
                sender_id=sender_id,
                receiver_id=receiver_id,
                file_id=file_id,
                media_type=media_type,
                caption=caption,
                created_at=now,
                expires_at=now + timedelta(seconds=MEDIA_APPROVAL_TIMEOUT),
            )
            self._pending_media[approval_id] = pending
            return approval_id

    async def get_pending_media(self, approval_id: str) -> Optional[PendingMedia]:
        async with self._lock:
            return self._pending_media.get(approval_id)

    async def remove_pending_media(self, approval_id: str) -> Optional[PendingMedia]:
        async with self._lock:
            return self._pending_media.pop(approval_id, None)

    async def get_expired_media(self) -> List[PendingMedia]:
        async with self._lock:
            expired = [pm for pm in self._pending_media.values() if pm.is_expired()]
            for pm in expired:
                del self._pending_media[pm.approval_id]
            return expired

    async def pending_media_count(self) -> int:
        async with self._lock:
            return len(self._pending_media)

    async def block_user(self, user_id: int, target_id: int) -> None:
        async with self._lock:
            if user_id not in self._blocked:
                self._blocked[user_id] = set()
            self._blocked[user_id].add(target_id)

    async def is_blocked(self, user_id: int, target_id: int) -> bool:
        async with self._lock:
            return target_id in self._blocked.get(user_id, set())

    async def get_blocked_list(self, user_id: int) -> Set[int]:
        async with self._lock:
            return set(self._blocked.get(user_id, set()))


# Singleton
state = StateManager()
