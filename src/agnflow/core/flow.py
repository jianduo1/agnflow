from typing import Any, Dict, Self
import traceback

from agnflow.core.connection import Connection
from agnflow.core.node import Node

log_zh = print
log = lambda *x: ...


class Flow(Connection):
    """工作流容器"""

    def __init__(self, name: str = None):
        super().__init__(name=name)

    def __getitem__(self, node: "Connection | tuple | list | slice") -> Self:
        """重载运算符 []

        功能：
        - 补全内部连接connections
        - 补全外部隐式连接hidden_connections
        - 添加节点到容器conntainer

        连接类型：
        - flow[a] 单节点
        - flow[a >> b] 链路
        - flow[a, b] 多节点
        - flow[a:(b, c):(d, e)] 切片表达式，相当于 a->(b,c)  (b,c)->(d,e)
        - flow[(a, b, c):(a, b, c)] 全连接，相当于 a<->b<->c
        - flow[flow[a, b], flow[c, d]] 嵌套
        """

        def to_conn_list(obj) -> list[Connection]:
            """将输入统一转为节点列表"""
            if isinstance(obj, Connection):
                return [obj]
            if isinstance(obj, (tuple, list)):
                return [*obj]
            return []

        conntainer: list[Connection] = self.conntainer.setdefault(self, [])
        # 1.补全内部连接connections
        # 1.1 处理切片表达式 flow[a:(b,c)]
        if isinstance(node, slice):
            # 支持三段式切片：start:stop:step
            starts: list[Connection] = to_conn_list(node.start)
            stops: list[Connection] = to_conn_list(node.stop)
            steps: list[Connection] = to_conn_list(node.step)
            # 构建工作流内部的显式连接 start->stop, stop->step
            for srcs, tgts in ((starts, stops), (stops, steps)):
                for src in srcs:
                    for tgt in tgts:
                        # 忽略自连接和空节点
                        if src is tgt or src is None or tgt is None:
                            continue
                        # 加入容器
                        if src not in conntainer:
                            conntainer.append(src)
                        if tgt not in conntainer:
                            conntainer.append(tgt)
                        # 建立连接
                        src_map: Dict[str, Connection] = self.connections.setdefault(src, {})
                        src_map[tgt.name] = tgt
        # 1.2 处理连接类型 flow[a>>b>>a]（a-b-a需要去重）
        elif isinstance(node, Connection):
            # 添加到容器，可以用于绘制mermaid流程图，{chain:[a,b]}
            for node in node.chains:
                if node not in conntainer:
                    conntainer.append(node)
        # 1.3 处理连接数组类型 flow[a,b,c]
        elif isinstance(node, (tuple, list)):
            for node in node:
                self.__getitem__(node)

        # 2.统一把所有节点都加到 conntainer[self]
        nodes = to_conn_list(node)  # 你可以写一个辅助函数，递归提取所有节点
        for node in nodes:
            if node not in conntainer:
                conntainer.append(node)

        return self

    def __iadd__(self, node: "Connection | tuple | list") -> Self:
        """动态添加节点，调用__getitem__建立连接，并补全外部连接和hidden_connections"""
        # 1. 补全内部连接connections，和添加当前节点到conntainer
        self.__getitem__(node)
        nodes = node if isinstance(node, (list, tuple)) else [node]
        # 2. 补全外部隐式连接hidden_connections
        # 2.1 获取self与外部的连接
        external_in = []
        external_out = []
        for src, tgt_map in self.connections.items():
            for tgt in tgt_map.values():
                if src is self:
                    external_out.append(tgt)
                if tgt is self:
                    external_in.append(src)
        # 2.2 补全外部隐式连接
        for n in nodes:
            for ext in external_in:
                self.hidden_connections.setdefault(ext, {})[n.name] = n
            for ext in external_out:
                self.hidden_connections.setdefault(n, {})[ext.name] = ext

        return self

    def __isub__(self, node: "Connection | tuple | list") -> Self:
        """动态删除节点，移除conntainer和相关连接，并清理外部连接。节点不在容器内时抛出异常。"""
        conntainer = self.conntainer.setdefault(self, [])
        nodes = node if isinstance(node, (list, tuple)) else [node]
        for n in nodes:
            if n in conntainer:
                # 从conntainer中清理
                conntainer.remove(n)
                # 从connections和hidden_connections中清理
                for conn_map in [self.connections, self.hidden_connections]:
                    # 使用字典副本进行遍历，避免运行时修改错误
                    for src, tgt_map in list(conn_map.items()):
                        # n为src
                        if src is n:
                            conn_map.pop(src)
                            break
                        # n为tgt
                        for tgt_name, tgt in list(tgt_map.items()):
                            if tgt is n:
                                conn_map[src].pop(tgt_name)
                                break
            else:
                raise ValueError(f"节点 {n} 不在容器 {self.name} 中，无法删除")
        return self

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
            log(f"\n🔵 Executing node: {current_node} (Remaining steps: {remaining_steps - step})")
            log_zh(f"\n🔵 执行节点: {current_node} (剩余步数: {remaining_steps - step})")

            # ⭐️ 执行当前节点
            try:
                # 统一使用 execute_workflow 方法执行节点
                result = await current_node.execute_workflow(
                    state, remaining_steps=remaining_steps - step, is_async=is_async
                )

                log(f"🔍 Node {current_node} execution result: {result}")
                log_zh(f"🔍 节点 {current_node} 执行结果: {result}")

            except Exception as e:
                print(f"🚨 节点 {current_node} 执行出错: {e}")
                traceback.print_exc()
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
            log(
                f"🟢 {self.name}{self.conntainer[self]} selects entry node: {start_node} based on entry_action: '{entry_action}'"
            )
            log_zh(
                f"🟢 {self.name}{self.conntainer[self]} 根据 entry_action: '{entry_action}' 选择入口节点: {start_node}"
            )
            return start_node

        # 2. 其次使用 container[self][0]
        if self in self.conntainer and self.conntainer[self]:
            start_node = self.conntainer[self][0]
            log(f"🟢 {self.name}{self.conntainer[self]} selects entry node: {start_node} as the first node")
            log_zh(f"🟢 {self.name}{self.conntainer[self]} 第一个节点作为起始节点: {start_node}")
            return start_node

        # 3. 都没有就返回 None（对应 exit）
        log(f"🔍 No start node found, exiting normally")
        log_zh("🔍 没有找到起始节点，正常退出")
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
                log(f"🔍 Node {current_node} with action '{action}' found the next node: {tgt}")
                log_zh(f"🔍 节点 {current_node} 的 action '{action}' 找到下一个节点: {tgt}")
                return tgt

        # 如果没有找到下一个节点，返回 None（对应 exit）
        log(f"\n🛑 Node {current_node} with action '{action}' did not find the next node, exiting normally")
        log_zh(f"\n🛑 节点 {current_node} 的 action '{action}' 没有找到下一个节点，正常退出")
        return None

    # endregion


