"""
智能体工作流集成模块
将智能体算法与工作流编排功能结合
"""

from typing import Dict, Any, List, Optional, Callable
from .core import Node, Flow
from .utils import (
    call_llm,
    get_embedding,
    search_web_duckduckgo,
    create_memory_system,
    create_rag_system,
    create_tool_manager,
    MCPToolManager,
    ConversationMemory,
    RAGSystem,
)


# ==================== 基础智能体节点 ====================


class LLMNode(Node):
    """LLM调用节点"""

    def __init__(
        self,
        name: str = "llm_node",
        model: str = "glm-4-flashx-250414",
        system_prompt: str = None,
        output_format: str = "text",
    ):
        super().__init__(name=name)
        self.model = model
        self.system_prompt = system_prompt
        self.output_format = output_format

    def exec(self, state: Dict[str, Any]):
        """执行LLM调用"""
        user_prompt = state.get("prompt", "")
        if not user_prompt:
            return {"error": "缺少prompt参数"}

        try:
            response = call_llm(
                user_prompt=user_prompt,
                system_prompt=self.system_prompt,
                model=self.model,
                output_format=self.output_format,
            )
            return {"llm_response": response}
        except Exception as e:
            return {"error": f"LLM调用失败: {str(e)}"}


class SearchNode(Node):
    """搜索节点"""

    def __init__(self, name: str = "search_node", search_engine: str = "duckduckgo"):
        super().__init__(name=name)
        self.search_engine = search_engine

    def exec(self, state: Dict[str, Any]):
        """执行搜索"""
        query = state.get("query", "")
        if not query:
            return {"error": "缺少query参数"}

        try:
            if self.search_engine == "duckduckgo":
                results = search_web_duckduckgo(query)
            else:
                results = f"不支持的搜索引擎: {self.search_engine}"

            return {"search_results": results}
        except Exception as e:
            return {"error": f"搜索失败: {str(e)}"}


class MemoryNode(Node):
    """记忆节点"""

    def __init__(self, name: str = "memory_node", max_messages: int = 10):
        super().__init__(name=name)
        self.memory = create_memory_system(max_messages)

    def exec(self, state: Dict[str, Any]):
        """处理记忆操作"""
        action = state.get("memory_action", "add")

        if action == "add":
            role = state.get("role", "user")
            content = state.get("content", "")
            if content:
                self.memory.add_message(role, content)
                return {"memory_status": "added", "message_count": len(self.memory.messages)}

        elif action == "get":
            count = state.get("count", 5)
            messages = self.memory.get_recent_messages(count)
            return {"recent_messages": messages}

        elif action == "search":
            query = state.get("query", "")
            if query:
                results = self.memory.search_similar_conversations(query)
                return {"similar_conversations": results}

        return {"error": f"不支持的记忆操作: {action}"}


class RAGNode(Node):
    """RAG节点"""

    def __init__(self, name: str = "rag_node"):
        super().__init__(name=name)
        self.rag = create_rag_system()

    def exec(self, state: Dict[str, Any]):
        """处理RAG操作"""
        action = state.get("rag_action", "retrieve")

        if action == "add_documents":
            documents = state.get("documents", [])
            if documents:
                self.rag.add_documents(documents)
                return {"documents_added": len(documents)}

        elif action == "build_index":
            try:
                self.rag.build_index()
                return {"index_built": True}
            except Exception as e:
                return {"error": f"索引构建失败: {str(e)}"}

        elif action == "retrieve":
            query = state.get("query", "")
            k = state.get("k", 3)
            if query:
                try:
                    results = self.rag.retrieve(query, k)
                    return {"retrieved_documents": results}
                except Exception as e:
                    return {"error": f"检索失败: {str(e)}"}

        elif action == "generate_answer":
            query = state.get("query", "")
            retrieved_docs = state.get("retrieved_documents", [])
            if query and retrieved_docs:
                try:
                    answer = self.rag.generate_answer(query, retrieved_docs)
                    return {"generated_answer": answer}
                except Exception as e:
                    return {"error": f"答案生成失败: {str(e)}"}

        return {"error": f"不支持的RAG操作: {action}"}


