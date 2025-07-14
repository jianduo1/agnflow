from fastapi import APIRouter
from fastapi.responses import FileResponse, JSONResponse

from agnflow.chatbot.chatbot_db import chat_db

router = APIRouter()

# --------- 聊天界面 ---------
@router.get("/zh")
async def get_chat_interface_zh(assets_path):
    return FileResponse(assets_path / "index_zh.html")

@router.get("/en")
async def get_chat_interface_en(assets_path):
    return FileResponse(assets_path / "index_en.html")


# --------- 聊天记录 ---------  
@router.get("/api/conversations")
async def get_conversations():
    rows = await chat_db.get_conversations()
    return JSONResponse([{"id": r[0], "created_at": r[1]} for r in rows])

@router.post("/api/conversation")
async def create_conversation():
    """创建会话"""
    conv_id = chat_db.create_conversation()
    return {"id": conv_id}

@router.delete("/api/conversation/{conv_id}")
async def delete_conversation(conv_id: str):
    """删除会话"""
    await chat_db.delete_conversation(conv_id)
    return {"status": "ok"}

@router.get("/api/conversation/{conv_id}")
async def get_conversation(conv_id: str):
    """获取会话历史记录"""
    messages = await chat_db.get_all_messages(conv_id)
    return JSONResponse(messages)


# --------- 消息 ---------
@router.delete("/api/message/{msg_id}")
async def delete_message(msg_id: int):
    await chat_db.delete_message(msg_id)
    return {"status": "ok"}
