from typing import Any, Callable, Optional, Tuple, Union

def human_in_the_loop(
    prompt: str,
    input_data: Any = None,
    validation_func: Optional[Callable[[str], Union[bool, Tuple[Any, bool]]]] = None,
    max_attempts: int = 3,
    auto_approve: bool = False,
) -> Tuple[Any, bool]:
    """Human-in-the-Loop 交互函数
    
    参数:
        prompt: 提示信息
        input_data: 输入数据
        validation_func: 验证函数
        max_attempts: 最大尝试次数
        auto_approve: 自动批准
    返回:
        result: 输入数据
        approved: 是否批准
    """
    if auto_approve:
        print(f"[AUTO-APPROVE] {prompt}\n输入数据: {input_data}")
        return input_data, True

    attempts = 0
    try:
        while attempts < max_attempts:
            attempts += 1
            print(f"\n[Human Review] {prompt}")
            if input_data is not None:
                print(f"需要人工审核的输入数据:\n{input_data}")
            if max_attempts - attempts == 0:
                print("⚠️ 这是最后一次输入机会，请仔细确认！")
            raw_input_str = input("请提供您的输入 (或 'approve'/'reject'): ").strip()
            lower_input = raw_input_str.lower()
            if lower_input == "approve":
                return input_data, True
            elif lower_input == "reject":
                return input_data, False
            if validation_func:
                try:
                    result = validation_func(raw_input_str)
                    if isinstance(result, tuple):
                        value, is_valid = result
                    else:
                        value, is_valid = raw_input_str, result
                    if is_valid:
                        return value, True
                    else:
                        print("输入无效。请重新输入。")
                except Exception as e:
                    print(f"验证错误: {e}. 请重新输入。")
            else:
                return raw_input_str, True
        print(f"达到最大尝试次数 ({max_attempts})。操作被拒绝。")
        return None, False
    except KeyboardInterrupt:
        print("\n操作被用户中断。已退出审核流程。")
        return None, False

hitl = human_in_the_loop

if __name__ == "__main__":
    # 示例1: 简单批准/拒绝
    data = {"name": "Alice", "age": 30}
    _, approved = human_in_the_loop("请审核此用户数据", data)
    print(f"Approved: {approved}")

    # 示例2: 带验证的输入
    def validate_age_input(age_str):
        """验证年龄输入是否有效，返回 (int, bool)"""
        try:
            age = int(age_str)
            if 0 < age < 120:
                return age, True
            return age, False
        except ValueError:
            return age_str, False
    age_input, approved = human_in_the_loop("请输入用户年龄", validation_func=validate_age_input)
    print(f"年龄: {age_input}, 批准: {approved}")

    # 示例3: 自动批准模式 (用于测试)
    result, approved = human_in_the_loop("这需要人工输入", input_data="测试数据", auto_approve=True)
    print(f"结果: {result}, 批准: {approved}")
