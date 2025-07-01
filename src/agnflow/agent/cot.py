"""
思维链节点实现 - 实现结构化思维过程管理

本模块支持结构化计划管理、思维评估和渐进式问题解决。
"""

from typing import TypedDict
from textwrap import dedent, indent
import yaml

from agnflow.core.node import Node
from agnflow.core.flow import Flow
from agnflow.agent.llm import call_llm, UserMsg


status_map = {"Done": "✅", "Pending": "⏳", "Verification Needed": "❌"}


def format_plan(plan_items, indent_level=0):
    """
    格式化结构化计划用于打印显示
    Args:
        plan_items: 计划项目列表或字典
        indent_level: 缩进级别
    Returns:
        格式化后的计划字符串
    """
    indent = "  " * indent_level
    output = []

    if isinstance(plan_items, list):
        for item in plan_items:
            if isinstance(item, dict):
                status = item.get("status", "Unknown")
                desc = item.get("description", "No description")
                result = item.get("result", "")
                mark = item.get("mark", "")  # 用于验证等标记

                # checklist 风格
                line = f"{indent}- [{status_map[status]}] {desc}"
                if result:
                    line += f": {result}"
                if mark:
                    line += f" ({mark})"
                output.append(line)

                # 递归格式化子步骤（如果存在）
                sub_steps = item.get("sub_steps")
                if sub_steps:
                    output.append(format_plan(sub_steps, indent_level + 1))
            elif isinstance(item, str):  # 字符串项目的基本回退
                output.append(f"{indent}- {item}")
            else:  # 意外类型的回退
                output.append(f"{indent}- {str(item)}")

    elif isinstance(plan_items, str):  # 处理计划仅为错误字符串的情况
        output.append(f"{indent}{plan_items}")
    else:
        output.append(f"{indent}# 无效的计划格式: {type(plan_items)}")

    return "\n".join(output)


def format_plan_for_prompt(plan_items, indent_level=0):
    """
    为提示词格式化结构化计划（简化视图）
    Args:
        plan_items: 计划项目
        indent_level: 缩进级别
    Returns:
        简化格式的计划字符串
    """
    indent = "  " * indent_level
    output = []

    # 为提示词清晰度进行简化格式化
    if isinstance(plan_items, list):
        for item in plan_items:
            if isinstance(item, dict):
                status = item.get("status", "Unknown")
                desc = item.get("description", "No description")
                line = f"{indent}- [{status_map[status]}] {desc}"
                output.append(line)
                sub_steps = item.get("sub_steps")
                if sub_steps:
                    # 在提示词中指示嵌套而不完整递归显示
                    output.append(format_plan_for_prompt(sub_steps, indent_level + 1))
            else:  # 回退
                output.append(f"{indent}- {str(item)}")
    else:
        output.append(f"{indent}{str(plan_items)}")
    return "\n".join(output)


class CoTState(TypedDict):
    problem: str
    """问题"""
    thoughts: list[dict]
    """思考历史"""
    current_thought_number: int
    """当前思考步骤"""
    thoughts_text: str
    """思考历史文本"""
    last_plan_structure: list[dict]
    """最后计划结构"""


