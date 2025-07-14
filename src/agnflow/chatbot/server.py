from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from agnflow.chatbot.routes import router
from agnflow.chatbot.websocket import websocket_endpoint
from agnflow.chatbot.config import assets_path

class Server:
    """Chatbot Server"""

    def __init__(self):
        # 创建FastAPI应用
        self.app = FastAPI(lifespan=self.lifespan)

        # 添加静态文件
        self.app.mount("/assets", StaticFiles(directory=str(assets_path)), name="assets")

        # 添加CORS中间件
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

        # 添加路由
        self.app.include_router(router)
        self.app.add_websocket_route("/ws", websocket_endpoint)

    @asynccontextmanager
    async def lifespan(self, app):
        from agnflow.chatbot.chatbot_db import chat_db

        # 初始化数据库
        await chat_db.init_db()
        yield

    def run(self, host: str = "0.0.0.0", port: int = 8000):
        # 运行服务器
        uvicorn.run(self.app, host=host, port=port)


if __name__ == "__main__":
    server = Server()
    print("Server started: http://localhost:8000/en")
    print("Server started: http://localhost:8000/zh")
    server.run()
