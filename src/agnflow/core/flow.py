from typing import Any

from agnflow.core.connection import Connection
from agnflow.core.node import Node

class Flow(Connection):
    """工作流容器 - 管理多个节点的执行流程"""

    def __init__(self, name: str = None):
        super().__init__(name=name)

    # region 执行流程

    async def execute_workflow(
        self, state: dict, remaining_steps: int = 10, entry_action: str = None, is_async: bool = False
    ) -> Any:
        """统一的工作流执行逻辑，支持同步/异步、最大步数限制和 action 入口

        步骤：
        1. 获取起始节点 `_get_start_node`
        2. 执行当前节点 `_execute_node_sync/async`
        3. 处理执行结果 `_process_execution_result`
        4. 获取下一个要执行的节点 `_get_next_node`
        5. 重复执行，直到达到最大步数或没有下一个节点
        """
        if remaining_steps <= 0:
            print(f"达到最大执行步数，流程正常终止")
            return "max_steps_exceeded"

        # ⭐️ 获取起始节点
        start_node = self._get_start_node(entry_action)
        if not start_node:
            print(f"没有找到起始节点，工作流结束")
            return "exit"

        # ⭐️ 当前执行节点（每次只执行一个节点）
        current_node = start_node
        step = 0

        while current_node and step < remaining_steps:
            print(f"\n🔵 执行节点: {current_node} (剩余步数: {remaining_steps - step})")

            # ⭐️ 执行当前节点
            try:
                # 统一使用 execute_workflow 方法执行节点
                result = await current_node.execute_workflow(
                    state, remaining_steps=remaining_steps - step, is_async=is_async
                )
                print(f"🔍 节点 {current_node} 执行结果: {result}")

            except Exception as e:
                print(f"🚨 节点 {current_node} 执行出错: {e}")
                result = "error"

            # ⭐️ 处理执行结果
            action, state_updates = self._process_execution_result(result)
            if state_updates:
                state.update(state_updates)

            # ⭐️ 获取下一个要执行的节点
            next_node = self._get_next_node(current_node, action)
            if next_node:
                current_node = next_node
            else:
                current_node = None  # 没有下一个节点，结束执行

            step += 1

        if step >= remaining_steps:
            print(f"达到最大执行步数 {remaining_steps}，流程正常终止")
            return "max_steps_exceeded"

        return "exit"

    def _process_execution_result(self, result: Any) -> tuple[str, dict]:
        """处理执行结果，返回 (action, state_updates)"""
        if isinstance(result, dict):
            return "exit", result
        elif isinstance(result, str):
            return result, {}
        elif isinstance(result, (list, tuple)):
            # 从结果中提取 action 和 state 更新
            action = next((item for item in result if isinstance(item, str)), "exit")
            state_updates = next((item for item in result if isinstance(item, dict)), {})
            return action, state_updates
        else:
            return "exit", {}

    def _get_start_node(self, entry_action: str = None) -> Connection | None:
        """
        获取起始节点，支持 action 入口选择

        1. 优先使用 connections[self][entry_action]
        2. 其次使用 container[self][0] 第一个节点
        3. 都没有就返回 None（对应 exit）
        """
        # 1. 优先使用 self.connections[self][entry_action]
        if entry_action and self in self.conntainer and entry_action in [i.name for i in self.conntainer[self]]:
            start_node = next(i for i in self.conntainer[self] if i.name == entry_action)
            print(
                f"🟢 {self.name}{self.conntainer[self]} 根据 entry_action: '{entry_action}' 选择入口节点: {start_node}"
            )
            return start_node

        # 2. 其次使用 container[self][0]
        if self in self.conntainer and self.conntainer[self]:
            start_node = self.conntainer[self][0]
            print(f"🟢 {self.name}{self.conntainer[self]} 第一个节点作为起始节点: {start_node}")
            return start_node

        # 3. 都没有就返回 None（对应 exit）
        print("🔍 没有找到起始节点，正常退出")
        return None

    def _get_next_node(self, current_node: Connection, action: str = None) -> Connection | None:
        """
        获取当前节点的下一个节点。

        使用 self.all_connections[current_node][action] 查找下一个节点，
        如果没有找到就返回 None（对应 exit）
        """
        # 使用 all_connections 查找下一个节点
        if current_node in self.all_connections:
            targets = self.all_connections[current_node]
            if action in targets:
                tgt = targets[action]
                print(f"🔍 节点 {current_node} 的 action '{action}' 找到下一个节点: {tgt}")
                return tgt

        # 如果没有找到下一个节点，返回 None（对应 exit）
        print(f"\n🛑 节点 {current_node} 的 action '{action}' 没有找到下一个节点，正常退出")
        return None

    # endregion


