def human_in_the_loop(prompt, input_data=None, validation_func=None, max_attempts=3, auto_approve=False):
    """
    Human-in-the-Loop 交互函数

    参数:
        prompt (str): 展示给人类的提示信息或问题
        input_data (any): 需要人类验证或处理的输入数据
        validation_func (function): 用于验证人类输入的验证函数
        max_attempts (int): 最大尝试次数
        auto_approve (bool): 是否在开发模式下自动批准

    返回:
        tuple: (human_input, is_approved)
    """

    # 开发模式下可以设置自动批准
    if auto_approve:
        print(f"[AUTO-APPROVE] {prompt}\n输入数据: {input_data}")
        return input_data, True

    attempts = 0

    while attempts < max_attempts:
        attempts += 1

        # 展示信息和输入数据
        print(f"\n[Human Review] {prompt}")
        if input_data is not None:
            print(f"需要人工审核的输入数据:\n{input_data}")

        # 获取人类输入
        human_input = input("请提供您的输入 (或 'approve'/'reject'): ").strip().lower()

        # 处理简单批准/拒绝
        if human_input == "approve":
            return input_data, True
        elif human_input == "reject":
            return input_data, False

        # 如果有验证函数，验证人类输入
        if validation_func:
            try:
                is_valid = validation_func(human_input)
                if is_valid:
                    return human_input, True
                else:
                    print("输入无效。请重新输入。")
            except Exception as e:
                print(f"验证错误: {e}. 请重新输入。")
        else:
            # 没有验证函数时，直接返回人类输入
            return human_input, True

    print(f"达到最大尝试次数 ({max_attempts})。操作被拒绝。")
    return None, False


# 示例验证函数
def validate_age_input(age_str):
    """验证年龄输入是否有效"""
    try:
        age = int(age_str)
        if 0 < age < 120:
            return True
        return False
    except ValueError:
        return False


# 使用示例
if __name__ == "__main__":
    # 示例1: 简单批准/拒绝
    print("\n--- 示例1: 简单批准/拒绝 ---")
    data = {"name": "Alice", "age": 30}
    _, approved = human_in_the_loop("请审核此用户数据", data)
    print(f"Approved: {approved}")

    # 示例2: 带验证的输入
    print("\n--- 示例2: 带验证的输入 ---")
    age_input, approved = human_in_the_loop("请输入用户年龄", validation_func=validate_age_input)
    print(f"年龄: {age_input}, 批准: {approved}")

    # 示例3: 自动批准模式 (用于测试)
    print("\n--- 示例3: 自动批准模式 ---")
    result, approved = human_in_the_loop("这需要人工输入", input_data="测试数据", auto_approve=True)
    print(f"结果: {result}, 批准: {approved}")
