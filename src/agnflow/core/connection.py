from typing import Any, Dict, Literal, TypeVar, Generic
import asyncio
from pathlib import Path
import re

from agnflow.utils.code import get_code_line

StateType = TypeVar("StateType", bound=dict)

class Connection(Generic[StateType]):
    """连接关系（节点与容器）

    特性：
    - 支持节点与容器关联
    - 支持容器嵌套容器
    - 支持复杂连接方式，如切片、全连接
    - 支持基于action的分支连接
    - 支持mermaid流程图绘制
    - 支持运行时动态添加连接

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
    """全局工作流节点连接"""
    conntainer: "dict[Connection,list[Connection]]" = {}  # 区分内连接和外连接的容器
    """全局工作流节点容器"""
    hidden_connections: "dict[Connection,dict[str,Connection]]" = {}  # {source: {action: target}}
    """全局工作流节点隐式连接"""

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
    def all_connections(self) -> "Dict[Connection, Dict[str, Connection]]":
        """合并所有连接"""
        return {
            key: {**self.hidden_connections.get(key, {}), **self.connections.get(key, {})}
            for key in self.hidden_connections | self.connections
        }

    # region 构建流程图（包含节点与容器关联）
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
                # 如果是 Connection 本身，返回其 chains 中的所有节点
                return [objs.chains[0]]
            elif isinstance(objs, (list, tuple)):
                # 如果是列表，递归处理每个元素
                result = []
                for obj in objs:
                    # 递归处理每个元素，确保结果都是Connection对象
                    sub_result = convert_to_conn_list(obj)
                    result.extend(sub_result)
                return result
            return []

        # 获取当前链路的最后一个节点作为目标
        sources: list[Connection] = convert_to_conn_list(source)
        targets: list[Connection] = convert_to_conn_list(target)

        # 建立连接关系，如 a -> b -> flow1[x,y] -> flow2[z,w] -> c
        # 1. 先构建显式连接 如 a-b-flow1-flow2-c
        for outer_src in sources:
            outer_src_map: Dict[str, Connection] = self.connections.setdefault(outer_src, {})
            for outer_tgt in targets:
                outer_src_map[outer_tgt.name] = outer_tgt

                # 2.后构建隐式连接，如 b-x b-y ，x-z x-w y-z y-w ，z-c w-c
                if outer_src in self.conntainer or outer_tgt in self.conntainer:
                    # 2.1 flow[a,b] >> c
                    if outer_src in self.conntainer:
                        inner_sources: list[Connection] = self.conntainer.get(outer_src, [])
                        inner_targets: list[Connection] = [outer_tgt]
                    # 2.2 c >> flow[a,b]
                    if outer_tgt in self.conntainer:
                        inner_sources: list[Connection] = [outer_src]
                        inner_targets: list[Connection] = self.conntainer.get(outer_tgt, [])
                    # 2.3 flow[a,b] >> flow[c,d]
                    if outer_tgt in self.conntainer and outer_src in self.conntainer:
                        inner_sources: list[Connection] = self.conntainer.get(outer_src, [])
                        inner_targets: list[Connection] = self.conntainer.get(outer_tgt, [])

                    # 确保inner_sources和inner_targets中都是Connection对象
                    inner_sources = [src for src in inner_sources if isinstance(src, Connection)]
                    inner_targets = [tgt for tgt in inner_targets if isinstance(tgt, Connection)]

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

    def __sub__(self, target: "Connection | list | tuple") -> "Connection":
        """重载运算符 - 用于断开连接
        - c1 - c2 表示断开 c1 到 c2 的连接
        - c1 - [c2, c3] 表示断开 c1 到 c2, c3 的所有连接
        - c1 - flow[c2, c3] 表示断开 c1 到容器内所有节点的连接
        - c1 - c2 - c3 表示链式断开连接
        """
        # 如果 target 是 Connection 且有 chains，说明是链式断开
        if isinstance(target, Connection) and hasattr(target, 'chains') and len(target.chains) > 1:
            # 链式断开：c1 - c2 - c3
            self.disconnect_from(target.chains[0])  # 断开到第一个节点
            # 返回一个新的 Connection 对象，继续链式操作
            return Connection(chains=target.chains[1:])
        else:
            # 普通断开
            self.disconnect_from(target)
            return self

    def __rsub__(self, source: "Connection | list | tuple") -> "Connection":
        """重载运算符 - 的右操作数版本
        - source - self 用于处理链式断开连接
        """
        if isinstance(source, Connection):
            source.disconnect_from(self)
            return source
        else:
            # 如果 source 是列表或元组，创建一个临时的 Connection 来处理
            temp_conn = Connection()
            temp_conn.disconnect_from(self)
            return temp_conn

    def disconnect_from(self, target: "Connection | list | tuple"):
        """断开连接的核心逻辑"""
        def convert_to_conn_list(objs) -> "list[Connection]":
            if isinstance(objs, Connection):
                # 如果是 Connection 子类（如 Node、Flow...），直接返回
                if objs.__class__ != Connection:
                    return [objs]
                # 如果是 Connection 本身，返回其 chains 中的所有节点
                return [objs.chains[0]]
            elif isinstance(objs, (list, tuple)):
                # 如果是列表，递归处理每个元素
                result = []
                for obj in objs:
                    # 递归处理每个元素，确保结果都是Connection对象
                    sub_result = convert_to_conn_list(obj)
                    result.extend(sub_result)
                return result
            return []

        sources = [self.chains[-1]]  # 当前链路的最后一个节点
        targets = convert_to_conn_list(target)

        # 1. 断开显式连接
        for src in sources:
            if src in self.connections:
                for tgt in targets:
                    if tgt.name in self.connections[src]:
                        del self.connections[src][tgt.name]
                # 如果该源节点的连接映射为空，删除整个映射
                if not self.connections[src]:
                    del self.connections[src]

        # 2. 断开隐式连接
        for src in sources:
            if src in self.hidden_connections:
                for tgt in targets:
                    if tgt.name in self.hidden_connections[src]:
                        del self.hidden_connections[src][tgt.name]
                if not self.hidden_connections[src]:
                    del self.hidden_connections[src]

        # 3. 处理容器关系
        for src in sources:
            if src in self.conntainer:
                # 从容器中移除目标节点
                container_nodes = self.conntainer[src]
                for tgt in targets:
                    if tgt in container_nodes:
                        container_nodes.remove(tgt)
                # 如果容器为空，删除容器
                if not container_nodes:
                    del self.conntainer[src]

    # endregion

    # region 执行流程
    def run(self, state: StateType, max_steps: int = 10, entry_action: str = None) -> Any:
        """同步执行工作流的核心逻辑"""
        return asyncio.run(
            self.execute_workflow(state=state, remaining_steps=max_steps, entry_action=entry_action, is_async=False)
        )

    async def arun(self, state: StateType, max_steps: int = 10, entry_action: str = None) -> Any:
        """异步执行工作流的核心逻辑"""
        return await self.execute_workflow(
            state=state, remaining_steps=max_steps, entry_action=entry_action, is_async=True
        )

    def execute_workflow(
        self, state: StateType, remaining_steps: int = 10, entry_action: str = None, is_async: bool = False
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

    def render_dot(self, saved_file: str = None, format: Literal["png", "svg", "pdf"] = "png"):
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
        lines.append("}")
        viz_str = "\n".join(lines)
        if saved_file:
            saved_filepath = Path.cwd() / saved_file
            saved_filepath = saved_filepath.with_suffix("")
            saved_filepath.parent.mkdir(parents=True, exist_ok=True)

            def dot_to_png(script, filename, format="png"):
                import graphviz

                graph = graphviz.Source(script)
                graph.render(filename=filename, format=format, cleanup=True)
            dot_to_png(viz_str, saved_filepath, format)
            return viz_str, saved_filepath
        return viz_str, None

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

    def render_mermaid(
        self,
        saved_file: str = None,
        title: str = "",
        theme: Literal["default", "neutral", "dark", "forest", "base"] = "forest",
    ):
        """渲染 Mermaid 流程图
        
        Args:
            saved_file: 保存文件路径，如果为 None 则只返回文本
            title: 图表标题
            theme: 主题
        """
        config_block = f"""---
