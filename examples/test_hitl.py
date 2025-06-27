from fastapi import FastAPI
from agnflow import Node, Flow
import uvicorn

from agnflow.agent.hitl.cli import human_in_the_loop
from agnflow.agent.hitl.api import get_hitl_router

def review_node(state):
    result, approved = human_in_the_loop("请人工审核本节点数据", input_data=state)
    if approved:
        return {"review_result": result, "approved": True}
    else:
        return "exit", {"review_result": result, "approved": False}


def test_hitl_cli():
    n1 = Node("review", exec=review_node)
    n2 = Node("next", exec=lambda state: print("流程继续", state))
    n1 >> n2
    flow = Flow(n1, name="hitl_demo")
    flow.run({"msg": "hello"})

def test_hitl_api():
    app = FastAPI()
    app.include_router(get_hitl_router(prefix="/hitl", tags=["HumanInTheLoop"]))
    uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    test_hitl_cli()
    test_hitl_api()