if __name__ == "__main__":
    from agnflow.utils.code import get_code_line

    # n1 = Node()
    # n2 = Node()
    # n3 = Node()
    # n4 = Node()
    # f1 = Flow()
    # f2 = Flow()
    # f3 = Flow()
    # # fmt: off
    # f1[n1 >> n2 >> f2[n3]] >> f3[n4];title=get_code_line()[0]
    # # fmt: on
    # print(f1.connections)
    # print(f1.hidden_connections)
    # print(f1.render_mermaid(saved_file="assets/flow_mermaid.png", title=title))

    # === HITL 节点集成示例 ===
    from agnflow.agent.hitl.cli import human_in_the_loop

    def review_node(state):
        result, approved = human_in_the_loop("请人工审核本节点数据", input_data=state)
        if approved:
            return {"review_result": result, "approved": True}
        else:
            return "exit", {"review_result": result, "approved": False}

    # n1 = Node("review", exec=review_node)
    # n2 = Node("next", exec=lambda state: print("流程继续", state))
    # n3 = Node("exit", exec=lambda state: "exit")
    # n1 >> n2
    # flow = Flow(n1, name="hitl_demo")
    # flow.run({"msg": "hello"})


class Supervisor(Flow):
    """监督者智能体（监督者与被监督者互连）"""

    def __getitem__(self, node: list[Node]) -> Self:
        """重载运算符 self[key]，设置子工作流

        Supervisor[n1, n2, n3] 第一个参数为监督者，其余为被监督者
        相当于
        Flow[n1, (n2, n3), n1]
        相当于
        n1 <-> n2
        n1 <-> n3
        """
        # 统一转为 list
        if not isinstance(node, (list, tuple)):
            node = [node]
        conntainer = self.conntainer.setdefault(self, [])
        # 预判加完后的总数
        new_total = len(conntainer) + len([n for n in node if n not in conntainer])
        if new_total < 2:
            raise ValueError("Supervisor只能接受两个以上节点")
        for n in node:
            if n not in conntainer:
                conntainer.append(n)
        supervisor, *supervisees = conntainer
        super().__getitem__(slice(supervisor, supervisees, supervisor))
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
    """蜂群智能体（蜂群节点全互连）"""

    def __getitem__(self, node: "list[Node] | Any") -> Self:
        """重载运算符 self[key]，获取子工作流

        Swarm[n1, n2, n3]
        相当于
        Flow[(n1, n2, n3), (n1, n2, n3)]
        相当于
        n1 <-> n2 <-> n3 <-> n1
        """
        # 统一转为 list
        if not isinstance(node, (list, tuple)):
            node = [node]

        # 预判加完后的总数
        conntainer = self.conntainer.setdefault(self, [])
        new_total = len(conntainer) + len([n for n in node if n not in conntainer])
        if new_total < 2:
            raise ValueError("Swarm只能接受两个以上节点")

        # 把节点添加到容器
        for n in node:
            if n not in conntainer:
                conntainer.append(n)
        
        # 显式连接：节点全互连
        super().__getitem__(slice(conntainer, conntainer))
        
        # 隐式连接
        for i in conntainer:
            for j in conntainer:
                if i is not j:
                    self.build_connections(i, j)
        return self