class ToolNode(Node):
    """工具调用节点"""

    def __init__(self, name: str = "tool_node"):
        super().__init__(name=name)
        self.tool_manager = create_tool_manager()

    def exec(self, state: Dict[str, Any]):
        """执行工具调用"""
        tool_name = state.get("tool_name", "")
        arguments = state.get("tool_arguments", {})

        if not tool_name:
            return {"error": "缺少tool_name参数"}

        try:
            result = self.tool_manager.call_tool(tool_name, arguments)
            return {"tool_result": result}
        except Exception as e:
            return {"error": f"工具调用失败: {str(e)}"}


# ==================== 高级智能体工作流 ====================


class ReActWorkflow:
    """ReAct工作流"""

    def __init__(self, tools: Optional[MCPToolManager] = None):
        self.tools = tools or create_tool_manager()
        self.flow = self._create_workflow()

    def _create_workflow(self) -> Flow:
        """创建ReAct工作流"""
        # 思考节点
        think_node = LLMNode(
            name="think",
            system_prompt="""你是一个ReAct代理，需要解决用户的问题。
请按照以下格式进行思考：
```yaml
reasoning: |
  <你的推理过程>
action: <要执行的动作名称>
action_input: <动作的输入参数>
```""",
            output_format="yaml",
        )

        # 行动节点
        action_node = ToolNode(name="act")

        # 观察节点
        observe_node = LLMNode(
            name="observe",
            system_prompt="""你是一个观察者，需要分析动作结果并提供客观观察。
请提供简洁的观察，不要做决策，只描述你看到的内容。""",
        )

        # 构建工作流
        think_node >> "continue" >> action_node >> "success" >> observe_node >> "continue" >> think_node
        think_node >> "final" >> "end"

        return Flow(start=think_node, name="react_workflow")

    def solve(self, query: str, max_iterations: int = 5) -> Dict[str, Any]:
        """解决问题"""
        state = {
            "query": query,
            "iteration": 0,
            "max_iterations": max_iterations,
            "thoughts": [],
            "actions": [],
            "observations": [],
        }

        # 运行工作流
        result = self.flow.run(state)

        return {
            "final_result": state.get("final_result"),
            "thoughts": state.get("thoughts", []),
            "actions": state.get("actions", []),
            "observations": state.get("observations", []),
            "iterations": state.get("iteration", 0),
        }


class TAOWorkflow:
    """TAO工作流"""

    def __init__(self, tools: Optional[MCPToolManager] = None):
        self.tools = tools or create_tool_manager()
        self.flow = self._create_workflow()

    def _create_workflow(self) -> Flow:
        """创建TAO工作流"""
        # 思考节点
        think_node = LLMNode(
            name="think",
            system_prompt="""你是一个TAO代理，需要解决用户的问题。
请按照以下格式进行思考：
```yaml
thinking: |
  <你的思考过程>
action: <要执行的动作名称>
action_input: <动作的输入参数>
is_final: <是否为最终答案>
```""",
            output_format="yaml",
        )

        # 行动节点
        action_node = ToolNode(name="act")

        # 观察节点
        observe_node = LLMNode(
            name="observe",
            system_prompt="""你是一个观察者，需要分析动作结果并提供客观观察。
请提供简洁的观察，不要做决策，只描述你看到的内容。""",
        )

        # 构建工作流
        think_node >> "continue" >> action_node >> "success" >> observe_node >> "continue" >> think_node
        think_node >> "final" >> "end"

        return Flow(start=think_node, name="tao_workflow")

    def solve(self, query: str, max_iterations: int = 5) -> Dict[str, Any]:
        """解决问题"""
        state = {
            "query": query,
            "iteration": 0,
            "max_iterations": max_iterations,
            "thoughts": [],
            "actions": [],
            "observations": [],
        }

        # 运行工作流
        result = self.flow.run(state)

        return {
            "final_result": state.get("final_result"),
            "thoughts": state.get("thoughts", []),
            "actions": state.get("actions", []),
            "observations": state.get("observations", []),
            "iterations": state.get("iteration", 0),
        }