if __name__ == "__main__":
    from agnflow.core.node import Node
    from agnflow.core.utils import get_code_line

    n1 = Node()
    n2 = Node()
    n3 = Node()
    n4 = Node()
    f1 = Flow()
    f2 = Flow()
    f3 = Flow()
    # fmt: off
    f1[n1 >> n2 >> f2[n3]] >> f3[n4];title=get_code_line()[0]
    # fmt: on
    print(f1.connections)
    print(f1.hidden_connections)
    print(f1.render_mermaid(saved_file="assets/flow_mermaid.png", title=title))


class Supervisor(Flow):
    """监督者智能体"""

    def __getitem__(self, key: tuple[Node]):
        """重载运算符 self[key]，设置子工作流

        Supervisor[n1, n2, n3] 第一个参数为监督者，其余为被监督者
        相当于
        Flow[n1, (n2, n3), n1]
        相当于
        n1 <-> n2
        n1 <-> n3
        """
        if len(key) == 1:
            raise ValueError("Supervisor只能接受两个以上参数")
        supervisor, *supervisees = key

        # 先用 slice 方式建立连接关系
        super().__getitem__(slice(supervisor, supervisees, supervisor))

        # 把所有节点都添加到 conntainer[self]
        conntainer = self.conntainer.setdefault(self, [])
        for node in key:
            if node not in conntainer:
                conntainer.append(node)

        return self


if __name__ == "__main__":
    n1 = Node(exec=lambda state: "n2")
    n2 = Node(exec=lambda state: "n3")
    n3 = Node(exec=lambda state: "n4")
    n4 = Node(exec=lambda state: "exit")
    s1 = Supervisor()
    # fmt: off
    # s1[n1, n2, n3] >> n4; title=get_code_line()[0]
    # fmt: on
    # # print(s1.render_mermaid())
    # print(s1.render_mermaid(saved_file="assets/supervisor_mermaid.png", title=title))


class Swarm(Flow):
    """蜂群智能体"""

    def __getitem__(self, key: tuple[Node]):
        """重载运算符 self[key]，获取子工作流

        Swarm[n1, n2, n3]
        相当于
        Flow[(n1, n2, n3), (n1, n2, n3)]
        相当于
        n1 <-> n2 <-> n3 <-> n1
        """
        if len(key) == 1:
            raise ValueError("Swarm只能接受两个以上参数")

        # 先用 slice 方式建立连接关系
        super().__getitem__(slice(key, key))

        # 把所有节点都添加到 conntainer[self]
        conntainer = self.conntainer.setdefault(self, [])
        for node in key:
            if node not in conntainer:
                conntainer.append(node)

        return self


if __name__ == "__main__":
    from .node import Node
    from pprint import pprint

    n1 = Node(exec=lambda state: "n2")
    n2 = Node(exec=lambda state: "n3")
    n3 = Node(exec=lambda state: "n4")
    n4 = Node(exec=lambda state: "exit")
    s1 = Swarm()
    s2 = Swarm()
    s3 = Swarm()

    # fmt: off
    s1[n1, n2, n3,n4];title=get_code_line()[0]
    # s1[n1, n2, n3,n4];title=get_code_line()[0]
    # n1 >> s1[n2, n3] >> n4;title=get_code_line()
    # s1[n1, n2] >> s2[n3, n4];title = get_code_line()
    # fmt: on

    # 绘制流程图
    # print(s1.render_dot(saved_file="assets/swarm_dot.png"))
    # print(s1.render_mermaid(saved_file="assets/swarm_mermaid.png", title=title))

    # 连接关系
    # # 蜂群容器
    # pprint(s1.conntainer, indent=2, width=30)
    # # 蜂群隐式连接
    # pprint(s1.hidden_connections, indent=2, width=30)
    # # 蜂群显式连接
    # pprint(s1.connections, indent=2, width=30)
    # # 蜂群所有连接
    # pprint(s1.all_connections, indent=2, width=30)

    # 执行流程
    # s1.run({}, max_steps=10, entry_action="n2")
