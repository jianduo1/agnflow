"""

### TODO 清单

- [x] llm
- [x] memory
- [x] rag
- [x] mcp tool
- [x] ReAct(reasoning + action)
- [x] TAO(thought + action + observation)
- [x] ToT(Chain of Thought)
- [x] CoT(Chain of Thought)
- [x] hitl(human in the loop)
- [x] supervisor swarm

"""

from typing import Literal, List, Dict
import os
from datetime import datetime
import uuid
import yaml
import json
import requests
from dotenv import load_dotenv
from openai import OpenAI
from duckduckgo_search import DDGS
import numpy as np
from sklearn.neighbors import NearestNeighbors

load_dotenv()


def call_llm(user_prompt, system_prompt=None, model="glm-4-flashx-250414", output_format: Literal["yaml", "json", "text"] = "text"):
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    messages = [{"role": "user", "content": user_prompt}]
    if system_prompt:
        messages.insert(0, {"role": "system", "content": system_prompt})
    completion = client.chat.completions.create(model=model, messages=messages)
    res = completion.choices[0].message.content
    if output_format == "text":
        return res
    if output_format == "yaml":
        res = res.strip().removeprefix("```yaml").removesuffix("```").strip()
        return yaml.safe_load(res)
    elif output_format == "json":
        res = res.strip().removeprefix("```json").removesuffix("```").strip()
        return json.loads(res)
    raise ValueError(f"不支持的输出格式: {output_format}")


def search_web_duckduckgo(query):
    results = DDGS().text(query, max_results=5)
    # Convert results to a string
    results_str = "\n\n".join([f"Title: {r['title']}\nURL: {r['href']}\nSnippet: {r['body']}" for r in results])
    return results_str


def search_web_brave(query):

    url = f"https://api.search.brave.com/res/v1/web/search?q={query}"
    api_key = os.getenv("BRAVE_SEARCH_API_KEY")

    headers = {"accept": "application/json", "Accept-Encoding": "gzip", "x-subscription-token": api_key}

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        results = data['web']['results']
        results_str = "\n\n".join([f"Title: {r['title']}\nURL: {r['url']}\nDescription: {r['description']}" for r in results])
        return results_str
    else:
        print(f"请求失败，状态码: {response.status_code}")


def get_embedding(text):
    client = OpenAI(base_url=os.getenv("EMBEDDING_BASE_URL"), api_key=os.getenv("EMBEDDING_API_KEY"))

    response = client.embeddings.create(model=os.getenv("EMBEDDING_MODEL_NAME"), input=text)

    # 从响应中提取 embedding 向量
    embedding = response.data[0].embedding

    # 转换为 numpy array 用于一致性
    return np.array(embedding, dtype=np.float32)


def get_similarity(text1, text2):
    emb1 = get_embedding(text1)
    emb2 = get_embedding(text2)
    return np.dot(emb1, emb2)


# ==================== Memory 功能 ====================


class ConversationMemory:
    """对话记忆管理类"""

    def __init__(self, max_messages=10):
        self.messages = []
        self.max_messages = max_messages
        self.vector_index = None
        self.vector_items = []

    def add_message(self, role: str, content: str):
        """添加消息到记忆"""
        message = {"id": str(uuid.uuid4()), "role": role, "content": content, "timestamp": datetime.now().isoformat()}
        self.messages.append(message)

        # 保持消息数量在限制内
        if len(self.messages) > self.max_messages:
            self.messages.pop(0)

    def get_recent_messages(self, count=5):
        """获取最近的消息"""
        return self.messages[-count:] if len(self.messages) >= count else self.messages

    def get_context(self):
        """获取对话上下文"""
        return [{"role": msg["role"], "content": msg["content"]} for msg in self.messages]

    def create_vector_index(self):
        """创建向量索引"""
        if not self.vector_items:
            return None

        embeddings = np.array([item["embedding"] for item in self.vector_items], dtype=np.float32)
        index = NearestNeighbors(n_neighbors=10, metric="cosine").fit(embeddings)

        return index

    def add_to_vector_store(self, conversation_pair, embedding):
        """添加对话对到向量存储"""
        item = {"conversation": conversation_pair, "embedding": embedding}
        self.vector_items.append(item)
        self.vector_index = self.create_vector_index()

    def search_similar_conversations(self, query, k=1):
        """搜索相似对话"""
        if not self.vector_index or not self.vector_items:
            return []

        query_embedding = get_embedding(query)
        query_embedding = np.array([query_embedding], dtype=np.float32)

        # 使用k_neighbors方法，限制返回的邻居数量
        k = min(k, len(self.vector_items))
        distances, indices = self.vector_index.kneighbors(query_embedding, n_neighbors=k)

        results = []
        for i, idx in enumerate(indices[0]):
            if idx < len(self.vector_items):
                results.append({"conversation": self.vector_items[idx]["conversation"], "distance": distances[0][i]})

        return results


