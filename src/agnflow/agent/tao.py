from typing import Literal, TypedDict
import yaml
import traceback

from agnflow.agent.llm import UserMsg, call_llm
from agnflow.core.node import Node
from agnflow.core.flow import Flow


class TAOState(TypedDict):
    query: str
    observations: list[str]
    thoughts: list[dict]
    current_thought_number: int
    current_action: str
    current_action_input: str


class ThinkNode(Node):
    """思考节点 - 分析当前情况并决定下一步行动

    TAO（思考-行动-观察）节点实现基于TAO模式的智能代理节点，包括思考决策、行动执行和结果观察功能。实现了AI代理的自主决策和迭代改进能力。
    """

    def exec(self, state) -> Literal['exit'] | Literal['action']:
        """准备阶段：准备思考所需的上下文"""
        query = state.get("query", "")
        observations = state.get("observations", [])
        thoughts = state.get("thoughts", [])
        current_thought_number = state.get("current_thought_number", 0)

        # 更新思考计数
        state["current_thought_number"] = current_thought_number + 1

        # 格式化之前的观察
        observations_text = "\n".join([f"Observation {i+1}: {obs}" for i, obs in enumerate(observations)])
        if not observations_text:
            observations_text = "没有观察到任何内容。"

        # 执行阶段：执行思考过程，决定下一步行动

        # 构建提示词
        prompt = f"""
        你是AI助手，需要根据用户的问题和之前的观察，思考下一步的行动。
        
        用户的问题: {query}
        
        之前的观察:
        {observations_text}
        
        请思考下一步的行动，并返回你的思考过程和决策，格式如下：
        ```yaml
        thinking: |
            <详细的思考过程>
        action: <行动名称, 例如 'search' 或 'answer'>
        action_input: <行动的输入参数>
        is_final: <如果这是最终答案, 设置为 true, 否则为 false>
        ```
        """

        # 调用LLM获取思考结果
        response = call_llm(UserMsg(prompt))

        # 解析YAML响应
        yaml_str = response.split("```yaml")[1].split("```")[0].strip()
        thought_data = yaml.safe_load(yaml_str)

        # 添加思考编号
        thought_data["thought_number"] = current_thought_number

        # 后处理阶段：保存思考结果并决定流程中的下一步
        # 保存思考结果
        if "thoughts" not in state:
            state["thoughts"] = []
        state["thoughts"].append(thought_data)

        # 保存行动信息
        state["current_action"] = thought_data["action"]
        state["current_action_input"] = thought_data["action_input"]

        # 如果是最终答案，结束流程
        if thought_data.get("is_final", False):
            state["final_answer"] = thought_data["action_input"]
            print(f"🎯 Final Answer: {thought_data['action_input']}")
            return "exit"

        # 否则继续执行行动
        print(f"🤔 思考 {thought_data['thought_number']}: 决定执行 {thought_data['action']}")
        return "action"


class ActionNode(Node):
    """行动节点 - 执行决定的行动"""

    def exec(self, state) -> Literal['observe']:
        # 准备阶段：准备执行行动
        action = state["current_action"]
        action_input = state["current_action_input"]

        # 执行阶段：执行行动并返回结果

        print(f"🚀 执行行动: {action}, 输入: {action_input}")

        # 根据行动类型执行不同操作
        if action == "search":
            # 模拟搜索操作
            result = self.search_web(action_input)
        elif action == "calculate":
            # 模拟计算操作
            result = self.calculate(action_input)
        elif action == "answer":
            # 直接返回答案
            result = action_input
        else:
            # 未知行动类型
            result = f"未知行动类型: {action}"

        # 后处理阶段：保存行动结果
        # 保存当前行动结果
        state["current_action_result"] = result
        print(f"✅ 行动完成, 结果获取")

        # 继续到观察节点
        return "observe"

    # 模拟工具函数
    def search_web(self, query):
        """模拟网络搜索"""
        # 这应该是实际的搜索逻辑
        return f"搜索结果: 关于 '{query}' 的信息..."

    def calculate(self, expression):
        """模拟计算操作"""
        # 这应该是实际的计算逻辑
        try:
            return f"计算结果: {eval(expression)}"
        except:
            return f"无法计算表达式: {expression}"


class ObserveNode(Node):
    """观察节点 - 分析行动结果并生成观察"""

    def exec(self, state) -> Literal['think']:
        # 准备阶段：准备观察数据
        action = state["current_action"]
        action_input = state["current_action_input"]
        action_result = state["current_action_result"]

        # 执行阶段：分析行动结果，生成观察

        # 构建提示词
        prompt = f"""
        你是观察者，需要分析行动结果并提供客观的观察。
        
        行动: {action}
        行动输入: {action_input}
        行动结果: {action_result}
        
        请提供一个简洁的观察结果。不要做出决定，只描述你看到的内容。
        """

        # 调用LLM获取观察结果
        observation = call_llm(UserMsg(prompt))

        print(f"👁️ 观察: {observation[:50]}...")

        # 后处理阶段：保存观察结果并决定下一步流程
        # 保存观察结果
        if "observations" not in state:
            state["observations"] = []
        state["observations"].append(observation)

        # 继续思考
        return "think"


class TAOFlow(Flow):
    def __init__(self, name: str = None):
        super().__init__(name)
        think = ThinkNode()
        action = ActionNode()
        observe = ObserveNode()
        self[think >> action >> observe]


if __name__ == "__main__":
    tao_flow = TAOFlow()
    state = TAOState(query="什么是智能体TAO")
    tao_flow.run(state)
