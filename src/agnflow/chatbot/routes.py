from agnflow.chatbot.web_node import WebNode
from fastapi import APIRouter, Request, UploadFile, File
from fastapi.responses import FileResponse, JSONResponse
import os
import uuid

from agnflow.chatbot.chatbot_db import chat_db
from agnflow.chatbot.config import assets_path
from agnflow.core import Node
router = APIRouter()

# --------- 聊天界面 ---------
@router.get("/zh")
async def get_chat_interface_zh():
    return FileResponse(assets_path / "index_zh.html")

@router.get("/en")
async def get_chat_interface_en():
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


# --------- 智能体 ---------
@router.get("/api/agent_nodes")
async def get_agent_nodes(request: Request):
    """获取所有智能体"""
    agent_nodes: list[WebNode] = request.app.state.agent_nodes
    return [node.get_agent_card_schema() for node in agent_nodes]


# --------- 图片上传 ---------
@router.post("/api/upload")
async def upload_image(file: UploadFile = File(...)):
    """图片上传接口，保存到本地，返回file_id"""
    upload_dir = "/tmp/agnx_uploads"
    os.makedirs(upload_dir, exist_ok=True)
    ext = os.path.splitext(file.filename)[-1].lower()
    file_id = str(uuid.uuid4()) + ext
    file_path = os.path.join(upload_dir, file_id)
    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)
    return {"file_id": file_id}

@router.get("/api/file/{file_id}")
async def get_uploaded_file(file_id: str):
    file_path = os.path.join("/tmp/agnx_uploads", file_id)
    if not os.path.exists(file_path):
        return JSONResponse({"error": "文件不存在"}, status_code=404)
    return FileResponse(file_path)
