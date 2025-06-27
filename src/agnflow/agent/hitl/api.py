from fastapi import APIRouter, HTTPException, FastAPI
from pydantic import BaseModel
from typing import Optional, Dict, Any, Literal
import uuid


def get_hitl_router(prefix: str = "/hitl", tags: list[str] = ["HumanInTheLoop"]) -> APIRouter:
    """
    # 获取 Human-in-the-Loop 审核流程的 FastAPI Router。

    ### 简单使用: `app.include_router(get_hitl_router())`

    ### 使用说明
    1. 在你的 FastAPI 项目中：
        ```python
        from agnflow.agent.hitl.api import get_hitl_router
        app.include_router(get_hitl_router())
        ```

    2. 启动服务后，访问 http://127.0.0.1:8000/docs ，即可在 Swagger UI 上测试如下接口：
        - POST /hitl/tasks/ 创建审核任务
        - GET /hitl/tasks/{task_id} 查询任务状态
        - POST /hitl/tasks/{task_id}/submit 提交审核结果

    3. curl 测试示例：

    ```bash
    # 创建任务
    response=$(curl -s -X POST "http://127.0.0.1:8000/hitl/tasks/" -H "Content-Type: application/json" -d '{"prompt": "请审核数据", "input_data": {"foo": 123}}')
    echo $response | jq
    task_id=$(jq -r '.task_id' <<< "$response")

    # 查询任务
    curl -s "http://127.0.0.1:8000/hitl/tasks/$task_id" | jq

    # 提交审核
    curl -s -X POST "http://127.0.0.1:8000/hitl/tasks/$task_id/submit" -H "Content-Type: application/json" -d '{"approve": true, "result": "同意"}' | jq
    ```

    """
    router = APIRouter(prefix=prefix, tags=tags)
    # 内存任务存储
    tasks: Dict[str, Dict[str, Any]] = {}

    class CreateTaskRequest(BaseModel):
        prompt: str
        input_data: Optional[Any] = None

    class TaskResponse(BaseModel):
        task_id: str
        prompt: str
        input_data: Optional[Any]
        status: Literal["pending", "approved", "rejected"]
        result: Optional[Any] = None

    class SubmitTaskRequest(BaseModel):
        result: Optional[Any] = None
        approve: bool

    @router.post("/tasks/", response_model=TaskResponse)
    async def create_task(req: CreateTaskRequest):
        """创建审核任务"""
        task_id = str(uuid.uuid4())
        tasks[task_id] = {"prompt": req.prompt, "input_data": req.input_data, "status": "pending", "result": None}
        print(f"[HITL] 创建任务: {task_id}\n  prompt: {req.prompt}\n  input_data: {req.input_data}")
        return TaskResponse(task_id=task_id, prompt=req.prompt, input_data=req.input_data, status="pending")

    @router.get("/tasks/{task_id}", response_model=TaskResponse)
    async def get_task(task_id: str):
        """查询任务状态"""
        task = tasks.get(task_id)
        if not task:
            print(f"[HITL] 查询任务: {task_id} 未找到")
            raise HTTPException(status_code=404, detail="Task not found")
        print(f"[HITL] 查询任务: {task_id} 状态: {task['status']}")
        return TaskResponse(task_id=task_id, **task)

    @router.post("/tasks/{task_id}/submit", response_model=TaskResponse)
    async def submit_task(task_id: str, req: SubmitTaskRequest):
        """提交审核结果"""
        task = tasks.get(task_id)
        if not task:
            print(f"[HITL] 提交任务: {task_id} 未找到")
            raise HTTPException(status_code=404, detail="Task not found")
        if task["status"] != "pending":
            print(f"[HITL] 提交任务: {task_id} 已处理，当前状态: {task['status']}")
            raise HTTPException(status_code=400, detail="Task already processed")
        task["status"] = "approved" if req.approve else "rejected"
        task["result"] = req.result
        print(f"[HITL] 提交任务: {task_id} -> 状态: {task['status']}\n  result: {req.result}")
        return TaskResponse(task_id=task_id, **task)

    return router


# ================= 示例代码 =================
if __name__ == "__main__":
    import uvicorn

    app = FastAPI()
    app.include_router(get_hitl_router())
    print("\n访问 http://127.0.0.1:8000/docs 进行交互式测试")
    uvicorn.run(app, host="0.0.0.0", port=8000)

"""
"""
