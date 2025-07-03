from inspect import signature
from typing import Annotated, Literal, TypedDict
from textwrap import dedent, indent
import json
import re

from agnflow.agent.llm import UserMsg, call_llm
from agnflow.core.node import Node
from agnflow.core.flow import Flow


def pprint(data, parse_func=None):
    """打印数据"""
    if parse_func and callable(parse_func):
        data = parse_func(data)
    elif not isinstance(data, str):
        data = json.dumps(data, indent=4, ensure_ascii=False)

    print(indent(text=data, prefix=" " * 8))


class TAOState(TypedDict):
    """TAO状态"""

    query: str  # 用户的问题
    current_thought_number: int  # 当前思考编号
    thoughts: list[dict]  # 思考
    action: str  # 动作名称
    action_input: str  # 动作输入
    action_result: str  # 动作结果
    observations: list[str]  # 观察，来自动作结果
    final_answer: str  # 最终答案


# ===================== 通用节点 =====================
class ThinkNode(Node[TAOState]):
    """通用思考节点"""

    def think(self, state: TAOState, action_prompt: str, extra_rule_prompt: str = "") -> dict:
        # 更新思考计数
        current_thought_number = state.get("current_thought_number", 0)
        state["current_thought_number"] = current_thought_number + 1
        # 格式化之前的观察
        observations = state.get("observations", [])
        observations_text = (
            "\n".join([f"第{i+1}次 {obs}" for i, obs in enumerate(observations)]) or "没有观察到任何内容。"
        )
        # 构建提示词
        prompt = f"""
你是AI助手，需要根据用户的问题和之前的观察，思考下一步的动作。

用户的问题: {state.get('query', '')}

之前的观察:
{observations_text}（最近一次）

可选动作：
{action_prompt}

额外规则：
{extra_rule_prompt}

请思考下一步的动作，并返回你的思考过程和决策，格式如下：
```yaml
thinking: |
    <详细的思考过程>
action: <动作名称，检查动作名称是否在上述可选动作名称列表中>
action_input: <动作的输入参数，类型为字典，默认为空字典，检查动作输入参数是否符合上述动作描述>
is_final: <如果这是最终答案, 设置为 true, 否则为 false>
```
"""
        # 打印提示词，便于调试
        pprint(prompt)
        # 调用LLM获取思考结果，添加思考编号
        thought_data = call_llm(UserMsg(prompt), output_format="yaml")
        # 标准化action字段，兼容多种LLM输出
        action = thought_data.get("action", "")
        # 如果是列表，取第一个
        if isinstance(action, list):
            action = action[0] if action else ""
        # 尝试从'动作 N xxx'或'def xxx'中提取动作名
        if isinstance(action, str):
            # 1. 匹配def xxx
            m = re.search(r"def ([a-zA-Z0-9_]+)", action)
            if m:
                action = m.group(1)
            else:
                # 2. 匹配'动作 N xxx'，取最后的xxx
                m2 = re.search(r"动作 \d+ ([^\s]+)", action)
                if m2:
                    action = m2.group(1)
                else:
                    # 3. 如果是'猜测数字'等，直接用
                    action = action.strip()
        thought_data["action"] = action
        # 打印思考结果，便于调试
        pprint(thought_data)
        thought_data["thought_number"] = state.get("current_thought_number", 0)
        # 保存思考结果，动作信息
        state.setdefault("thoughts", []).append(thought_data)
        state["action"] = thought_data["action"]
        state["action_input"] = thought_data["action_input"]
        # 如果是最终答案，结束流程
        if thought_data.get("is_final", False):
            state["final_answer"] = thought_data["action_input"]
            print(f"🎯 最终答案: {thought_data['action_input']}")
            return {"result": "exit"}
        # 否则继续执行动作
        print(f"🤔 思考 {thought_data['thought_number']}: 决定执行 {thought_data['action']}")
        pprint(state)
        return {"result": "action-node"}

    def exec(self, state: TAOState) -> Literal["exit"] | Literal["action-node"]:
        self.think(state, ActionNode.get_actions_prompt(), "")


class ActionNode(Node[TAOState]):
    """通用动作节点"""

    @classmethod
    def get_actions_prompt(cls) -> str:
        propmt = ""
        i = 0
        for action, func in cls.__dict__.items():
            if action.startswith("_") or action in ["exec", "get_actions_prompt", "action"]:
                continue
            if callable(func):
                i += 1
                params: str = str(signature(func)).replace("self, ", "").replace("Annotated", "A")
                propmt += f"{i}. {action}{params} 描述：{func.__doc__}\n"
        return propmt

    def action(self, state: TAOState):
        action = state["action"]
        action_input = state["action_input"]
        print(f"🚀 执行动作: {action}, 输入: {action_input}")
        if hasattr(self, action):
            func = getattr(self, action)
            if callable(func):
                try:
                    result = func(**action_input) if isinstance(action_input, dict) else func(action_input)
                except Exception as e:
                    result = f"动作执行异常: {e}"
            else:
                result = f"动作 {action} 不是可调用方法"
        else:
            result = f"未知动作类型: {action}"
        state["action_result"] = result
        print(f"✅ 动作完成, 结果获取: {result}")
        return {"result": "observe-node"}

    def exec(self, state: TAOState) -> Literal["observe-node"]:
        self.action(state)

    # 示例工具函数
    def search_web(self, query: Annotated[str, "搜索网络"]):
        """模拟网络搜索"""
        return f"搜索结果: 关于 '{query}' 的信息..."

    def calculate(self, expression: Annotated[str, "计算表达式"]):
        """模拟计算操作"""
        try:
            return f"计算结果: {eval(expression)}"
        except:
            return f"无法计算表达式: {expression}"

    def answer(self, answer: Annotated[str, "回答问题"]):
        """直接返回答案"""
        return str(answer)