# ==================== RAG 功能 ====================


class RAGSystem:
    """检索增强生成系统"""

    def __init__(self):
        self.documents = []
        self.embeddings = None
        self.index = None

    def add_documents(self, texts: List[str]):
        """添加文档"""
        self.documents.extend(texts)

    def chunk_text(self, text: str, chunk_size: int = 1000, overlap: int = 200):
        """将文本分块"""
        chunks = []
        start = 0
        while start < len(text):
            end = start + chunk_size
            chunk = text[start:end]
            chunks.append(chunk)
            start = end - overlap
        return chunks

    def create_embeddings(self):
        """为所有文档创建嵌入"""
        if not self.documents:
            return

        all_embeddings = []
        for doc in self.documents:
            embedding = get_embedding(doc)
            all_embeddings.append(embedding)

        self.embeddings = np.array(all_embeddings, dtype=np.float32)

    def build_index(self):
        """构建搜索索引"""
        if self.embeddings is None:
            self.create_embeddings()

        if self.embeddings is None or len(self.embeddings) == 0:
            return

        self.index = NearestNeighbors(n_neighbors=10, metric="cosine").fit(self.embeddings)

    def retrieve(self, query: str, k: int = 3):
        """检索相关文档"""
        if self.index is None:
            self.build_index()

        if self.index is None:
            return []

        query_embedding = get_embedding(query)
        query_embedding = np.array([query_embedding], dtype=np.float32)

        # 使用k_neighbors方法，限制返回的邻居数量
        k = min(k, len(self.documents))
        distances, indices = self.index.kneighbors(query_embedding, n_neighbors=k)

        results = []
        for i, idx in enumerate(indices[0]):
            if idx < len(self.documents):
                results.append({"document": self.documents[idx], "distance": distances[0][i], "index": idx})

        return results

    def generate_answer(self, query: str, retrieved_docs: List[Dict]):
        """基于检索的文档生成答案"""
        context = "\n\n".join([doc["document"] for doc in retrieved_docs])

        prompt = f"""
基于以下上下文回答问题：

上下文：
{context}

问题：{query}

答案：
"""

        return call_llm(prompt)


# ==================== MCP Tool 功能 ====================


class MCPToolManager:
    """MCP工具管理器"""

    def __init__(self):
        self.tools = {}
        self.mcp_enabled = False

    def register_tool(self, name: str, description: str, function: callable, input_schema: Dict = None):
        """注册工具"""
        self.tools[name] = {"description": description, "function": function, "input_schema": input_schema or {}}

    def get_available_tools(self):
        """获取可用工具列表"""
        return [{"name": name, "description": tool["description"], "input_schema": tool["input_schema"]} for name, tool in self.tools.items()]

    def call_tool(self, tool_name: str, arguments: Dict):
        """调用工具"""
        if tool_name not in self.tools:
            raise ValueError(f"工具 '{tool_name}' 不存在")

        tool = self.tools[tool_name]
        return tool["function"](**arguments)

    def enable_mcp(self, server_script_path: str = None):
        """启用MCP支持"""
        self.mcp_enabled = True
        # 这里可以添加实际的MCP客户端初始化代码
        print("MCP支持已启用")


# ==================== ReAct 功能 ====================


