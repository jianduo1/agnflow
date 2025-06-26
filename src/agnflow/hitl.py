# import queue
# import time
# import threading
# from typing import Any, Callable, Dict, Optional, Union


# class HumanInTheLoopSystem:
#     """简易高效的人工介入循环系统"""

#     def __init__(
#         self, auto_process_func: Optional[Callable] = None, max_queue_size: int = 100, poll_interval: float = 0.5
#     ):
#         """
#         初始化HITL系统

#         参数:
#             auto_process_func: 自动处理函数，无法自动处理时进入人工环节
#             max_queue_size: 任务队列最大容量
#             poll_interval: 检查新任务的时间间隔(秒)
#         """
#         self.task_queue = queue.Queue(maxsize=max_queue_size)
#         self.auto_process_func = auto_process_func
#         self.poll_interval = poll_interval
#         self.running = False
#         self.thread = None
#         self.results = {}  # 存储任务结果

#     def start(self) -> None:
#         """启动HITL系统后台处理线程"""
#         if self.running:
#             print("系统已在运行中")
#             return

#         self.running = True
#         self.thread = threading.Thread(target=self._background_process, daemon=True)
#         self.thread.start()
#         print("Human-in-the-Loop系统已启动")

#     def stop(self) -> None:
#         """停止HITL系统"""
#         self.running = False
#         if self.thread:
#             self.thread.join(timeout=1.0)
#         print("Human-in-the-Loop系统已停止")

#     def add_task(self, task_id: str, task_data: Any, priority: int = 0) -> bool:
#         """
#         向系统添加新任务

#         参数:
#             task_id: 任务唯一标识
#             task_data: 任务数据
#             priority: 任务优先级(数值越小优先级越高)

#         返回:
#             添加成功与否
#         """
#         try:
#             # 包装任务数据，包含优先级和ID
#             self.task_queue.put((priority, task_id, task_data), block=False)
#             return True
#         except queue.Full:
#             print(f"任务队列已满，无法添加任务: {task_id}")
#             return False

#     def _background_process(self) -> None:
#         """后台处理线程主函数"""
#         while self.running:
#             self.process_task()
#             time.sleep(self.poll_interval)

#     def process_task(self) -> None:
#         """处理单个任务的主逻辑"""
#         try:
#             # 按优先级获取任务 (优先级数值越小越先处理)
#             priority, task_id, task_data = self.task_queue.get(block=True, timeout=self.poll_interval)

#             # 尝试自动处理
#             auto_result = self.process_task_automatically(task_id, task_data)

#             if auto_result is not None:
#                 # 自动处理成功
#                 self.results[task_id] = {"result": auto_result, "processed_by": "auto", "timestamp": time.time()}
#             else:
#                 # 需要人工处理
#                 human_result = self.get_human_feedback(task_id, task_data)
#                 self.results[task_id] = {"result": human_result, "processed_by": "human", "timestamp": time.time()}

#             self.task_queue.task_done()
#             print(f"任务 {task_id} 处理完成，结果: {self.results[task_id]['result']}")

#         except queue.Empty:
#             # 超时，无新任务
#             pass
#         except Exception as e:
#             print(f"处理任务时发生错误: {str(e)}")

#     def process_task_automatically(self, task_id: str, task_data: Any) -> Optional[Any]:
#         """
#         尝试自动处理任务

#         参数:
#             task_id: 任务ID
#             task_data: 任务数据

#         返回:
#             自动处理结果，若无法处理返回None
#         """
#         if self.auto_process_func:
#             try:
#                 result = self.auto_process_func(task_data)
#                 print(f"自动处理任务 {task_id} 成功")
#                 return result
#             except Exception as e:
#                 print(f"自动处理任务 {task_id} 失败: {str(e)}")
#         return None

#     def get_human_feedback(self, task_id: str, task_data: Any) -> Any:
#         """
#         获取人工对任务的反馈

#         参数:
#             task_id: 任务ID
#             task_data: 任务数据

#         返回:
#             人工反馈结果
#         """
#         print(f"\n===== 待处理任务: {task_id} =====")
#         print(f"任务数据: {task_data}")
#         print("请输入处理结果 (示例: 同意/拒绝 或 具体标注内容):")

#         # 这里可以扩展为更复杂的界面，如Web界面或GUI
#         # 简化版使用命令行输入
#         while True:
#             user_input = input(">>> ")
#             if user_input.strip():
#                 return user_input
#             print("输入不能为空，请重新输入")

#     def get_task_result(self, task_id: str) -> Optional[Dict]:
#         """
#         获取任务处理结果

#         参数:
#             task_id: 任务ID

#         返回:
#             任务结果字典，若任务未处理完成返回None
#         """
#         return self.results.get(task_id)

#     def get_all_results(self) -> Dict:
#         """获取所有已处理任务的结果"""
#         return self.results


# # 使用示例
# def simple_auto_processor(data: str) -> str:
#     """简单的自动处理函数示例"""
#     if "yes" in data.lower() or "同意" in data:
#         return "自动批准"
#     elif "no" in data.lower() or "拒绝" in data:
#         return "自动拒绝"
#     return None  # 无法自动处理


# def demo_human_in_the_loop():
#     """演示HITL系统的使用"""
#     # 创建HITL系统，传入自动处理函数
#     hitl = HumanInTheLoopSystem(auto_process_func=simple_auto_processor)

#     # 启动系统
#     hitl.start()

#     # 添加一些任务
#     hitl.add_task("task_1", "是否批准用户申请？")
#     hitl.add_task("task_2", "这张图片是否包含动物？")
#     hitl.add_task("task_3", "yes, 请批准这个请求")  # 可以自动处理
#     hitl.add_task("task_4", "no, 拒绝这个操作")  # 可以自动处理

#     print("已添加任务，等待处理...")

#     # 等待一段时间让任务处理
#     time.sleep(2)

#     # 检查任务结果
#     for task_id in ["task_1", "task_2", "task_3", "task_4"]:
#         result = hitl.get_task_result(task_id)
#         if result:
#             processed_by = "自动" if result["processed_by"] == "auto" else "人工"
#             print(f"任务 {task_id} 处理结果: {result['result']} (处理者: {processed_by})")
#         else:
#             print(f"任务 {task_id} 尚未处理完成")

#     # 停止系统
#     hitl.stop()


# if __name__ == "__main__":
#     demo_human_in_the_loop()


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
