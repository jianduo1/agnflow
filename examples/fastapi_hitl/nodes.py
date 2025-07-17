"""FastAPI HITL节点实现。

本模块提供了基于FastAPI的人机协作节点，包括任务处理、异步审查和结果输出功能。
支持SSE（Server-Sent Events）实时状态更新和异步事件等待。
"""

from agnflow.core import Flow
from agnflow.core import Node, Node


class ProcessNode(Node):
    """任务处理节点 - 处理用户输入的任务"""

    def exec(self, state):
        task_input = state.get("task_input", "No input")

        import time
        processed_output = time.sleep(2)

        state["processed_output"] = processed_output
        return "review_node" 


class ReviewNode(Node):
    """异步审查节点 - 等待用户审查和反馈"""

    async def aexec(self, state):
        """准备阶段：设置SSE状态更新并准备审查事件"""
        review_event = state.get("review_event")
        queue = state.get("sse_queue")  # 期望队列在共享存储中
        processed_output = state.get("processed_output", "N/A")

        if not review_event or not queue:
            return None  # 信号失败

        # 将状态更新推送到SSE队列
        status_update = {"status": "waiting_for_review", "output_to_review": processed_output}
        await queue.put(status_update)

        review_event = review_event
        if not review_event:
            return
        await review_event.wait()

        feedback = state.get("feedback")

        # 清除事件以支持潜在循环
        review_event = state.get("review_event")
        if review_event:
            review_event.clear()
        state["feedback"] = None  # 重置反馈

        if feedback == "approved":
            state["final_result"] = state.get("processed_output")
            return "result_node"
        else:
            print("ReviewNode Post: Action=rejected")
            return "process_node"


class ResultNode(Node):
    """结果输出节点 - 显示最终结果"""

    def exec(self, state):

        print(f"--- FINAL RESULT ---")
        print(state.get("final_result", "No final result."))
        print(f"--------------------")


# Example main function
# Please replace this with your own main function
def main():
    state = {"question": "In one sentence, what's the end of universe?", "answer": None}

    process_node = ProcessNode()
    review_node = ReviewNode()
    result_node = ResultNode()
    flow = Flow()

    flow[process_node >> review_node >> [result_node, process_node]]
    flow.run(state)
    print("Question:", state["question"])
    print("Answer:", state["answer"])


if __name__ == "__main__":
    main()