class ReActAgent:
    """ReAct (Reasoning + Action) 代理"""

    def __init__(self, tools: MCPToolManager = None):
        self.tools = tools or MCPToolManager()
        self.thoughts = []
        self.actions = []
        self.observations = []

    def think(self, query: str):
        """思考阶段"""
        context = self._build_context()

        prompt = f"""
你是一个ReAct代理，需要解决用户的问题。

用户问题：{query}

可用工具：
{self._format_tools()}

历史记录：
{context}

请按照以下格式进行思考：
```yaml
reasoning: |
  <你的推理过程>
action: <要执行的动作名称>
action_input: <动作的输入参数>
```

请基于推理选择最合适的动作。
"""

        response = call_llm(prompt, output_format="yaml")
        return response

    def act(self, action_name: str, action_input: Dict):
        """执行动作"""
        try:
            result = self.tools.call_tool(action_name, action_input)
            return {"success": True, "result": result}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def observe(self, action_result: Dict):
        """观察结果"""
        return f"动作执行结果：{action_result}"

    def solve(self, query: str, max_iterations: int = 5):
        """解决完整问题"""
        for i in range(max_iterations):
            # 思考
            thought = self.think(query)
            self.thoughts.append(thought)

            # 执行动作
            action_result = self.act(thought["action"], thought["action_input"])
            self.actions.append(action_result)

            # 观察
            observation = self.observe(action_result)
            self.observations.append(observation)

            # 检查是否完成
            if action_result.get("success") and "final_answer" in action_result.get("result", ""):
                return action_result["result"]

        return "达到最大迭代次数，问题未完全解决"

    def _build_context(self):
        """构建上下文"""
        context_parts = []

        for i, (thought, action, obs) in enumerate(zip(self.thoughts, self.actions, self.observations)):
            context_parts.append(f"步骤 {i+1}:")
            context_parts.append(f"  思考: {thought.get('reasoning', '')}")
            context_parts.append(f"  动作: {thought.get('action', '')}")
            context_parts.append(f"  结果: {obs}")

        return "\n".join(context_parts)

    def _format_tools(self):
        """格式化工具列表"""
        tools = self.tools.get_available_tools()
        formatted = []
        for tool in tools:
            formatted.append(f"- {tool['name']}: {tool['description']}")
        return "\n".join(formatted)


# ==================== TAO 功能 ====================


class TAOAgent:
    """TAO (Thought + Action + Observation) 代理"""

    def __init__(self, tools: MCPToolManager = None):
        self.tools = tools or MCPToolManager()
        self.thoughts = []
        self.actions = []
        self.observations = []

    def think(self, query: str):
        """思考阶段"""
        context = self._build_context()

        prompt = f"""
你是一个TAO代理，需要解决用户的问题。

用户问题：{query}

可用工具：
{self._format_tools()}

历史记录：
{context}

请按照以下格式进行思考：
```yaml
thinking: |
  <你的思考过程>
action: <要执行的动作名称>
action_input: <动作的输入参数>
is_final: <是否为最终答案>
```

请基于思考选择最合适的动作。
"""

        response = call_llm(prompt, output_format="yaml")
        return response

    def act(self, action_name: str, action_input: Dict):
        """执行动作"""
        try:
            if action_name == "answer":
                return {"success": True, "result": action_input}
            else:
                result = self.tools.call_tool(action_name, action_input)
                return {"success": True, "result": result}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def observe(self, action_result: Dict):
        """观察结果"""
        prompt = f"""
分析以下动作结果并提供观察：

动作结果：{action_result}

请提供客观的观察，不要做决策，只描述你看到的内容。
"""

        observation = call_llm(prompt)
        return observation

    def solve(self, query: str, max_iterations: int = 5):
        """解决完整问题"""
        for i in range(max_iterations):
            # 思考
            thought = self.think(query)
            self.thoughts.append(thought)

            # 执行动作
            action_result = self.act(thought["action"], thought["action_input"])
            self.actions.append(action_result)

            # 观察
            observation = self.observe(action_result)
            self.observations.append(observation)

            # 检查是否完成
            if thought.get("is_final", False):
                return action_result.get("result", "完成")

        return "达到最大迭代次数，问题未完全解决"

    def _build_context(self):
        """构建上下文"""
        context_parts = []

        for i, (thought, action, obs) in enumerate(zip(self.thoughts, self.actions, self.observations)):
            context_parts.append(f"步骤 {i+1}:")
            context_parts.append(f"  思考: {thought.get('thinking', '')}")
            context_parts.append(f"  动作: {thought.get('action', '')}")
            context_parts.append(f"  观察: {obs}")

        return "\n".join(context_parts)

    def _format_tools(self):
        """格式化工具列表"""
        tools = self.tools.get_available_tools()
        formatted = []
        for tool in tools:
            formatted.append(f"- {tool['name']}: {tool['description']}")
        return "\n".join(formatted)