title: "{title}"
config:
  look: handDrawn
  theme: {theme}
---
"""

        lines = ["graph TB"]
        clusters = list(self.conntainer.keys()) if hasattr(self, "conntainer") and self.conntainer else [self]
        declared_nodes = set()
        declared_clusters = set()
        cluster_internal_edges = []
        external_edges = []
        cluster_name_map = {}
        for cluster in clusters:
            members = self.conntainer.get(cluster, []) if hasattr(self, "conntainer") else []
            # 过滤掉非Connection对象
            members = [m for m in members if isinstance(m, Connection)]
            member_names = set(n.name for n in members)
            for node in members:
                cluster_name_map[node.name] = cluster.name
        processed_pairs = set()
        for cluster in clusters:
            members = self.conntainer.get(cluster, []) if hasattr(self, "conntainer") else []
            # 过滤掉非Connection对象
            members = [m for m in members if isinstance(m, Connection)]
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
                                f"    {src.name} <--> |{label}| {tgt.name}"
                                if label
                                else f"    {src.name} <--> {tgt.name}"
                            )
                        else:
                            # 只有单向连接，使用单向箭头
                            edge_str = (
                                f"    {src.name} --> |{label}| {tgt.name}"
                                if label
                                else f"    {src.name} --> {tgt.name}"
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
                # 过滤掉非Connection对象
                members = [m for m in members if isinstance(m, Connection)]
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
            def mermaid_to_png(script,filename):
                import base64
                import io, requests
                from PIL import Image as im

                graphbytes = script.encode("utf8")
                base64_bytes = base64.urlsafe_b64encode(graphbytes)
                base64_string = base64_bytes.decode("ascii")
                img = im.open(io.BytesIO(requests.get("https://mermaid.ink/img/" + base64_string).content))
                img.save(filename)
            mermaid_to_png(viz_str, saved_filepath)
            return viz_str, saved_filepath
        return viz_str, None

    # endregion


if __name__ == "__main__":
    c1 = Connection()
    c2 = Connection()
    c3 = Connection()
    c4 = Connection()
    c5 = Connection()
    flow = Connection()
    c1 >> c2
    c1 >> c3
    print(c1.connections, c1.conntainer, c1.hidden_connections)
    # print((c1 >> c2 >> c3).chains)
    # print((c1 << [c2, c3] << c4
    # print((c1 << flow[c2, c3 >> c5] << c4
    # print((c1 << flow[c2, c3 >> c5] << c4).hidden_connections)
    # print(c1.render_mermaid(saved_file="assets/test.png"))
    # print(c1.render_dot(saved_file="assets/test.svg", format="svg"))
