from typing import IO, Annotated as A, Literal, Union
import base64
from pathlib import Path
import os
import uuid
from agnflow.agent.msg import ImageMsg
import aiohttp

from agnflow.agent.zhipu import (
    zhipu_chat,
    zhipu_audio,
    zhipu_image,
    zhipu_video,
    msg_texts,
    msg_images,
    query_train_info,
    pprint,
)
from agnflow.chatbot.web_node import WebNode
from agnflow.chatbot.type import textarea, json, file

writing_prompt = """
- 上下文：我想推广公司的新产品。我的公司名为：[公司名称]，新产品名为：[产品名称]，是一款面向[目标用户群体]的产品类型]。
- 目标：帮我创建一条[平台名称]平台的帖子，目的是吸引人们点击产品链接进行学习和体验。
- 风格：参照[参考品牌]等成功公司的宣传风格，它们在推广类似产品时的文案风格，同时结合[平台名称]的文案风格。
- 语调：[语调风格，如：说服性、轻松幽默、专业权威等]
- 受众：[目标受众描述，包括年龄、兴趣、消费习惯等]
- 响应：保持[平台名称]帖子简洁而深具影响力，注意要使用emoji表情，
    **平台链接以markdown格式输出显示**：[产品名称]（[产品链接]）。
    **平台logo放在文案最下方**：[logo图片链接]

请根据以下具体信息生成文案：
"""


class WritingNode(WebNode):
    """✍🏻 智能写作"""

    async def aexec(
        self,
        content: A[textarea, "写作内容"] = "",
        company_name: A[str, "公司名称（可选）"] = "",
        product_name: A[str, "产品名称（可选）"] = "",
        target_audience: A[str, "目标用户群体（可选）"] = "",
        product_type: A[str, "产品类型（可选）"] = "",
        platform: A[str, "发布平台（可选）"] = "",
        reference_brand: A[str, "参考品牌（可选）"] = "",
        tone: A[
            Literal["专业权威", "轻松幽默", "温暖亲切", "简洁直接", "故事性强", "科技感强"], "语调风格"
        ] = "专业权威",
        product_link: A[str, "产品链接（可选）"] = "",
        platform_logo: A[str, "平台 Logo（可选）"] = "",
    ):
        """智能写作节点 - 根据用户提供的信息生成高质量文案

        支持多种写作场景：
        1. 产品推广文案
        2. 社交媒体帖子
        3. 品牌故事
        4. 活动宣传
        等...
        """
        # 构建提示词
        context_parts = []

        # 基础写作需求
        context_parts.append(f"写作内容：{content}" if content else "")

        # 产品相关信息（如果有）
        product_info = []
        if company_name:
            product_info.append(f"公司名称：{company_name}")
        if product_name:
            product_info.append(f"产品名称：{product_name}")
        if target_audience:
            product_info.append(f"目标用户：{target_audience}")
        if product_type:
            product_info.append(f"产品类型：{product_type}")
        if product_info:
            context_parts.append("产品信息：\n" + "\n".join(product_info))

        # 发布平台相关（如果有）
        platform_info = []
        if platform:
            platform_info.append(f"发布平台：{platform}")
        if reference_brand:
            platform_info.append(f"参考品牌：{reference_brand}")
        if platform_info:
            context_parts.append("发布信息：\n" + "\n".join(platform_info))

        # 写作风格
        style_info = [f"语调风格：{tone}"]
        context_parts.append("写作风格：\n" + "\n".join(style_info))

        # 链接和素材（如果有）
        media_info = []
        if product_link:
            media_info.append(f"产品链接：{product_link}")
        if platform_logo:
            media_info.append(f"平台Logo：{platform_logo}")
        if media_info:
            context_parts.append("媒体资源：\n" + "\n".join(media_info))

        # 组合最终提示词
        prompt = """请根据以下信息生成一篇优质文案。

要求：
1. 根据提供的信息生成符合场景的文案
2. 如果提供了产品信息，确保文案突出产品核心价值
3. 如果指定了发布平台，遵循该平台的文案风格
4. 适当使用 emoji 增强表现力
5. 如果提供了链接，以 markdown 格式嵌入
6. 如果提供了 Logo，放在文案末尾

具体信息：
""" + "\n\n".join(
            filter(None, context_parts)
        )

        # 调用 LLM 生成文案
        conversation = self.state.get("conversation")
        await self.send_text(type="start", content="")

        try:
            # 使用智谱API生成文案
            generator = zhipu_chat(messages=prompt, model="glm-4", mode="stream")
            full_response = ""
            for chunk in generator():
                full_response += chunk
                await self.send_text(type="chunk", content=chunk)

            # 保存对话历史
            await self.save_message(conversation=conversation, role="user", content=prompt)
            await self.save_message(conversation=conversation, role="assistant", content=full_response)

        except Exception as e:
            error_msg = f"生成文案时发生错误: {str(e)}"
            print(error_msg)
            await self.send_text(type="error", content=error_msg)
        finally:
            await self.send_text(type="end", content="")