# ==================== ToT (Tree of Thoughts) 功能 ====================


class ToTNode:
    """ToT节点"""

    def __init__(self, thought: str, parent=None):
        self.thought = thought
        self.parent = parent
        self.children = []
        self.value = None
        self.status = "pending"  # pending, evaluated, expanded

    def add_child(self, thought: str):
        """添加子节点"""
        child = ToTNode(thought, self)
        self.children.append(child)
        return child

    def evaluate(self, evaluator_func):
        """评估节点"""
        self.value = evaluator_func(self.thought)
        self.status = "evaluated"
        return self.value


class ToTAgent:
    """Tree of Thoughts 代理"""

    def __init__(self, evaluator_func=None):
        self.evaluator_func = evaluator_func or self._default_evaluator
        self.root = None
        self.max_depth = 3
        self.max_breadth = 5

    def solve(self, query: str):
        """使用ToT解决问题"""
        self.root = ToTNode(f"开始解决: {query}")

        # 生成初始想法
        initial_thoughts = self._generate_thoughts(query, self.root)
        for thought in initial_thoughts:
            self.root.add_child(thought)

        # 扩展和评估树
        self._expand_tree(self.root, depth=0)

        # 找到最佳路径
        best_path = self._find_best_path(self.root)

        return self._extract_solution(best_path)

    def _generate_thoughts(self, context: str, parent_node: ToTNode):
        """生成想法"""
        prompt = f"""
基于以下上下文，生成3-5个不同的思考方向：

上下文：{context}
当前思考：{parent_node.thought}

请生成不同的思考方向，每个方向应该是一个具体的步骤或想法。
"""

        response = call_llm(prompt)
        thoughts = [line.strip() for line in response.split('\n') if line.strip()]
        return thoughts[: self.max_breadth]

    def _expand_tree(self, node: ToTNode, depth: int):
        """扩展树"""
        if depth >= self.max_depth:
            return

        # 评估当前节点
        node.evaluate(self.evaluator_func)

        # 如果节点有价值，继续扩展
        if node.value and node.value > 0.5:
            thoughts = self._generate_thoughts(node.thought, node)
            for thought in thoughts:
                child = node.add_child(thought)
                self._expand_tree(child, depth + 1)

    def _find_best_path(self, node: ToTNode):
        """找到最佳路径"""
        if not node.children:
            return [node]

        best_child = max(node.children, key=lambda x: x.value or 0)
        best_path = self._find_best_path(best_child)
        return [node] + best_path

    def _extract_solution(self, path: List[ToTNode]):
        """提取解决方案"""
        solution_parts = [node.thought for node in path]
        return "\n".join(solution_parts)

    def _default_evaluator(self, thought: str):
        """默认评估函数"""
        prompt = f"""
评估以下思考的质量（0-1分）：

思考：{thought}

请只返回一个0到1之间的数字，表示这个思考的质量。
"""

        try:
            response = call_llm(prompt)
            return float(response.strip())
        except:
            return 0.5


# ==================== CoT (Chain of Thoughts) 功能 ====================


