from typing import Callable
import asyncio, warnings, copy, time, tempfile, subprocess


class Conn:
    """节点连接"""

    counter = 1

    def __init__(self):
        self.next_ndoes = {}
        self._action = None
        self.name = f"{self.__class__.__name__}_{Conn.counter}"
        Conn.counter += 1

    # region 节点连接
    def __rshift__(self, target: "Conn | str | dict[str, Conn]"):
        """重载运算符 >>
        - source >> target (action默认为"default")
        - source >> "action" >> target
        - source >> {"action1": target, "action2": target2}
        """
        if isinstance(target, Conn):
            self.next_ndoes[self._action or "default"] = target
            return target
        elif isinstance(target, str):
            self._action = target
            return self
        elif isinstance(target, (list, tuple)) and (target := next(target, None)):
            self.next_ndoes[self._action or "default"] = target
            return self
        elif isinstance(target, dict):
            for a, t in target.items():
                self.next_ndoes[a] = t
            return self
        return self

    def __lshift__(self, source: "Conn | str | dict[str, Conn]"):
        """重载运算符 <<
        - target << source
        - target << "action" << source
        - target << {"action1": source, "action2": source2}
        """
        if isinstance(source, Conn):
            source.next_ndoes[self._action or "default"] = self
            return source
        elif isinstance(source, str):
            self._action = source
            return self
        elif isinstance(source, dict):
            for a, s in source.items():
                s.next_ndoes[a] = self
            return source
        return self

    # endregion


class Node(Conn):
    """节点"""

    def __init__(self, name: str = None, exec: Callable = None, aexec: Callable = None, max_retries=1, wait=0):
        super().__init__()
        if exec:
            self.exec = exec
        if aexec:
            self.aexec = aexec
        if name:
            self.name = name
        self.max_retries, self.wait = max_retries, wait

    # region 流程控制 _run -> _exec -> exec
    def _run(self, state):
        return self._exec(state)

    async def _arun(self, state):
        return await self._aexec(state)

    def _exec(self, state):
        for self.cur_retry in range(self.max_retries):  # 重试机制
            try:
                # 如果exec函数有state参数，则直接调用exec(state=state)
                if "state" in self.exec.__code__.co_varnames:
                    return self.exec(state=state)
                # 否则，根据exec函数的指定参数名，从state中获取参数
                else:
                    return self.exec(**{k: state[k] for k in self.exec.__code__.co_varnames if k != "self" and k in state})

            except Exception as e:
                if self.cur_retry == self.max_retries - 1:
                    return self.exec_fallback(state, e)
                if self.wait > 0:
                    time.sleep(self.wait)

    async def _aexec(self, state):
        for self.cur_retry in range(self.max_retries):  # 重试机制
            try:
                # 如果exec函数有state参数，则直接调用exec(state=state)
                if "state" in self.aexec.__code__.co_varnames:
                    return await self.aexec(state=state)
                # 否则，根据exec函数的指定参数名，从state中获取参数
                else:
                    return await self.aexec(**{k: state[k] for k in self.aexec.__code__.co_varnames if k != "self" and k in state})

            except Exception as e:
                if self.cur_retry == self.max_retries - 1:
                    return await self.aexec_fallback(state, e)
                if self.wait > 0:
                    await asyncio.sleep(self.wait)

    def exec_fallback(self, state, exc):
        raise exc

    async def aexec_fallback(self, state, exc):
        raise exc

    def exec(self, state):
        pass

    async def aexec(self, state):
        pass

    # endregion

    # region 绘制流程图
    def to_dot(self, depth=0, visited=None):
        """将节点渲染为dot格式"""
        if visited is None:
            visited = set()

        if id(self) in visited:
            return [], set()

        visited.add(id(self))
        lines = []
        used_nodes = {self.name}

        # 渲染当前节点
        lines.append(f'    {self.name};')

        # 渲染边
        for act, nxt in self.next_ndoes.items():
            if nxt is not None:
                # 如果后继节点是Flow，连接到其起始节点
                if isinstance(nxt, Flow) and nxt.start_node:
                    target_node = nxt.start_node.name
                else:
                    target_node = nxt.name

                label = f' [label="{act}"]' if act and act != "default" else ""
                lines.append(f'    {self.name} -> {target_node}{label};')

                # 递归渲染后继节点
                if isinstance(nxt, Flow):
                    nested_lines, nested_nodes = nxt.to_dot(depth + 1, visited)
                    lines.extend(nested_lines)
                    used_nodes.update(nested_nodes)
                else:
                    nested_lines, nested_nodes = nxt.to_dot(depth, visited)
                    lines.extend(nested_lines)
                    used_nodes.update(nested_nodes)

        return lines, used_nodes

    def to_mermaid(self, depth=0, visited=None):
        """将节点渲染为mermaid格式"""
        if visited is None:
            visited = set()

        if id(self) in visited:
            return [], set()

        visited.add(id(self))
        lines = []
        used_nodes = {self.name}

        # 渲染边
        for act, nxt in self.next_ndoes.items():
            if nxt is not None:
                # 如果后继节点是Flow，连接到其起始节点
                if isinstance(nxt, Flow) and nxt.start_node:
                    target_node = nxt.start_node.name
                else:
                    target_node = nxt.name

                lines.append(f'    {self.name} --{act}--> {target_node}')

                # 递归渲染后继节点
                if isinstance(nxt, Flow):
                    nested_lines, nested_nodes = nxt.to_mermaid(depth + 1, visited)
                    lines.extend(nested_lines)
                    used_nodes.update(nested_nodes)
                else:
                    nested_lines, nested_nodes = nxt.to_mermaid(depth, visited)
                    lines.extend(nested_lines)
                    used_nodes.update(nested_nodes)

        return lines, used_nodes

    # endregion


