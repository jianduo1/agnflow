"""
混合注入实际应用示例
展示在实际工作流中如何使用混合注入功能
"""

import asyncio
import time
from agnflow import Node, Flow


def user_validation(user_id, state):
    """用户验证节点 - 混合注入示例"""
    print(f"验证用户ID: {user_id}")
    print(f"当前状态: {state}")

    # 可以同时访问具体参数和完整状态
    if user_id in state.get("valid_users", []):
        return "process_node", {"user_validated": True, "validation_time": time.time()}
    else:
        return "error_node", {"user_validated": False, "error": "用户不存在"}


def process_request(request_data, state):
    """请求处理节点 - 混合注入示例"""
    print(f"处理请求数据: {request_data}")
    print(f"用户验证状态: {state.get('user_validated')}")

    # 根据验证状态处理请求
    if state.get("user_validated"):
        processed_data = f"已处理: {request_data}"
        return "success", {"processed_data": processed_data, "process_time": time.time()}
    else:
        return "error", {"error": "用户未验证"}


async def async_data_fetch(user_id, state):
    """异步数据获取节点 - 混合注入示例"""
    print(f"异步获取用户 {user_id} 的数据")
    print(f"当前处理状态: {state}")

    # 模拟异步操作
    await asyncio.sleep(0.1)

    # 根据用户ID获取数据
    user_data = {"user_id": user_id, "profile": {"name": f"用户{user_id}", "level": "VIP"}, "fetch_time": time.time()}

    return "data_ready", {"user_data": user_data}


def generate_response(state):
    """响应生成节点 - 混合注入示例"""
    user_data = state.get("user_data")
    processed_data = state.get("processed_data")

    print(f"生成响应，用户数据: {user_data}")
    print(f"处理后的数据: {processed_data}")
    print(f"完整状态: {state}")

    # 组合所有信息生成最终响应
    response = {"user": user_data, "result": processed_data, "timestamp": time.time(), "status": "success"}

    return {"final_response": response}


def error_handler(error_msg, state):
    """错误处理节点 - 混合注入示例"""
    print(f"处理错误: {error_msg}")
    print(f"错误时的状态: {state}")

    return {"error_response": {"error": error_msg, "timestamp": time.time(), "status": "error"}}


def create_mixed_injection_workflow():
    """创建使用混合注入的工作流"""

    # 创建节点
    validation_node = Node("validation", exec=user_validation)
    process_node = Node("process", exec=process_request)
    fetch_node = Node("fetch", aexec=async_data_fetch)
    response_node = Node("response", exec=generate_response)
    error_node = Node("error", exec=error_handler)

    # 连接工作流
    validation_node >> [process_node >> fetch_node >> response_node, error_node]

    return Flow(validation_node, name="mixed_injection_workflow")


def run_sync_example():
    """运行同步示例"""
    print("=== 同步混合注入示例 ===")

    flow = create_mixed_injection_workflow()

    # 测试成功流程
    print("\n1. 测试成功流程:")
    initial_state = {"user_id": "123", "request_data": "Hello World", "valid_users": ["123", "456", "789"]}

    result = flow.run(initial_state)
    print(f"工作流结果: {result}")

    # 测试失败流程
    print("\n2. 测试失败流程:")
    initial_state = {"user_id": "999", "request_data": "Hello World", "valid_users": ["123", "456", "789"]}

    result = flow.run(initial_state)
    print(f"工作流结果: {result}")


async def run_async_example():
    """运行异步示例"""
    print("\n=== 异步混合注入示例 ===")

    flow = create_mixed_injection_workflow()

    # 测试异步流程
    print("\n1. 测试异步流程:")
    initial_state = {"user_id": "456", "request_data": "Async Hello", "valid_users": ["123", "456", "789"]}

    result = await flow.arun(initial_state)
    print(f"异步工作流结果: {result}")


def demonstrate_parameter_access():
    """演示参数访问的灵活性"""
    print("\n=== 参数访问灵活性演示 ===")

    def flexible_node(user_id, request_data, state):
        """展示灵活的参数访问"""
        print(f"直接访问 user_id: {user_id}")
        print(f"直接访问 request_data: {request_data}")
        print(f"通过state访问其他字段: {state.get('extra_info')}")
        print(f"完整状态: {state}")

        return {"demonstrated": True}

    node = Node("flexible", exec=flexible_node)
    flow = Flow(node, name="flexible_demo")

    initial_state = {"user_id": "123", "request_data": "test", "extra_info": "这是额外信息"}

    flow.run(initial_state)


if __name__ == "__main__":
    # 运行同步示例
    run_sync_example()

    # 运行异步示例
    asyncio.run(run_async_example())

    # 演示参数访问灵活性
    demonstrate_parameter_access()

    print("\n✅ 混合注入示例完成！")
    print("\n关键特性总结：")
    print("1. 可以同时获得具体参数和完整状态")
    print("2. 支持同步和异步函数")
    print("3. 支持分支和错误处理")
    print("4. 提供灵活的节点函数设计")