class CoTAgent:
    """Chain of Thoughts 代理"""

    def __init__(self):
        self.thoughts = []

    def solve(self, query: str, max_steps: int = 5):
        """使用CoT解决问题"""
        current_context = query

        for step in range(max_steps):
            # 生成下一步思考
            thought = self._generate_thought(current_context, step + 1)
            self.thoughts.append(thought)

            # 更新上下文
            current_context = f"{current_context}\n\n步骤 {step + 1}: {thought}"

            # 检查是否完成
            if "最终答案" in thought or step == max_steps - 1:
                break

        return self._extract_final_answer()

    def _generate_thought(self, context: str, step: int):
        """生成思考步骤"""
        prompt = f"""
你正在使用Chain of Thoughts方法解决问题。

当前问题：{context}

这是第 {step} 步思考。请提供你的推理过程，并说明下一步应该做什么。
如果这是最后一步，请提供最终答案。
"""

        return call_llm(prompt)

    def _extract_final_answer(self):
        """提取最终答案"""
        if not self.thoughts:
            return "没有生成任何思考"

        # 尝试从最后一个思考中提取答案
        last_thought = self.thoughts[-1]

        # 简单的答案提取逻辑
        if "最终答案" in last_thought:
            # 提取最终答案部分
            answer_start = last_thought.find("最终答案")
            if answer_start != -1:
                return last_thought[answer_start:]

        return last_thought


# ==================== HITL (Human in the Loop) 功能 ====================


class HITLAgent:
    """Human in the Loop 代理"""

    def __init__(self, auto_mode=False):
        self.auto_mode = auto_mode
        self.history = []

    def process_with_human(self, query: str, context: str = ""):
        """处理需要人工干预的查询"""
        # 分析是否需要人工干预
        needs_human = self._analyze_human_needed(query, context)

        if needs_human and not self.auto_mode:
            # 请求人工输入
            human_input = self._get_human_input(query, context)
            self.history.append({"query": query, "context": context, "human_input": human_input, "timestamp": datetime.now().isoformat()})
            return human_input
        else:
            # 自动处理
            result = self._auto_process(query, context)
            self.history.append({"query": query, "context": context, "auto_result": result, "timestamp": datetime.now().isoformat()})
            return result

    def _analyze_human_needed(self, query: str, context: str):
        """分析是否需要人工干预"""
        prompt = f"""
分析以下查询是否需要人工干预：

查询：{query}
上下文：{context}

请判断是否需要人工干预，返回 "yes" 或 "no"。
需要人工干预的情况包括：
- 需要主观判断
- 涉及敏感信息
- 需要创造性思维
- 需要专业知识
"""

        response = call_llm(prompt).lower().strip()
        return "yes" in response

    def _get_human_input(self, query: str, context: str):
        """获取人工输入"""
        print(f"\n🤖 需要人工干预:")
        print(f"查询: {query}")
        if context:
            print(f"上下文: {context}")
        print("请输入你的回答:")

        return input("> ")

    def _auto_process(self, query: str, context: str):
        """自动处理"""
        prompt = f"""
自动处理以下查询：

查询：{query}
上下文：{context}

请提供合适的回答。
"""

        return call_llm(prompt)

    def get_history(self):
        """获取历史记录"""
        return self.history


# ==================== Supervisor Swarm 功能 ====================


class SupervisorAgent:
    """监督代理"""

    def __init__(self, name: str, criteria: List[str]):
        self.name = name
        self.criteria = criteria
        self.approvals = 0
        self.rejections = 0

    def evaluate(self, result: str, context: str = ""):
        """评估结果"""
        prompt = f"""
你是监督代理 {self.name}，负责评估结果质量。

评估标准：{', '.join(self.criteria)}

结果：{result}
上下文：{context}

请评估这个结果是否符合标准，返回 "approve" 或 "reject" 以及原因。
"""

        response = call_llm(prompt).lower()

        if "approve" in response:
            self.approvals += 1
            return {"decision": "approve", "reason": response}
        else:
            self.rejections += 1
            return {"decision": "reject", "reason": response}


