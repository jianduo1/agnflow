"""FastAPI后台任务节点实现。

本模块提供了支持后台任务处理的文章生成节点，包括大纲生成、内容编写和样式应用功能。
通过SSE队列实现实时进度更新，支持长时间运行的任务。
"""

import asyncio
import json
import uuid
from fastapi import FastAPI, BackgroundTasks, Form
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path

from agnflow.core import Node, Flow
from agnflow.agent.llm import call_llm
BASE_PATH = Path(__file__).parent

class GenerateOutline(Node):
    """大纲生成节点 - 为主题生成文章大纲"""

    def exec(self, state):
        """执行阶段：使用LLM生成文章大纲"""

        topic = state["topic"]
        prompt = f"""
创建一个关于 {topic} 的简单大纲。
最多包含 3 个主要部分（没有子部分）。

输出 YAML 格式，如下所示：

```yaml
sections:
    - 第一部分标题
    - 第二部分标题  
    - 第三部分标题
```"""
        result = call_llm(prompt, output_format="yaml")
        state["sections"] = result["sections"]

        # 通过SSE队列发送进度更新
        progress_msg = {"step": "outline", "progress": 33, "data": {"sections": result["sections"]}}
        state["sse_queue"].put_nowait(progress_msg)

        return "content_node"

class WriteContent(Node):
    """内容编写节点 - 批量为每个章节生成内容"""

    def exec(self, state):
        # 存储章节和sse_queue供exec使用
        self.sections = state.get("sections", [])
        self.sse_queue = state["sse_queue"]

        res_list = []
        for section in  self.sections:

            # 为单个章节生成简短段落
            prompt = f"""
为这个部分写一个简短的段落（最多100个字）：

{section}

要求：
- 用简单易懂的术语解释这个想法
- 使用日常语言，避免行话
- 保持非常简洁（不超过100个字）
- 包括一个简短的例子或类比
"""
            content = call_llm(prompt)

            # 为此章节发送进度更新
            current_section_index = self.sections.index(section) if section in self.sections else 0
            total_sections = len(self.sections)

            # 进度从33%（大纲后）到66%（样式前）
            # 每个章节贡献(66-33)/total_sections = 33/total_sections百分比
            section_progress = 33 + ((current_section_index + 1) * 33 // total_sections)

            progress_msg = {
                "step": "content", 
                "progress": section_progress, 
                "data": {
                    "section": section,
                    "completed_sections": current_section_index + 1,
                    "total_sections": total_sections
                }
            }
            self.sse_queue.put_nowait(progress_msg)

            res_list.append( f"## {section}\n\n{content}\n")

        # 后处理阶段：合并所有章节内容生成草稿
        draft = "\n".join(res_list)
        state["draft"] = draft
        return "style_node"

class ApplyStyle(Node):
    """样式应用节点 - 为文章应用特定风格"""
    def exec(self, state):
        # 准备阶段：获取草稿
        draft = state["draft"]

        # 执行阶段：为文章应用特定风格
        prompt = f"""
重写以下草稿，以对话式、吸引人的风格：

{draft}

让它：
- 对话式且温暖
- 包括启发性的问题，吸引读者
- 适当添加类比和隐喻
- 包括一个强有力的开头和结论
"""

        # 后处理阶段：保存最终文章并通过SSE队列发送完成更新
        state["final_article"] = call_llm(prompt)

        # 通过SSE队列发送完成更新
        progress_msg = {"step": "complete", "progress": 100, "data": {"final_article": state["final_article"]}}
        state["sse_queue"].put_nowait(progress_msg)


app = FastAPI()

app.mount("/assets", StaticFiles(directory=BASE_PATH / "assets"), name="assets")

active_jobs = {}


def run_article_workflow(job_id: str, topic: str):
    """Run the article workflow in background"""
    try:
        # Get the pre-created queue from active_jobs
        sse_queue = active_jobs[job_id]
        state = {"topic": topic, "sse_queue": sse_queue, "sections": [], "draft": "", "final_article": ""}

        # Run the workflow
        outline_node = GenerateOutline()
        content_node = WriteContent()
        style_node = ApplyStyle()
        article_flow = Flow()

        article_flow[outline_node >> content_node >> style_node]
        article_flow.run(state)

    except Exception as e:
        # Send error message
        error_msg = {"step": "error", "progress": 0, "data": {"error": str(e)}}
        if job_id in active_jobs:
            active_jobs[job_id].put_nowait(error_msg)


@app.post("/start-job")
async def start_job(background_tasks: BackgroundTasks, topic: str = Form(...)):
    """Start a new article generation job"""
    job_id = str(uuid.uuid4())

    # Create SSE queue and register job immediately
    sse_queue = asyncio.Queue()
    active_jobs[job_id] = sse_queue

    # Start background task
    background_tasks.add_task(run_article_workflow, job_id, topic)

    return {"job_id": job_id, "topic": topic, "status": "started"}


@app.get("/progress/{job_id}")
async def get_progress(job_id: str):
    """Stream progress updates via SSE"""

    async def event_stream():
        if job_id not in active_jobs:
            yield f"data: {json.dumps({'error': 'Job not found'})}\n\n"
            return

        sse_queue = active_jobs[job_id]

        # Send initial connection confirmation
        yield f"data: {json.dumps({'step': 'connected', 'progress': 0, 'data': {'message': 'Connected to job progress'}})}\n\n"

        try:
            while True:
                # Wait for next progress update
                try:
                    # Use asyncio.wait_for to avoid blocking forever
                    progress_msg = await asyncio.wait_for(sse_queue.get(), timeout=1.0)
                    yield f"data: {json.dumps(progress_msg)}\n\n"

                    # If job is complete, clean up and exit
                    if progress_msg.get("step") == "complete":
                        del active_jobs[job_id]
                        break

                except asyncio.TimeoutError:
                    # Send heartbeat to keep connection alive
                    yield f"data: {json.dumps({'heartbeat': True})}\n\n"

        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

    return StreamingResponse(
        event_stream(),
        media_type="text/plain",
        headers={"Cache-Control": "no-cache", "Connection": "keep-alive", "Content-Type": "text/event-stream"},
    )


@app.get("/")
async def get_index():
    """Serve the main page"""
    return FileResponse(BASE_PATH/"assets/index.html")


@app.get("/progress.html")
async def get_progress_page():
    """Serve the progress page"""
    return FileResponse(BASE_PATH/"assets/progress.html")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