class VisionNode(WebNode):
    """👀 视觉分析"""

    SUPPORTED_FORMATS = (".jpg", ".jpeg", ".png", ".gif", ".webp")
    MAX_FILE_SIZE = 10 * 1024 * 1024
    UPLOAD_DIR = "/tmp/agnx_uploads"

    async def aexec(
        self,
        image_file: A[file, "上传图片ID"] = None,  # 保留file类型参数，便于schema和前端自动化
        image_url: A[str, "图片链接"] = None,
        query_type: A[
            Literal["图像描述生成", "图像分类", "视觉推理", "视觉问答", "图像情感分析", "社交媒体内容生成"], "分析类型"
        ] = "图像描述生成",
    ):
        conversation = self.state.get("conversation")
        await self.send_text(type="start", content="")
        try:
            image_data = None
            # 优先从self.state获取file_id，否则用入参
            image_file_id = self.state.get("image_file_id") or image_file
            # 兼容file_id为list的情况
            if isinstance(image_file_id, list):
                image_file_id = image_file_id[0] if image_file_id else None
            image_url_state = self.state.get("image_url") or image_url
            query_type_state = self.state.get("query_type")
            file_path = None
            # 1. 优先处理本地上传图片
            if image_file_id:
                file_path = os.path.join(self.UPLOAD_DIR, image_file_id)
                if not os.path.exists(file_path):
                    raise ValueError(f"文件不存在: {file_path}")
            # 2. 处理远程图片链接，下载到本地
            elif image_url_state:
                ext = os.path.splitext(image_url_state)[-1].lower()
                if ext not in self.SUPPORTED_FORMATS:
                    ext = ".jpg"  # 默认jpg
                file_id = str(uuid.uuid4()) + ext
                file_path = os.path.join(self.UPLOAD_DIR, file_id)
                os.makedirs(self.UPLOAD_DIR, exist_ok=True)
                async with aiohttp.ClientSession() as session:
                    async with session.get(image_url_state) as resp:
                        if resp.status != 200:
                            raise ValueError(f"图片下载失败: {image_url_state}")
                        with open(file_path, "wb") as f:
                            f.write(await resp.read())
            else:
                raise ValueError("请上传图片或填写图片链接")
            # 统一后续处理
            with open(file_path, "rb") as f:
                content = f.read()
            if len(content) > self.MAX_FILE_SIZE:
                raise ValueError(f"文件大小超过限制（{self.MAX_FILE_SIZE/1024/1024}MB）")
            ext = os.path.splitext(file_path)[-1].lower()
            if ext not in self.SUPPORTED_FORMATS:
                raise ValueError(f"不支持的文件格式，支持的格式：{', '.join(self.SUPPORTED_FORMATS)}")
            image_data = f"data:image/{ext[1:]};base64," + base64.b64encode(content).decode("utf-8")
            qt = query_type_state or query_type
            image_message = {
                "图像描述生成": "对图像进行详细描述，包括主要元素、场景、颜色等。",
                "图像分类": "请分析图像中的主要对象类别。",
                "视觉推理": "请根据图像内容进行视觉推理分析。",
                "视觉问答": "请回答关于图像内容的具体问题。",
                "图像情感分析": "分析并描述图像所传达的主要情感或情绪。",
                "社交媒体内容生成": "根据图片内容创作一篇吸引人的社交媒体文案。",
            }.get(qt, "对图像进行详细描述。")
            # 拼接用户输入内容
            user_content = self.state.get("content")
            if user_content:
                image_message = f"{image_message}\n用户补充说明：{user_content}"
            msg = {
                "role": "user",
                "content": [
                    {"type": "text", "text": image_message},
                    {"type": "image_url", "image_url": {"url": image_data}},
                ],
            }
            # 修正：zhipu_chat要求messages为list
            generator = zhipu_chat(messages=[msg], model="vision", mode="stream")
            full_response = ""
            for chunk in generator():
                full_response += chunk
                await self.send_text(type="chunk", content=chunk)
            save_msg = msg.copy()
            save_msg["content"][1]["image_url"]["url"] = "[图片数据]"
            # 修正：保存消息时content需为str，不能为dict

            # 优先保存前端传来的拼接字符串
            await self.save_message(conversation=conversation, role="user", content=user_content)
            await self.save_message(conversation=conversation, role="assistant", content=full_response)
        except Exception as e:
            error_msg = f"处理图片时发生错误: {str(e)}"
            print(f"❌ 错误: {error_msg}")
            await self.send_text(type="error", content=error_msg)
        finally:
            await self.send_text(type="end", content="")


if __name__ == "__main__":
    import asyncio
    import json
    import websockets

    data1 = {
        "conversation": "377d157d03-47b-89b6-b16153e8733",
        "type": "message",
        "content": "好",
        "entry_action": "vision_node",
    }

    data2 = {
        "conversation": "377d157d03-47b-89b6-b16153e873d3",
        "type": "message",
        "content": "好",
        "entry_action": "vision_node",
    }

    async def hello():
        uri = "ws://localhost:8000/ws"
        async with websockets.connect(uri) as websocket:
            await websocket.send(json.dumps(data1))
            await asyncio.sleep(1)
            await websocket.send(json.dumps(data2))

    asyncio.run(hello())