class SupervisorSwarm:
    """监督者群体"""

    def __init__(self):
        self.supervisors = []
        self.consensus_threshold = 0.7

    def add_supervisor(self, name: str, criteria: List[str]):
        """添加监督者"""
        supervisor = SupervisorAgent(name, criteria)
        self.supervisors.append(supervisor)

    def evaluate_result(self, result: str, context: str = ""):
        """群体评估结果"""
        if not self.supervisors:
            return {"decision": "approve", "reason": "没有监督者"}

        evaluations = []
        for supervisor in self.supervisors:
            evaluation = supervisor.evaluate(result, context)
            evaluations.append(evaluation)

        # 计算批准率
        approvals = sum(1 for eval in evaluations if eval["decision"] == "approve")
        approval_rate = approvals / len(evaluations)

        # 收集所有原因
        reasons = [eval["reason"] for eval in evaluations]

        if approval_rate >= self.consensus_threshold:
            return {"decision": "approve", "approval_rate": approval_rate, "reasons": reasons}
        else:
            return {"decision": "reject", "approval_rate": approval_rate, "reasons": reasons}

    def get_supervisor_stats(self):
        """获取监督者统计信息"""
        stats = []
        for supervisor in self.supervisors:
            total = supervisor.approvals + supervisor.rejections
            approval_rate = supervisor.approvals / total if total > 0 else 0
            stats.append(
                {"name": supervisor.name, "approvals": supervisor.approvals, "rejections": supervisor.rejections, "approval_rate": approval_rate}
            )
        return stats


# ==================== 工具函数 ====================


def create_memory_system(max_messages=10) -> ConversationMemory:
    """创建记忆系统"""
    return ConversationMemory(max_messages)


def create_rag_system() -> RAGSystem:
    """创建RAG系统"""
    return RAGSystem()


def create_tool_manager() -> MCPToolManager:
    """创建工具管理器"""
    return MCPToolManager()


def create_react_agent(tools=None) -> ReActAgent:
    """创建ReAct代理"""
    return ReActAgent(tools)


def create_tao_agent(tools=None) -> TAOAgent:
    """创建TAO代理"""
    return TAOAgent(tools)


def create_tot_agent(evaluator_func=None) -> ToTAgent:
    """创建ToT代理"""
    return ToTAgent(evaluator_func)


def create_cot_agent() -> CoTAgent:
    """创建CoT代理"""
    return CoTAgent()


def create_hitl_agent(auto_mode=False) -> HITLAgent:
    """创建HITL代理"""
    return HITLAgent(auto_mode)


def create_supervisor_swarm() -> SupervisorSwarm:
    """创建监督者群体"""
    return SupervisorSwarm()


if __name__ == "__main__":
    print("## 测试 call_llm")
    prompt = "用几句话解释一下生命的意义是什么？"
    print(f"## 提示词: {prompt}")
    response = call_llm(prompt)
    print(f"## 响应: {response}")

    # print("## 测试 search_web")
    # query = "谁获得了2024年诺贝尔物理学奖？"
    # print(f"## 查询: {query}")
    # results = search_web_duckduckgo(query)
    # print(f"## 结果: {results}")

    print("## 测试 Memory 功能")
    memory = create_memory_system()
    memory.add_message("user", "你好")
    memory.add_message("assistant", "你好！有什么可以帮助你的吗？")
    print(f"## 记忆消息数: {len(memory.messages)}")

    print("## 测试 RAG 功能")
    rag = create_rag_system()
    rag.add_documents(["人工智能是计算机科学的一个分支，致力于创建能够执行通常需要人类智能的任务的系统。"])
    rag.build_index()
    results = rag.retrieve("什么是人工智能？")
    print(f"## RAG检索结果数: {len(results)}")

    print("## 测试 CoT 功能")
    cot_agent = create_cot_agent()
    result = cot_agent.solve("计算 15 + 27 的结果")
    print(f"## CoT结果: {result}")

    print("## 测试向量搜索功能")
    # 创建一些测试向量
    test_vectors = np.random.rand(10, 5)  # 10个5维向量
    query_vector = np.random.rand(5)  # 查询向量

    print("使用scikit-learn实现")
    nn = NearestNeighbors(n_neighbors=3, metric="cosine").fit(test_vectors)
    distances, indices = nn.kneighbors([query_vector])
    print(f"sklearn结果 - 距离: {distances[0]}, 索引: {indices[0]}")
