from typing import Any, List, Optional, Tuple, Literal, TypedDict
import aiosqlite
import uuid


class Chat(TypedDict):
    id: int
    conversation: str
    role: str
    content: str
    timestamp: str


class ChatbotDB:
    """聊天记录数据库"""

    def __init__(self, db_path: str = "chatbot.sqlite3") -> None:
        """初始化数据库"""
        self.db_path: str = db_path

    async def _execute(
        self, sql: str, params: Tuple = (), action: Literal["fetchone", "fetchall", "update"] = "fetchall"
    ) -> Optional[Any]:
        """执行SQL语句"""
        async with aiosqlite.connect(self.db_path) as conn:
            c = await conn.cursor()
            await c.execute(sql, params)
            result = None
            if action == "fetchone":
                result = await c.fetchone()
            elif action == "fetchall":
                result = await c.fetchall()
            elif action == "update":
                await conn.commit()
            return result

    async def init_db(self) -> None:
        sql = """CREATE TABLE IF NOT EXISTS chat_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            conversation TEXT NOT NULL,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )"""
        await self._execute(sql=sql, action="update")

    def create_conversation(self) -> str:
        """创建会话"""
        return str(uuid.uuid4())

    async def get_conversations(self) -> List[Tuple[str, str]]:
        """获取所有会话"""
        sql = "SELECT conversation, MIN(timestamp) as created_at FROM chat_history GROUP BY conversation ORDER BY created_at ASC"
        return await self._execute(sql=sql, action="fetchall")

    async def delete_conversation(self, conversation: str) -> None:
        """删除会话"""
        await self._execute("DELETE FROM chat_history WHERE conversation=?", (conversation,), action="update")

    async def delete_message(self, msg_id: int) -> None:
        """删除消息"""
        await self._execute("DELETE FROM chat_history WHERE id=?", (msg_id,), action="update")

    async def save_message(self, conversation: str, role: str, content: str) -> int:
        """保存消息"""
        sql = "INSERT INTO chat_history (conversation, role, content) VALUES (?, ?, ?)"
        async with aiosqlite.connect(self.db_path) as conn:
            c = await conn.cursor()
            await c.execute(sql, (conversation, role, content))
            await conn.commit()
            msg_id = c.lastrowid
            return msg_id

    async def get_all_messages(self, conversation: str) -> list[Chat]:
        """获取所有消息"""
        sql = "SELECT id, role, content, timestamp FROM chat_history WHERE conversation=? ORDER BY id ASC"
        rows = await self._execute(sql=sql, params=(conversation,), action="fetchall")
        return [{"id": r[0], "role": r[1], "content": r[2], "timestamp": r[3]} for r in rows]


chat_db = ChatbotDB()

if __name__ == "__main__":
    import asyncio
    async def main():
        # 初始化数据库
        await chat_db.init_db()
        print(chat_db.get_all_messages())

    asyncio.run(main())