class Flow(Conn):
    """工作流"""

    def __init__(self, start: Conn | None = None, name: str = None):
        super().__init__()
        self.start_node = start
        if name:
            self.name = name

    # region 流程控制 flow.run -> flow._run -> node._run -> node._exec -> node.exec
    def run(self, state: dict):
        if self.next_ndoes:
            warnings.warn("节点不会运行后继节点。使用Flow。")
        return self._run(state)

    async def arun(self, state: dict):
        if self.next_ndoes:
            warnings.warn("节点不会运行后继节点。使用Flow。")
        return await self._arun(state)

    def _run(self, state: dict):
        curr: Conn = copy.copy(self.start_node)
        while curr:
            res = curr._run(state)
            # 返回值为字典，则更新state
            if isinstance(res, dict):
                action = "default"
                state.update(res)
            # 返回值为字符串，则设置action
            elif isinstance(res, str):
                action = res
            # 返回值为列表或元组，第一个字符串类型设置为action，第一个字典类型则更新state
            elif isinstance(res, (list, tuple)):
                action = next((item for item in res if isinstance(item, str)), None)
                state.update(next((item for item in res if isinstance(item, dict)), {}))
            # 返回值为其他类型，则设置action
            else:
                action = "default"
            # 根据action，获取下一个节点
            curr = copy.copy(curr.next_ndoes.get(action))
        return action

    async def _arun(self, state: dict):
        curr: Conn = copy.copy(self.start_node)
        action = None
        while curr:
            res = await curr._arun(state)
            if isinstance(res, dict):
                state.update(res)
            elif isinstance(res, str):
                action = res
            elif isinstance(res, (list, tuple)):
                action = next((item for item in res if isinstance(item, str)), None)
                state.update(next((item for item in res if isinstance(item, dict)), {}))
            else:
                action = res
            curr = copy.copy(curr.next_ndoes.get(action or "default"))
        return action

    # endregion

    # region 辅助方法
    def _find_exit_nodes(self, flow):
        """找到Flow的出口节点（没有后继节点的节点）"""
        exit_nodes = []
        visited = set()
        
        def traverse(node):
            if id(node) in visited:
                return
            visited.add(id(node))
            
            if isinstance(node, Flow):
                # 如果是嵌套Flow，遍历其起始节点
                if node.start_node:
                    traverse(node.start_node)
            else:
                # 检查当前节点是否有后继节点
                has_next = False
                for next_node in node.next_ndoes.values():
                    if next_node is not None:
                        has_next = True
                        traverse(next_node)
                
                # 如果没有后继节点，则为出口节点
                if not has_next:
                    exit_nodes.append(node)
        
        # 从Flow的起始节点开始遍历
        if flow.start_node:
            traverse(flow.start_node)
        
        return exit_nodes

    # endregion

    # region 自渲染方法
    def to_dot(self, depth=0, visited=None):
        """将Flow渲染为dot格式，包含子图"""
        if visited is None:
            visited = set()

        if id(self) in visited:
            return [], set()

        visited.add(id(self))
        lines = []
        used_nodes = set()

        # 根据深度选择颜色
        colors = ["lightgrey", "lightblue", "lightgreen", "red", "lightyellow", "lightpink"]
        color = colors[depth % len(colors)]

        # 开始子图
        subgraph_id = f"cluster_{id(self)}"
        lines.append(f'  subgraph {subgraph_id} {{')
        lines.append(f"    rankdir=TB;")
        lines.append(f'    label = "{self.name}";')
        lines.append(f'    style=filled;')
        lines.append(f'    color={color};')

        # 渲染起始节点及其后继
        if self.start_node:
            start_lines, start_nodes = self.start_node.to_dot(depth + 1, visited)
            lines.extend(start_lines)
            used_nodes.update(start_nodes)

        # 结束子图
        lines.append('  }')

        # 渲染Flow自身的边（连接到外部节点）
        for act, nxt in self.next_ndoes.items():
            if nxt is not None:
                # 找到出口节点
                exit_nodes = self._find_exit_nodes(self)
                for exit_node in exit_nodes:
                    # 如果外部节点是Flow，连接到其起始节点
                    if isinstance(nxt, Flow) and nxt.start_node:
                        target_node = nxt.start_node.name
                    else:
                        target_node = nxt.name

                    label = f' [label="{act}"]' if act and act != "default" else ""
                    lines.append(f'    {exit_node.name} -> {target_node}{label};')

                # 递归渲染外部节点
                if isinstance(nxt, Flow):
                    nested_lines, nested_nodes = nxt.to_dot(depth, visited)
                    lines.extend(nested_lines)
                    used_nodes.update(nested_nodes)
                else:
                    nested_lines, nested_nodes = nxt.to_dot(depth, visited)
                    lines.extend(nested_lines)
                    used_nodes.update(nested_nodes)

        return lines, used_nodes

    def to_mermaid(self, depth=0, visited=None):
        """将Flow渲染为mermaid格式，包含子图"""
        if visited is None:
            visited = set()

        if id(self) in visited:
            return [], set()

        visited.add(id(self))
        lines = []
        used_nodes = set()

        # 开始子图
        lines.append(f'    subgraph {self.name}')

        # 收集属于当前Flow的节点（不包括嵌套Flow的节点）
        current_flow_nodes = set()
        if self.start_node:
            # 遍历当前Flow的所有节点
            queue = [self.start_node]
            visited_nodes = set()

            while queue:
                node = queue.pop(0)
                if id(node) in visited_nodes:
                    continue
                visited_nodes.add(id(node))

                if isinstance(node, Flow):
                    # 如果是嵌套Flow，不收集其节点，但继续遍历其起始节点
                    if node.start_node:
                        queue.append(node.start_node)
                else:
                    # 普通节点属于当前Flow
                    current_flow_nodes.add(node.name)

                # 继续遍历后继节点
                for succ in node.next_ndoes.values():
                    if succ is not None:
                        queue.append(succ)

        # 渲染当前Flow的节点
        for node_name in current_flow_nodes:
            lines.append(f'        {node_name}')

        # 渲染起始节点及其后继（递归渲染嵌套Flow和边）
        if self.start_node:
            start_lines, start_nodes = self.start_node.to_mermaid(depth + 1, visited)
            lines.extend(start_lines)
            used_nodes.update(start_nodes)

        # 结束子图
        lines.append('    end')

        # 渲染Flow自身的边（连接到外部节点）
        for act, nxt in self.next_ndoes.items():
            if nxt is not None:
                # 找到出口节点
                exit_nodes = self._find_exit_nodes(self)
                for exit_node in exit_nodes:
                    # 如果外部节点是Flow，连接到其起始节点
                    if isinstance(nxt, Flow) and nxt.start_node:
                        target_node = nxt.start_node.name
                    else:
                        target_node = nxt.name

                    lines.append(f'    {exit_node.name} --{act}--> {target_node}')

                # 递归渲染外部节点
                if isinstance(nxt, Flow):
                    nested_lines, nested_nodes = nxt.to_mermaid(depth, visited)
                    lines.extend(nested_lines)
                    used_nodes.update(nested_nodes)
                else:
                    nested_lines, nested_nodes = nxt.to_mermaid(depth, visited)
                    lines.extend(nested_lines)
                    used_nodes.update(nested_nodes)

        return lines, used_nodes

    # endregion

    # region 绘制流程图
    def render_dot(self, saved_file: str = None):
        """使用新的自渲染方法生成dot格式"""
        lines = ["digraph G {"]
        lines.append("    rankdir=TB;")

        # 使用自渲染方法
        content_lines, used_nodes = self.to_dot(0, set())
        lines.extend(content_lines)

        # 标记起始节点
        start_name = self.start_node.name if self.start_node else "unknown"
        lines.append(f'    {start_name} [style=filled, fillcolor="#f9f"];')
        lines.append("}")

        viz_str = "\n".join(lines)

        if saved_file:
            saved_file = saved_file if saved_file.endswith('.png') else saved_file + '.png'
            with tempfile.NamedTemporaryFile('w+', suffix='.dot') as tmp_dot:
                tmp_dot.write(viz_str)
                tmp_dot.flush()
                s, o = subprocess.getstatusoutput(f'dot -Tpng {tmp_dot.name} -o {saved_file}')
                if s != 0:
                    warnings.warn(f"dot 生成图片失败，检查 dot 是否安装（brew install graphviz）: {o}")
                else:
                    print(f"图片已保存为: {saved_file}")

        return viz_str

    def render_mermaid(self, saved_file: str = None):
        """使用新的自渲染方法生成mermaid格式"""
        lines = ["flowchart TD"]

        # 使用自渲染方法
        content_lines, used_nodes = self.to_mermaid(0, set())
        lines.extend(content_lines)

        # 标记起始节点
        start_name = self.start_node.name if self.start_node else "unknown"
        lines.append('    classDef startNode fill:#f9f,stroke:#333,stroke-width:2px;')
        lines.append(f'    {start_name}:::startNode')

        viz_str = "\n".join(lines)

        if saved_file:
            saved_file = saved_file if saved_file.endswith('.png') else saved_file + '.png'
            with tempfile.NamedTemporaryFile('w+', suffix='.mmd', delete=True) as tmp_mmd:
                tmp_mmd.write(viz_str)
                tmp_mmd.flush()
                s, o = subprocess.getstatusoutput(f'mmdc -i {tmp_mmd.name} -o {saved_file}')
                if s != 0:
                    warnings.warn(
                        f"mmdc 生成图片失败: {o}\n"
                        "检查 mmdc 是否安装:\n"
                        "- npm install -g @mermaid-js/mermaid-cli\n"
                        "- npx puppeteer browsers install chrome-headless-shell"
                    )
                else:
                    print(f"图片已保存为: {saved_file}")

        return viz_str

    # endregion