class COTNode(Node):
    """思维链节点 - ChainOfThought - 实现结构化思维过程管理

    链式思维步骤：

    1. 评估之前的思维步骤
    2. 执行计划中的待处理步骤
    3. 维护和更新结构化计划
    4. 处理错误和验证需求
    """

    def exec(self, state: CoTState) -> str:
        # 准备阶段：整理思维历史和计划状态
        problem = state.get("problem", "")
        thoughts = state.get("thoughts", [])
        current_thought_number = state.get("current_thought_number", 0) + 1
        state["current_thought_number"] = current_thought_number

        # 格式化之前的思维并提取最后的计划结构
        thoughts_text = ""
        last_plan_structure = None
        if thoughts:
            thoughts_text_list = []
            for i, thought in enumerate(thoughts):
                thought_block = f"思考 {thought.get('thought_number', i+1)}:\n"
                thinking = dedent(thought.get("current_thinking", "N/A")).strip()
                thought_block += f"  思考内容:\n{indent(thinking, '    ')}\n"

                plan_list = thought.get("planning", [])
                # 使用递归辅助函数进行显示格式化
                plan_str_formatted = format_plan(plan_list, indent_level=2)
                thought_block += f"  当前计划状态:\n{plan_str_formatted}"

                if i == len(thoughts) - 1:
                    last_plan_structure = plan_list  # 保持实际结构

                thoughts_text_list.append(thought_block)

            thoughts_text = "\n--------------------\n".join(thoughts_text_list)
        else:
            thoughts_text = "还没有任何思考"
            # 使用字典建议初始计划结构
            last_plan_structure = [
                {"description": "理解问题", "status": "Pending"},
                {"description": "制定一个高层次的计划", "status": "Pending"},
                {"description": "结论", "status": "Pending"},
            ]

        # 使用特定辅助函数为提示词上下文格式化最后的计划结构
        last_plan_text = format_plan_for_prompt(last_plan_structure) if last_plan_structure else "# 没有之前的计划"

        # 执行阶段：生成下一个思维步骤
        # --- 构建提示词 ---
        # 为字典结构更新的指令
        instruction_base = dedent(
            f"""
            你的任务是生成下一个思维步骤（编号为 {current_thought_number}）。

            请遵循以下要求：

            1.  **评估上一步思维：** 如果这不是第一次思考，请在 `current_thinking` 的开头对思维 {current_thought_number - 1} 进行简明评估。
                评估格式示例："对思维 {current_thought_number - 1} 的评估：[✅正确/⚠️有小问题/❌重大错误 - 说明理由]"。如发现错误，请优先处理。
            2.  **执行计划步骤：** 执行计划中第一个 `status: Pending` 的步骤，并在 `current_thinking` 中详细说明你的推理过程。
            3.  **维护和更新计划结构：** 生成最新的 `planning` 列表。每一项为字典，需包含：`description`（字符串）、`status`（"Pending"、"Done"、"Verification Needed"），可选 `result`（已完成时的简要总结）或 `mark`（需验证时的原因说明）。如有子步骤，使用 `sub_steps` 键，其值为同结构的字典列表。
            4.  **更新当前步骤状态：** 对已执行的步骤，将其 `status` 设为 "Done"，并补充 `result` 简要总结。如评估需验证，则将 `status` 设为 "Verification Needed"，并添加 `mark` 说明。
            5.  **细化复杂步骤：** 若某个 "Pending" 步骤较为复杂，请为其添加 `sub_steps`，将其细分为多个新的子步骤（均为 "Pending"）。父步骤在所有子步骤完成前保持 "Pending"。
            6.  **根据评估调整计划：** 如评估发现问题，请合理修改计划（如更改状态、添加修正步骤等）。
            7.  **推进至结论：** 确保计划最终包含形如 `{{'description': "Conclusion", 'status': "Pending"}}` 的结论步骤。
            8.  **终止条件：** 仅当执行 `description: "Conclusion"` 步骤时，将 `next_thought_needed` 设为 `false`，其余情况均为 `true`。
        """
        )

        # 上下文基本保持不变
        instruction_context = dedent(
            """
            **这是第一次思考：** 请创建一个初始计划，格式为字典列表（每项包含 description, status 键）。如有需要，可通过 `sub_steps` 键添加子步骤。然后，在 `current_thinking` 中执行第一个步骤，并给出更新后的计划（将第1步的 `status` 标记为 "Done"，并补充 `result` 简要总结）。
        """
            if not thoughts
            else f"""
                **上一步计划（简化视图）：**
                {last_plan_text}

                请以评估思维 {current_thought_number - 1} 开始 `current_thinking`。然后，执行第一个 `status: Pending` 的步骤。更新计划结构（字典列表），体现评估、执行和细化等变化。
            """
        )

        # 为字典结构更新的输出格式示例
        instruction_format = dedent(
            """
            仅将你的回复格式化为用 ```yaml ... ``` 包裹的 YAML 结构：
            ```yaml
            current_thinking: |
              [对思维 N 的评估：[评估结果] ...（如适用）]
              [当前步骤的思考内容...]
            planning:
              # 字典列表（键包括: description, status, 可选[result, mark, sub_steps]）
              - description: "步骤 1"
                status: "Done"
                result: "简要结果总结"
              - description: "步骤 2 复杂任务" # 现在被细分
                status: "Pending" # 父步骤保持 Pending
                sub_steps:
                  - description: "子任务 2a"
                    status: "Pending"
                  - description: "子任务 2b"
                    status: "Verification Needed"
                    mark: "思维 X 的结果可能有问题"
              - description: "步骤 3"
                status: "Pending"
              - description: "结论"
                status: "Pending"
            next_thought_needed: true # 仅在执行"结论"步骤时设为 false。
            ```
        """
        )

        # 组合提示词部分
        prompt = dedent(
            f"""
            你是一名严谨的 AI 助手，正通过结构化计划逐步解决复杂问题。
            你会批判性地评估前一步，必要时用子步骤细化计划，并合理处理错误。请严格使用指定的 YAML 字典结构输出计划。

            问题：{problem}

            之前的思考：
            {thoughts_text}
            --------------------
            {instruction_base}
            {instruction_context}
            {instruction_format}
        """
        )
        # --- 结束提示词构建 ---

        response = call_llm(UserMsg(prompt))

        # 简单 YAML 提取
        yaml_str = response.split("```yaml")[1].split("```")[0].strip()
        thought_data = yaml.safe_load(yaml_str)  # 可能抛出 YAMLError

        # --- 验证（使用 assert） ---
        assert thought_data is not None, "YAML 解析失败，结果为 None"
        assert "current_thinking" in thought_data, "LLM 响应缺少 'current_thinking'"
        assert "next_thought_needed" in thought_data, "LLM 响应缺少 'next_thought_needed'"
        assert "planning" in thought_data, "LLM 响应缺少 'planning'"
        assert isinstance(thought_data.get("planning"), list), "LLM 响应 'planning' 不是列表"
        # 可选：如果需要，添加列表项为字典的更深层验证
        # --- 结束验证 ---

        # 添加思维编号
        thought_data["thought_number"] = current_thought_number

        # 后处理阶段：更新思维历史并决定下一步
        # 将新思维添加到列表
        state.setdefault("thoughts", []).append(thought_data)

        # 使用更新的递归辅助函数提取计划用于打印
        plan_list = thought_data.get("planning", ["错误: Planning data missing."])
        plan_str_formatted = format_plan(plan_list, indent_level=1)

        thought_num = thought_data.get("thought_number", "N/A")
        current_thinking = thought_data.get("current_thinking", "错误: Missing thinking content.")
        dedented_thinking = dedent(current_thinking).strip()

        # 根据描述确定这是否是结论步骤
        is_conclusion = False
        if isinstance(plan_list, list):
            # 检查当前执行的步骤（可能是最后一个 'Done' 或如果评估失败则为当前的 'Pending'）是否为结论
            # 这个逻辑是近似的 - 可能需要根据 LLM 如何处理状态更新进行改进
            for item in reversed(plan_list):  # 首先检查最近的项目
                if isinstance(item, dict) and item.get("description") == "Conclusion":
                    # 如果结论已完成或待处理且我们正在结束，则认为是结论
                    if item.get("status") == "Done" or (
                        item.get("status") == "Pending" and not thought_data.get("next_thought_needed", True)
                    ):
                        is_conclusion = True
                        break
                # 简单检查，如果结论可能是子步骤，可能需要嵌套搜索

        # 使用 is_conclusion 标志或 next_thought_needed 标志进行终止
        if not thought_data.get("next_thought_needed", True):  # 主要终止信号
            state["solution"] = dedented_thinking  # 解决方案是最后步骤的思维内容
            print(f"\n思考 {thought_num} (结论):")
            print(f"{indent(dedented_thinking, '  ')}")
            print("\n最终计划状态:")
            print(indent(plan_str_formatted, "  "))
            print("\n=== 最终解决方案 ===")
            print(dedented_thinking)
            print("======================\n")
            return "exit"

        # 否则，继续链式思维
        print(f"\n思考 {thought_num}:")
        print(f"{indent(dedented_thinking, '  ')}")
        print("\n当前计划状态:")
        print(indent(plan_str_formatted, "  "))
        print("-" * 50)

        return self.name

class CoTFlow(Flow):
    def __init__(self, name: str = None):
        super().__init__(name)
        node = COTNode()
        self[node >> node]


if __name__ == "__main__":

    # cot_node = COTNode()
    # cot_flow = CoTFlow()
    # cot_flow[cot_node >> cot_node]
    # flow.run({"problem": "给出 1 + (2 * 3) + 4 每一步计算结果"})

    flow = CoTFlow()
    flow.run({"problem": "什么是智能体CoT"}, max_steps=200)