class ObserveNode(Node[TAOState]):
    """通用观察节点"""

    def observe(self, state: TAOState, extra_rule_prompt: str = ""):
        prompt = f"""
你是观察者，需要分析动作结果并提供客观的观察。

动作: {state['action']}
动作输入: {state['action_input']}
动作结果: {state['action_result']}

额外规则：
{extra_rule_prompt}

请提供一个简洁的观察结果。不要做出决定，只描述你看到的内容。
"""
        observation = call_llm(UserMsg(prompt))
        print(f"👁️ 观察: {observation[:50]}...")
        state.setdefault("observations", []).append(observation)
        return {"result": "think-node"}

    def exec(self, state: TAOState) -> Literal["think-node"]:
        self.observe(state)


# ===================== 通用流程 =====================
class TAOFlow(Flow[TAOState]):
    def __init__(self, name: str = None):
        super().__init__(name=name)
        self.think_node = ThinkNode(name="think-node")
        self.action_node = ActionNode(name="action-node")
        self.observe_node = ObserveNode(name="observe-node")
        self[self.think_node >> self.action_node >> self.observe_node >> self.think_node]


# ===================== 猜数字游戏重构 =====================
class GuessNumberState(TAOState):
    min_value: int  # 当前最小值
    max_value: int  # 当前最大值
    target_number: int


class GuessNumberThinkNode(ThinkNode):
    def exec(self, state: GuessNumberState) -> Literal["exit"] | Literal["action-node"]:
        extra_rule = """猜数字游戏策略：
- 如果观察显示"太大了"，猜测一个更小的数字
- 如果观察显示"太小了"，猜测一个更大的数字
- 如果观察显示"猜对了"，游戏结束
- 使用二分查找策略：从中间开始，根据反馈调整范围
- 必须提供具体的数字，不能是描述性文字
- 假设数字范围是1-100，第一次猜测50
- 如果50太大，下次猜测25;如果50太小，下次猜测75
- 根据反馈继续二分查找
"""
        result = self.think(state, GuessNumberActionNode.get_actions_prompt(), extra_rule)
        return result["result"]


class GuessNumberActionNode(ActionNode):
    def exec(self, state: GuessNumberState) -> Literal["observe-node"]:
        return self.action(state)["result"]

    def guess(self, guess: Annotated[int, "猜测的数字"]):
        """猜测数字"""
        return guess

    def action(self, state: GuessNumberState):
        action = state["action"]
        action_input = state["action_input"]
        target = state["target_number"]
        print(f"🚀 执行动作: {action}, 输入: {action_input}")
        if action == "guess":
            if isinstance(action_input, dict) and "guess" in action_input:
                guess = action_input["guess"]
            else:
                state["action_result"] = "请提供猜测的数字"
                return {"result": "observe-node"}
            try:
                guess = int(guess)
            except (ValueError, TypeError):
                state["action_result"] = f"无效的数字: {guess}"
                return {"result": "observe-node"}
            if guess < target:
                state["action_result"] = f"太小了: {guess}"
            elif guess > target:
                state["action_result"] = f"太大了: {guess}"
            else:
                state["action_result"] = f"猜对了: {guess}"
        else:
            state["action_result"] = f"未知动作类型: {action}"
        print(f"✅ 动作完成, 结果获取: {state['action_result']}")
        return {"result": "observe-node"}


class GuessNumberObserveNode(ObserveNode):
    def exec(self, state: GuessNumberState) -> Literal["think-node"]:
        # 解析上一次动作结果
        last_result = state["action_result"]
        # 尝试解析上次猜测的数字
        last_guess = None
        if ":" in str(last_result):
            try:
                last_guess = int(str(last_result).split(":")[-1].strip())
            except Exception:
                last_guess = None
        # 初始化区间
        min_value = state.get("min_value", 1)
        max_value = state.get("max_value", 100)
        # 根据反馈调整区间
        if "太大了" in last_result and last_guess is not None:
            max_value = last_guess - 1
        elif "太小了" in last_result and last_guess is not None:
            min_value = last_guess + 1
        # 写回state
        state["min_value"] = min_value
        state["max_value"] = max_value
        # 生成观察内容
        obs = f"{last_result}，当前可猜区间：min={min_value}, max={max_value}"
        state.setdefault("observations", []).append(obs)
        return "think-node"


class GuessNumberFlow(TAOFlow):
    def __init__(self, target_number: int):
        self.name = "guess-number"
        self.think_node = GuessNumberThinkNode(name="think-node")
        self.action_node = GuessNumberActionNode(name="action-node")
        self.observe_node = GuessNumberObserveNode(name="observe-node")
        self[self.think_node >> self.action_node >> self.observe_node >> self.think_node]
        self.target_number = target_number


if __name__ == "__main__":
    flow = GuessNumberFlow(target_number=10)
    state = GuessNumberState(query="猜数字游戏", target_number=10, min_value=1, max_value=100)
    flow.run(state, max_steps=20)
