from agnflow.core import Node, Flow
from agnflow.agent.llm import call_llm

class ChatNode(Node):

    def exec(self, state):
        # 初始化
        if "messages" not in state:
            state["messages"] = []
            print("🤖 欢迎来到聊天！输入 'exit' 结束对话。")
        messages = state["messages"]

        # 用户输入
        user_input = input("\n👤 你: ")
        if user_input.lower() == 'exit':
            return None
        messages.append({"role": "user", "content": user_input})

        # 调用LLM
        response = call_llm(messages)
        if response is None:
            print("\n👋 再见！")
            return None 

        # 输出结果
        print(f"\n🤖 助手: {response}")
        messages.append({"role": "assistant", "content": response})

        return "chat_node"


if __name__ == "__main__":
    chat_node = ChatNode()
    flow = Flow()
    flow[chat_node >> chat_node]

    state = {}
    flow.run(state)