class CoTWorkflow:
    """Chain of Thoughts工作流"""

    def __init__(self, max_steps: int = 5):
        self.max_steps = max_steps
        self.flow = self._create_workflow()

    def _create_workflow(self) -> Flow:
        """创建CoT工作流"""
        # 思考步骤节点
        think_node = LLMNode(
            name="think",
            system_prompt="""你正在使用Chain of Thoughts方法解决问题。
请提供你的推理过程，并说明下一步应该做什么。
如果这是最后一步，请提供最终答案。""",
        )

        # 构建工作流
        think_node >> "continue" >> think_node
        think_node >> "final" >> "end"

        return Flow(start=think_node, name="cot_workflow")

    def solve(self, query: str) -> Dict[str, Any]:
        """解决问题"""
        state = {"query": query, "step": 0, "max_steps": self.max_steps, "thoughts": [], "context": query}

        # 运行工作流
        result = self.flow.run(state)

        return {
            "final_answer": state.get("final_answer"),
            "thoughts": state.get("thoughts", []),
            "steps": state.get("step", 0),
        }


class RAGWorkflow:
    """RAG工作流"""

    def __init__(self):
        self.flow = self._create_workflow()

    def _create_workflow(self) -> Flow:
        """创建RAG工作流"""
        # 查询嵌入节点
        embed_node = Node(name="embed_query")

        # 检索节点
        retrieve_node = RAGNode(name="retrieve")

        # 生成答案节点
        generate_node = LLMNode(
            name="generate",
            system_prompt="""基于检索到的文档回答问题。
请提供准确、相关的答案。""",
        )

        # 构建工作流
        embed_node >> "default" >> retrieve_node >> "default" >> generate_node >> "default" >> "end"

        return Flow(start=embed_node, name="rag_workflow")

    def solve(self, query: str, documents: List[str]) -> Dict[str, Any]:
        """解决问题"""
        state = {"query": query, "documents": documents}

        # 运行工作流
        result = self.flow.run(state)

        return {
            "answer": state.get("generated_answer"),
            "retrieved_documents": state.get("retrieved_documents", []),
            "query_embedding": state.get("query_embedding"),
        }


# ==================== 工厂函数 ====================


def create_react_workflow(tools: Optional[MCPToolManager] = None) -> ReActWorkflow:
    """创建ReAct工作流"""
    return ReActWorkflow(tools)


def create_tao_workflow(tools: Optional[MCPToolManager] = None) -> TAOWorkflow:
    """创建TAO工作流"""
    return TAOWorkflow(tools)


def create_cot_workflow(max_steps: int = 5) -> CoTWorkflow:
    """创建CoT工作流"""
    return CoTWorkflow(max_steps)


def create_rag_workflow() -> RAGWorkflow:
    """创建RAG工作流"""
    return RAGWorkflow()


def create_llm_node(name: str = "llm_node", **kwargs) -> LLMNode:
    """创建LLM节点"""
    return LLMNode(name=name, **kwargs)


def create_search_node(name: str = "search_node", **kwargs) -> SearchNode:
    """创建搜索节点"""
    return SearchNode(name=name, **kwargs)


def create_memory_node(name: str = "memory_node", **kwargs) -> MemoryNode:
    """创建记忆节点"""
    return MemoryNode(name=name, **kwargs)


def create_rag_node(name: str = "rag_node", **kwargs) -> RAGNode:
    """创建RAG节点"""
    return RAGNode(name=name, **kwargs)


def create_tool_node(name: str = "tool_node", **kwargs) -> ToolNode:
    """创建工具节点"""
    return ToolNode(name=name, **kwargs)
