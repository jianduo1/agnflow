from typing import Any, Callable
import asyncio, time, inspect
from agnflow.core.connection import Connection


class Node(Connection):
    """节点 - 工作流的基本执行单元"""

    def __init__(self, name: str = None, exec: Callable = None, aexec: Callable = None, max_retries=1, wait=0):
        super().__init__(name=name)
        self.exec = exec or self.exec
        self.aexec = aexec or self.aexec
        self.max_retries = max_retries
        self.wait = wait
        self.cur_retry = 0

    def __getitem__(self, key):
        raise NotImplementedError("Node 类不支持 __getitem__ 方法")

    # region 执行流程

    async def execute_workflow(
        self, state: dict, remaining_steps: int = 10, entry_action: str = None, is_async: bool = False
    ) -> Any:
        """Node 作为单节点工作流，调用自定义或者默认执行器（exec/aexec）

        支持同步/异步执行，重试机制，错误处理
        """
        if remaining_steps <= 0:
            return "max_steps_exceeded"

        # ⭐️ 执行重试机制
        for self.cur_retry in range(self.max_retries):
            try:
                # ⭐️ 调用自定义或者默认执行器（exec/aexec），根据 is_async 选择同步/异步
                if is_async:
                    return await self._call_with_params(self.aexec, state)
                else:
                    return self._call_with_params(self.exec, state)
            except Exception as exc:
                # ⭐️ 执行错误处理
                if self.cur_retry == self.max_retries - 1:
                    if is_async:
                        return await self.aexec_fallback(state, exc)
                    else:
                        return self.exec_fallback(state, exc)
                if self.wait > 0:
                    if is_async:
                        await asyncio.sleep(self.wait)
                    else:
                        time.sleep(self.wait)

    def _call_with_params(self, executor: Callable, state: dict) -> Any:
        """根据函数签名智能调用执行器

        步骤：
        - 提取 executor 的参数名和默认值
        - 如果 state 中有对应值，覆盖默认值
        - 如果参数名为 state 且 state 是 dict，传递整个 state

        示例：
        - executor：def exec(state, a, b=1): pass
        - state：{"a": 1}
        - 返回：exec(**{"state": state, "a": state["a"], "b": 1}) 也就是 exec(state, a=1, b=1)
        """
        if not callable(executor):
            return None

        # 获取函数参数信息
        sig = inspect.signature(executor)
        params = sig.parameters

        # 构建调用参数
        call_kwargs = {}

        for param_name, param in params.items():
            if param_name == "self":
                continue

            # 如果参数有默认值，使用默认值
            if param.default != inspect.Parameter.empty:
                call_kwargs[param_name] = param.default

            # 如果 state 中有对应值，覆盖默认值
            if param_name in state:
                call_kwargs[param_name] = state[param_name]
            # 特殊处理：如果参数名为 state 且 state 是 dict，传递整个 state
            elif param_name == "state" and isinstance(state, dict):
                call_kwargs[param_name] = state

        return executor(**call_kwargs)

    # endregion

    # region 默认执行器和错误处理
    def exec(self, state: dict) -> Any:
        """默认同步执行器"""
        print(f"默认同步执行器: {self}, 当前 state: {state}, 返回 exit")
        return "exit"

    async def aexec(self, state: dict) -> Any:
        """默认异步执行器"""
        print(f"默认异步执行器: {self}, 当前 state: {state}, 返回 exit")
        return "exit"

    def exec_fallback(self, state: dict, exc: Exception) -> Any:
        """同步执行失败的回调"""
        raise exc

    async def aexec_fallback(self, state: dict, exc: Exception) -> Any:
        """异步执行失败的回调"""
        raise exc

    # endregion


if __name__ == "__main__":
    from agnflow.core.utils import get_code_line

    n1 = Node()
    n2 = Node()
    n3 = Node()
    n4 = Node()
    n5 = Node()
    # fmt: off
    n1 >> [n2 >> n3, n3 >>n4] >> n5; title=get_code_line()[0]
    # fmt: on
    print(n1.connections)
    # print(n1.render_mermaid(saved_file="assets/node_mermaid.png", title=title))