if __name__ == "__main__":
    from pprint import pprint

    n1 = Node(exec=lambda state: "n2")
    n2 = Node(exec=lambda state: "n3")
    n3 = Node(exec=lambda state: "n4")
    n4 = Node(exec=lambda state: "exit")
    s1 = Swarm()
    s2 = Swarm()
    s3 = Swarm()

    # fmt: off
    # n1>>s1[ n2, n3];title=get_code_line()[0]
    # s1[n1, n2, n3,n4];title=get_code_line()[0]
    # n1 >> s1[n2, n3] >> n4;title=get_code_line()
    # s1[n1, n2] >> s2[n3, n4];title = get_code_line()
    # fmt: on

    # 绘制流程图
    # print(s1.render_dot(saved_file="assets/swarm_dot.png"))
    # for i in s1.render_mermaid(saved_file="assets/swarm_mermaid.png", title=title)[1:]:
    #     print(i)
    # pprint(s1.hidden_connections, indent=2, width=30)
    # s1 += n4
    # # s1[n4]
    # for i in s1.render_mermaid(saved_file="assets/swarm_mermaid_2.png", title=title)[1:]:
    #     print(i)
    # pprint(s1.hidden_connections, indent=2, width=30)
    # s1 -= n2
    # # s1[~n2]
    # for i in s1.render_mermaid(saved_file="assets/swarm_mermaid_3.png", title=title)[1:]:
    #     print(i)
    # pprint(s1.hidden_connections, indent=2, width=30)

    # 连接关系
    # pprint(s1.conntainer, indent=2, width=30)
    # pprint(s1.hidden_connections, indent=2, width=30)
    # pprint(s1.connections, indent=2, width=30)

    # 执行流程
    # s1.run({}, max_steps=10, entry_action="n2")


class ParallelFlow(Flow):
    """并行节点"""

    def __getitem__(self, nodes: list[Node]):
        """重载运算符 self[key]，获取子节点"""
        container = self.conntainer.setdefault(self, [])
        container.extend(nodes)
        return self

    async def execute_workflow(
        self, state: dict, remaining_steps: int = 10, entry_action: str = None, is_async: bool = False
    ) -> Any:
        """并行节点执行工作流"""
        container = self.conntainer.get(self, [])
        await asyncio.gather(
            *[node.execute_workflow(state, remaining_steps, entry_action, is_async) for node in container]
        )


if __name__ == "__main__":
    from agnflow.core.flow import Flow
    import asyncio

    async def sleep_and_print(self, state):
        ns = {"n1": 3, "n2": 2, "n3": 1}
        n = ns[self.name]
        await asyncio.sleep(n)
        print(f" {self.name}: sleep: {n}s state:{state}")

    n1 = Node(aexec=sleep_and_print)
    n2 = Node(aexec=sleep_and_print)
    n3 = Node(aexec=sleep_and_print)
    pf = ParallelFlow()
    pf[n1, n2, n3]

    asyncio.run(pf.arun({"a": 1}))
    # print(pn.connections)
    print(pf.render_mermaid(saved_file="assets/parallel_flow.png", title="并行运行工作流示例"))
