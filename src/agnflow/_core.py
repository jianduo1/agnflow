"""
TODO: 智能体类型
- [x] 节点类型
- [x] 条件工作流类型
- [x] 监督者类型
- [x] 蜂群类型

TODO: 多智能体开发框架
- [x] 工作流编排
- [x] 工作流执行
- [ ] 工作流监控
- [x] 工作流可视化

"""

from typing import Any, Callable, Self, Dict
import asyncio, time, tempfile, subprocess, warnings
from pathlib import Path
import inspect
import re


def get_code_line() -> list[str]:
    """基于调用栈获取代码行

    ```python
    1 + 1; l = get_code_line()
    print(l)
    out:
    ['1 + 1']
    ```
    """
    stack = inspect.stack()[1:]
    try:

        def handle(line):
            if ";" in line and "get_code_line" in line:
                line = ";".join([i for i in line.split(";") if "get_code_line" not in i])
            return line

        return [handle(frame.code_context[0].strip()) for frame in stack if frame.code_context]
    finally:
        del stack


class Connection:
    """连接关系（节点与容器）

    数据：
    - name 通过查询调用堆栈的技术，动态获取当前实例的变量名，作为name属性
    - chains 链式调用数组 c1 >> c2 >> c3 ==> [c1, c2, c3]
    - conntainer 工作流容器，支持容器嵌套容器，如 flow[a,b] 相当于 {flow:[a,b]}
    - connections 显式连接，如
        a >> flow[x,y] >> b 相当于 a-flow-b 相当于 {a:{"flow":flow}, flow:{"b":b}}
    - hidden_connections 隐式连接，绘制mermaid流程图时会隐式，如
        a >> flow[x,y] >> b 相当于 a-x a-y x-b y-b 相当于 {a:{"x":x,"y":y}, x:{"b}:b, y:{"b}:b}

    容器：
    - 包含多个节点，
    - 节点与容器进行连接，意味着节点与容器内所有节点会进行连接，如
        - x >> flow[a,b,c] 表示 x 同时与 a,b,c 进行连接
    - 支持基于切片的复杂连接方式，如
        - flow[(a):(b,c):(d,e)] 表示
        - a 与 b,c 进行连接，`a->b a->c`
        - b,c 与 d,e 组成四对连接，`b->d b->e c->d c->e`
        - flow[(a,b,c):(a,b,c)] 实现了 a,b,c 的全连接，也就是 `a<->b c<->c c<->a`
    - TODO: 支持容器嵌套容器的形式

    连接类型：
    - 节点 >> 节点
    - 节点 >> 容器（源节点，会与容器中所有节点进行连接）
    - 容器 >> 容器（源容器所有节点，会与目标容器所有节点进行连接）
    - 容器 >> 节点（容器中所有节点，都会连接到目标节点）

    图例：
    ```
              +--flow1-+    +--flow2-+
    x -> y -> | a -> b | -> | c -> d | -> z
              +--------+    +--------+
    ```
    """

    connections: "dict[Connection,dict[str,Connection]]" = {}  # {source: {action: target}}
    conntainer: "dict[Connection,list[Connection]]" = {}  # 区分内连接和外连接的容器
    hidden_connections: "dict[Connection,dict[str,Connection]]" = {}  # {source: {action: target}}

    def __init__(self, name: str = None, chains: "list[Connection]" = None):
        self.chains: list[Connection] = chains or [self]  # [source , ... , target]
        self.name = name or self._get_instance_name()

    def _get_instance_name(self) -> str:
        """设置实例名称"""
        # stack = inspect.stack()
        try:
            # stack[0]: _collect_names
            # stack[1]: Connections.__init__
            # stack[2]: Node.__init__ or Flow.__init__
            # stack[3]: 用户代码中调用构造函数的帧。
            for line in get_code_line():
                match = re.match(r"^\s*(\w+)\s*=\s*" + self.__class__.__name__ + r"\(", line)
                if match:
                    return str(match.group(1))
            # if len(stack) > 1:
            #     for frame in stack:
            #         if frame.code_context:
            #             line = frame.code_context[0].strip()
            #             match = re.match(r"^\s*(\w+)\s*=\s*" + self.__class__.__name__ + r"\(", line)
            #             if match:
            #                 return str(match.group(1))
            return self.__class__.__name__
        except Exception:
            return self.__class__.__name__
        # finally:
        #     del stack

    def __repr__(self) -> str:
        return f"{self.name}"
        # return f"{self.__class__.__name__}@{self.name}"

    @property
    def all_connections(self):
        """合并所有连接"""
        return {
            key: {**self.hidden_connections.get(key, {}), **self.connections.get(key, {})}
            for key in self.hidden_connections | self.connections
        }

    # region 构建节点与容器关联
    def build_connections(
        self,
        source: "Connection | list | tuple",
        target: "Connection | list | tuple",
    ):
        """构建节点连接，记录容器的节点数据"""

        def convert_to_conn_list(objs) -> "list[Connection]":
            if isinstance(objs, Connection):
                # 如果是 Connection 子类（如 Node、Flow...），直接返回
                if objs.__class__ != Connection:
                    return [objs]
                # 如果是 Connection 本身，返回其 chains 中的第一个节点
                return [objs.chains[0]]
            elif isinstance(objs, (list, tuple)):
                # 如果是列表，递归处理每个元素
                result = []
                for obj in objs:
                    result.extend(convert_to_conn_list(obj))
                return result
            return []

        # 获取当前链路的最后一个节点作为目标
        sources: list[Connection] = convert_to_conn_list(source)
        targets: list[Connection] = convert_to_conn_list(target)

        # 建立连接关系，如 a -> b -> flow1[x,y] -> flow2[z,w] -> c
        # 先构建显式连接 如 a-b-flow1-flow2-c
        for outer_src in sources:
            outer_src_map: Dict[str, Connection] = self.connections.setdefault(outer_src, {})
            for outer_tgt in targets:
                outer_src_map[outer_tgt.name] = outer_tgt

                # 后构建隐式连接，如 b-x b-y ，x-z x-w y-z y-w ，z-c w-c
                if outer_src in self.conntainer or outer_tgt in self.conntainer:
                    # outer_src 是 flow[a,b] ，构建 [a,b] 连接到 c
                    if outer_src in self.conntainer:
                        inner_sources: list[Connection] = self.conntainer.get(outer_src, [])
                        inner_targets: list[Connection] = [outer_tgt]
                    # outer_tgt 是 flow[a,b]，构建 c 连接到 [a,b]
                    if outer_tgt in self.conntainer:
                        inner_sources: list[Connection] = [outer_src]
                        inner_targets: list[Connection] = self.conntainer.get(outer_tgt, [])
                    # outer_src 是 flow[a,b] ，outer_tgt 是 flow[c,d]，构建 [a,b] 连接到 [c,d]
                    if outer_tgt in self.conntainer and outer_src in self.conntainer:
                        inner_sources: list[Connection] = self.conntainer.get(outer_src, [])
                        inner_targets: list[Connection] = self.conntainer.get(outer_tgt, [])
                    for inner_src in inner_sources:
                        inner_src_map: Dict[str, Connection] = self.hidden_connections.setdefault(inner_src, {})
                        for inner_tgt in inner_targets:
                            if inner_src is inner_tgt or inner_src is None or inner_tgt is None:  # 跳过自连接和空连接
                                continue
                            inner_src_map[inner_tgt.name] = inner_tgt

    def __rshift__(self, target: "Connection | list | tuple") -> "Connection":
        """重载运算符 >>
        - src 或 {"src":src} 或 [src] >> tgt 或 {"tgt":tgt} 或 [tgt]
        """
        # # 获取当前链路的最后一个节点作为目标
        self.build_connections(self.chains[-1], target)
        # 返回新的链路代理，链路尾部插入 target
        return Connection(chains=self.chains + [target])

    def __lshift__(self, source: Any) -> "Connection":
        """重载运算符 <<
        - target << source
        - [target1, target2] << source
        - {action: target, ...} << source
        - target << [source1, source2, ...]
        - target << {action: source, ...}
        使其逻辑与__rshift__保持一致，支持多种输入类型，并添加详细注释。
        """
        # 取当前链路的第一个节点作为目标，支持多种类型
        self.build_connections(source, self.chains[0])
        # 返回新的链路代理，链路头部插入 source
        return Connection(chains=[source] + self.chains)

    def __getitem__(self, key: "Connection | tuple | list | slice") -> Self:
        """
        重载运算符 []，获取子工作流

        连接类型：
        - flow[a] 单节点
        - flow[a >> b] 链路
        - flow[a, b] 多节点
        - flow[a:(b, c):(d, e)] 切片表达式，分段连接
        - flow[(a, b, c):(a, b, c)] 全连接
        - 支持action分支（dict）
        - 预留容器嵌套扩展点
        """

        def to_node_list(obj) -> list[Connection]:
            """将输入统一转为节点列表"""
            if isinstance(obj, Connection):
                return [obj]
            if isinstance(obj, (tuple, list)):
                return [*obj]
            return []

        conntainer: list[Connection] = self.conntainer.setdefault(self, [])

        # ⭐️ 处理切片表达式 flow[a:(b,c)]
        if isinstance(key, slice):
            # 支持三段式切片：start:stop:step
            starts: list[Connection] = to_node_list(key.start)
            stops: list[Connection] = to_node_list(key.stop)
            steps: list[Connection] = to_node_list(key.step)
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

        # ⭐️ 处理连接类型 flow[a>>b>>a]（a-b-a需要去重）
        elif isinstance(key, Connection):
            # 添加到容器，可以用于绘制mermaid流程图，{chain:[a,b]}
            for node in key.chains:
                if node not in conntainer:
                    conntainer.append(node)

        # ⭐️ 处理连接数组类型 flow[a,b,c]
        elif isinstance(key, (tuple, list)):
            for node in key:
                self.__getitem__(node)

        return self

    # endregion

    # region 执行流程
    def run(self, state: dict, max_steps: int = 10, entry_action: str = None) -> Any:
        """同步执行工作流的核心逻辑"""
        return asyncio.run(
            self.execute_workflow(state=state, remaining_steps=max_steps, entry_action=entry_action, is_async=False)
        )

    async def arun(self, state: dict, max_steps: int = 10, entry_action: str = None) -> Any:
        """异步执行工作流的核心逻辑"""
        return await self.execute_workflow(
            state=state, remaining_steps=max_steps, entry_action=entry_action, is_async=True
        )

    def execute_workflow(
        self, state: dict, remaining_steps: int = 10, entry_action: str = None, is_async: bool = False
    ) -> Any:
        """统一的工作流执行接口，Node 作为单节点工作流"""
        raise NotImplementedError("Node 类不支持 execute_workflow 方法")

    # endregion

    # region 绘制流程图
    def collect_clusters(self, visited=None):
        if visited is None:
            visited = set()
        if id(self) in visited:
            return []
        visited.add(id(self))
        lines = []
        if self in self.conntainer:
            lines.append(f"    subgraph cluster_{self.name} {{")
            lines.append(f'        label="{self.name}";')
            for node in self.conntainer[self]:
                sub_lines = node.collect_clusters(visited)
                for l in sub_lines:
                    lines.append("        " + l if l.strip() else "")
            # 添加锚点节点
            lines.append(f"        {self.name}[shape=point,width=0, height=0];")
            lines.append("    }")
        else:
            lines.append(f"    {self.name};")
        return lines

    def collect_edges(self, visited_edges=None, visited_nodes=None):
        if visited_edges is None:
            visited_edges = set()
        if visited_nodes is None:
            visited_nodes = set()
        lines = []
        for src, targets in self.connections.items():
            for act, tgt in targets.items():
                edge = (id(src), id(tgt), act)
                if edge not in visited_edges:
                    # 如果 src/tgt 是容器，则用锚点节点名
                    src_name = src.name if src in self.conntainer else src.name
                    tgt_name = tgt.name if tgt in self.conntainer else tgt.name
                    if src in self.conntainer:
                        src_name = src.name
                    if tgt in self.conntainer:
                        tgt_name = tgt.name
                    label = f' [label="{act}"]' if act and act != "default" else ""
                    lines.append(f"    {src_name} -> {tgt_name}{label};")
                    visited_edges.add(edge)
                # 递归目标节点
                if id(tgt) not in visited_nodes:
                    visited_nodes.add(id(tgt))
                    lines.extend(tgt.collect_edges(visited_edges, visited_nodes))
        return lines

    def collect_mermaid_edges(self, visited_edges=None, visited_nodes=None, cluster_points=None):
        if visited_edges is None:
            visited_edges = set()
        if visited_nodes is None:
            visited_nodes = set()
        if cluster_points is None:
            cluster_points = {}
        lines = []
        for src, targets in self.connections.items():
            for act, tgt in targets.items():
                edge = (id(src), id(tgt), act)
                if edge not in visited_edges:
                    src_is_container = src in self.conntainer
                    tgt_is_container = tgt in self.conntainer
                    if src_is_container or tgt_is_container:
                        if src_is_container and tgt_is_container:
                            src_point = f"{src.name}_{tgt.name}_src"
                            tgt_point = f"{src.name}_{tgt.name}_tgt"
                            cluster_points.setdefault(src.name, set()).add(src_point)
                            cluster_points.setdefault(tgt.name, set()).add(tgt_point)
                            label = f"{act}" if act and act != "default" else ""
                            lines.append(f"    {src_point} --{label}--> {tgt_point}")
                        elif src_is_container:
                            tgt_point = f"{src.name}_{tgt.name}_tgt"
                            cluster_points.setdefault(src.name, set()).add(tgt_point)
                            label = f"{act}" if act and act != "default" else ""
                            lines.append(f"    {src.name} --{label}--> {tgt_point}")
                        elif tgt_is_container:
                            src_point = f"{src.name}_{tgt.name}_src"
                            cluster_points.setdefault(tgt.name, set()).add(src_point)
                            label = f"{act}" if act and act != "default" else ""
                            lines.append(f"    {src_point} --{label}--> {tgt.name}")
                    else:
                        label = f"{act}" if act and act != "default" else ""
                        lines.append(f"    {src.name} --{label}--> {tgt.name}")
                    visited_edges.add(edge)
                if id(tgt) not in visited_nodes:
                    visited_nodes.add(id(tgt))
                    lines.extend(tgt.collect_mermaid_edges(visited_edges, visited_nodes, cluster_points))
        return lines

    def render_dot(self, saved_file: str = None):
        """生成dot格式文本，可选保存为图片，支持所有容器的 cluster 嵌套结构，保证无list混入"""

        lines = ["digraph G {", "    rankdir=TB;"]
        # 找到所有容器节点
        containers = list(self.conntainer.keys()) if hasattr(self, "conntainer") and self.conntainer else [self]
        visited = set()
        for container in containers:
            lines.extend(container.collect_clusters(visited))
        # 边
        visited_edges = set()
        visited_nodes = set()
        for container in containers:
            lines.extend(container.collect_edges(visited_edges, visited_nodes))
        # 标记起始节点
        # start_name = self.name if hasattr(self, "name") else "unknown"
        # lines.append(f'    {start_name} [style=filled, fillcolor="#f9f"];')
        lines.append("}")
        viz_str = "\n".join(lines)
        if saved_file:
            saved_filepath = Path.cwd() / saved_file
            saved_filepath.parent.mkdir(parents=True, exist_ok=True)
            with tempfile.NamedTemporaryFile("w+", suffix=".dot") as tmp_dot:
                tmp_dot.write(viz_str)
                tmp_dot.flush()
                s, o = subprocess.getstatusoutput(f"dot -Tpng {tmp_dot.name} -o {saved_filepath}")
                if s != 0:
                    warnings.warn(f"dot 生成图片失败，检查 dot 是否安装（brew install graphviz）: {o}")
                else:
                    print(f"图片已保存为: {saved_file}")
        return viz_str

    def to_mermaid(self, depth=0, visited=None):
        """将节点及其连接渲染为mermaid格式（只用connections和conntainer）"""
        if visited is None:
            visited = set()
        if id(self) in visited:
            return [], set()
        visited.add(id(self))
        lines = []
        used_nodes = {self.name}
        for src, targets in self.connections.items():
            for act, tgt in targets.items():
                label = f"--{act}-->" if act and act != "default" else "--->"
                lines.append(f"    {src.name} {label} {tgt.name}")
                if id(tgt) not in visited:
                    nested_lines, nested_nodes = tgt.to_mermaid(depth, visited)
                    lines.extend(nested_lines)
                    used_nodes.update(nested_nodes)
        return lines, used_nodes

    def render_mermaid(self, saved_file: str = None, title: str = ""):

        # 对 title 进行 YAML 安全处理，移除所有特殊字符
        safe_title = (
            str(title).replace('"', "").replace("'", "").replace("[", "").replace("]", "").replace("\n", " ").strip()
        )
        if not safe_title:
            safe_title = ""
        config_block = f"""---\ntitle: "{title}"\nconfig:\n  look: handDrawn\n---\n"""

        lines = ["graph TB"]
        clusters = list(self.conntainer.keys()) if hasattr(self, "conntainer") and self.conntainer else [self]
        declared_nodes = set()
        declared_clusters = set()
        cluster_internal_edges = []
        external_edges = []
        cluster_name_map = {}
        for cluster in clusters:
            members = self.conntainer.get(cluster, []) if hasattr(self, "conntainer") else []
            member_names = set(n.name for n in members)
            for node in members:
                cluster_name_map[node.name] = cluster.name
        processed_pairs = set()
        for cluster in clusters:
            members = self.conntainer.get(cluster, []) if hasattr(self, "conntainer") else []
            member_names = set(n.name for n in members)
            for src, targets in cluster.connections.items():
                for act, tgt in targets.items():
                    if src.name in member_names and tgt.name in member_names:
                        pair = tuple(sorted([src.name, tgt.name]))
                        if pair in processed_pairs:
                            continue
                        reverse_label = ""
                        if tgt in cluster.connections and src.name in cluster.connections[tgt]:
                            reverse_label = cluster.connections[tgt][src.name]
                        label1 = f"{act}" if act and act != "default" else ""
                        label2 = ""
                        if reverse_label:
                            label2 = f"{reverse_label}" if reverse_label and reverse_label != "default" else ""
                        if label1 or label2:
                            label = f"{label1} / {label2}".strip(" / ")
                        else:
                            label = ""
                        
                        # 根据是否有反向连接决定箭头类型
                        if reverse_label:
                            # 有反向连接，使用双向箭头
                            edge_str = (
                                f"    {src.name} <--> |{label}| {tgt.name}" if label else f"    {src.name} <--> {tgt.name}"
                            )
                        else:
                            # 只有单向连接，使用单向箭头
                            edge_str = (
                                f"    {src.name} --> |{label}| {tgt.name}" if label else f"    {src.name} --> {tgt.name}"
                            )
                        cluster_internal_edges.append((cluster.name, edge_str))
                        processed_pairs.add(pair)
                    else:
                        src_cluster = cluster_name_map.get(src.name, src.name)
                        tgt_cluster = cluster_name_map.get(tgt.name, tgt.name)
                        if src_cluster != tgt_cluster:
                            label = f"{act}" if act and act != "default" else ""
                            external_edges.append((src_cluster, tgt_cluster, label))
        for cluster in clusters:
            if cluster.name not in declared_clusters:
                lines.append(f"subgraph {cluster.name}")
                members = self.conntainer.get(cluster, []) if hasattr(self, "conntainer") else []
                for node in members:
                    if node.name not in declared_nodes:
                        lines.append(f"    {node.name}")
                        declared_nodes.add(node.name)
                for cname, edge in cluster_internal_edges:
                    if cname == cluster.name:
                        lines.append(edge)
                lines.append("end")
                declared_clusters.add(cluster.name)
        edge_set = set()
        for src, tgt, label in external_edges:
            edge_str = f"{src} --{label}--> {tgt}"
            if edge_str not in edge_set:
                lines.append(edge_str)
                edge_set.add(edge_str)
        viz_str = config_block + "\n".join(lines)
        if saved_file:
            saved_filepath = Path.cwd() / saved_file
            saved_filepath.parent.mkdir(parents=True, exist_ok=True)
            with tempfile.NamedTemporaryFile("w+", suffix=".mmd", delete=True) as tmp_mmd:
                tmp_mmd.write(viz_str)
                tmp_mmd.flush()
                s, o = subprocess.getstatusoutput(f"mmdc -i {tmp_mmd.name} -o {saved_filepath}")
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


if __name__ == "__main__":
    c1 = Connection()
    c2 = Connection()
    c3 = Connection()
    c4 = Connection()
    c5 = Connection()
    flow = Connection()
    # print((c1 >> c2 >> c3).chains)
    # print((c1 << [c2, c3] << c4
    # print((c1 << flow[c2, c3 >> c5] << c4
    # print((c1 << flow[c2, c3 >> c5] << c4).hidden_connections)


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
    n1 = Node()
    n2 = Node()
    n3 = Node()
    n4 = Node()
    n5 = Node()
    # fmt: off
    # n1 >> [n2 >> n3, n3 >>n4] >> n5; title=get_code_line()[0]
    # fmt: on
    # print(n1.connections)
    # print(n1.render_mermaid(saved_file="assets/node_mermaid.png", title=title))


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
