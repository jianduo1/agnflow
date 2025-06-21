"""
agnflow 用法示例
"""

from typing import TypedDict
import asyncio
from agnflow import Node, Flow


# ✨一、状态定义（使用TypedDict）

class State(TypedDict):
    data: str


state: State = {"data": "test"}


# ✨二、定义工作流节点

# 节点函数入参：根据变量名，自动从state中获取参数并且注入，默认为注入整个state
# 节点函数返回值：返回 (action, state) ，action用于导航到下一个节点，state 用于更新状态

# 方法1：使用类继承Node
class A(Node):
    def exec(self, data):
        print(f"A exec {data}")
        import random

        a = random.choices(["c", "b"], weights=[0.7, 0.3])
        return a

    async def aexec(self, data):
        print(f"A exec {data}")
        import random

        a = random.choices(["c", "b"], weights=[0.7, 0.3])
        return a


class B(Node):
    def exec(self, state):
        print(f"B exec {state}")

    async def aexec(self, state):
        print(f"B exec {state}")


class C(Node):
    def exec(self, state):
        print(f"C exec {state}")
        return "a", {"data": "test:C"}

    async def aexec(self, state):
        print(f"C exec {state}")
        return "a", {"data": "test:C"}


# 方法2：使用函数和Node的exec和aexec参数
def d1_exec(data):
    return "a", {"data": "test:d1"}


async def d1_aexec(data):
    return "a"  # 返回 action，用于导航到下一个节点


def d2_exec(state): ...
async def d2_aexec(state):
    return "a", {"data": "test:d2"}


a = A("a")
b = B("b")
c = C("c")
b2 = C("b2")
flow3 = Flow(b2, name="flow3")
d1 = Node("d1", exec=d1_exec, aexec=d1_aexec)
d2 = Node("d2", exec=d2_exec, aexec=d2_aexec)

# ✨三、连接工作流节点（a指向b和c，c指向a）

# 方法1：正向
# a >> "b" >> b >> "c" >> c

# 方法2：反向
# c << "c" << b << "b" << a

# 方法3：循环多分支
a >> {"b": b >> {"b2": flow3}, "c": c >> {"a": a}}

# ✨五、连接主工作流节点（d1指向子工作流，子工作流指向d2）

flow = Flow(a, name="flow")
d1 >> flow >> d2
flow2 = Flow(d1, name="flow2")

if __name__ == "__main__":
    # ✨六、同步执行工作流
    flow2.run(state)

    # ✨七、异步执行工作流
    asyncio.run(flow2.arun(state))

    # ✨八、绘制流程图
    print(flow2.render_dot(saved_file="./assets/flow_dot.png"))
    print(flow2.render_mermaid(saved_file="./assets/flow_mermaid.png"))
