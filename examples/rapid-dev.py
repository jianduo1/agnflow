"""
AgnFlow - Rapid Agent Development
"""

from typing import TypedDict
from agnflow import Node, Flow, Supervisor, Swarm

class State(TypedDict):
    data: str

# Define nodes
n1 = Node(exec=lambda state: "n2")
n2 = Node(exec=lambda state: "n3")
n3 = Node(exec=lambda state: "n5")
n4 = Node(exec=lambda state: "n5")
n5 = Node(exec=lambda state: "n6")
n6 = Node(exec=lambda state: print(state))
# Flow is a collection of nodes
flow = Flow()
# Supervisor n2 and supervisees(n3, n4) are interconnected
s1 = Supervisor()
# Full interconnection of swarm nodes(n5, n6)
s2 = Swarm()

# Build flow
flow[n1] >> s1[n2, n3, n4] >> s2[n5, n6]
# connections are the connections between nodes
print(flow.connections)
# hidden_connections are the connections between nodes and
# containers, or between containers themselves.
# They are not shown in the flowchart.
print(flow.hidden_connections)
# conntainer is the collection of nodes
print(flow.conntainer)
# Render mermaid, output mermaid script and saved path
print(flow.render_mermaid(saved_file="assets/output.png")[0])
# Run flow, start from n1
state: State = {"data": "hello"}
flow.run(state=state, entry_action="n1")

"""
AgnFlow - 快速开发智能体
"""

# from typing import TypedDict
# from agnflow import Node, Flow, Supervisor, Swarm

# class State(TypedDict):
#     data: str

# # 定义节点
# n1 = Node(exec=lambda state: "n2")
# n2 = Node(exec=lambda state: "n3")
# n3 = Node(exec=lambda state: "n5")
# n4 = Node(exec=lambda state: "n5")
# n5 = Node(exec=lambda state: "n6")
# n6 = Node(exec=lambda state: print(state))
# # Flow 是节点的集合
# flow = Flow()
# # Supervisor n2 以及被监督者(n3, n4)互连
# s1 = Supervisor()
# # Swarm 节点(n5, n6)全互连
# s2 = Swarm()

# # 构建流程
# flow[n1] >> s1[n2, n3, n4] >> s2[n5, n6]
# # connections 表示节点之间的连接关系
# print(flow.connections)
# # hidden_connections 表示节点与容器、或容器之间的连接（流程图中不显示）
# print(flow.hidden_connections)
# # conntainer 表示节点的集合
# print(flow.conntainer)
# # 渲染 mermaid，输出 mermaid 脚本和保存路径
# print(flow.render_mermaid(saved_file="assets/output.png")[0])
# # 运行流程, 从 n1 开始
# state: State = {"data": "hello"}
# flow.run(state=state, entry_action="n1")

# 代码截图链接
# https://carbon.now.sh/?bg=rgba%28171%2C+184%2C+195%2C+1%29&t=seti&wt=none&l=auto&width=602&ds=true&dsyoff=24px&dsblur=68px&wc=true&wa=false&pv=0px&ph=0px&ln=true&fl=1&fm=Hack&fs=14px&lh=133%25&si=false&es=2x&wm=false&code=from%2520typing%2520import%2520TypedDict%250Afrom%2520agnflow%2520import%2520Node%252C%2520Flow%252C%2520Supervisor%252C%2520Swarm%250A%250Aclass%2520State%28TypedDict%29%253A%250A%2520%2520%2520%2520data%253A%2520str%250A%250A%2523%2520%25E5%25AE%259A%25E4%25B9%2589%25E8%258A%2582%25E7%2582%25B9%250An1%2520%253D%2520Node%28exec%253Dlambda%2520state%253A%2520%2522n2%2522%29%250An2%2520%253D%2520Node%28exec%253Dlambda%2520state%253A%2520%2522n3%2522%29%250An3%2520%253D%2520Node%28exec%253Dlambda%2520state%253A%2520%2522n4%2522%29%250An4%2520%253D%2520Node%28exec%253Dlambda%2520state%253A%2520%2522n5%2522%29%250An5%2520%253D%2520Node%28exec%253Dlambda%2520state%253A%2520%2522n6%2522%29%250An6%2520%253D%2520Node%28exec%253Dlambda%2520state%253A%2520print%28state%29%29%250A%2523%2520Flow%2520%25E6%2598%25AF%25E8%258A%2582%25E7%2582%25B9%25E7%259A%2584%25E9%259B%2586%25E5%2590%2588%250Aflow%2520%253D%2520Flow%28%29%250A%2523%2520Supervisor%2520n2%2520%25E4%25BB%25A5%25E5%258F%258A%25E8%25A2%25AB%25E7%259B%2591%25E7%259D%25A3%25E8%2580%2585%28n3%252C%2520n4%29%25E4%25BA%2592%25E8%25BF%259E%250As1%2520%253D%2520Supervisor%28%29%250A%2523%2520Swarm%2520%25E8%258A%2582%25E7%2582%25B9%28n5%252C%2520n6%29%25E5%2585%25A8%25E4%25BA%2592%25E8%25BF%259E%250As2%2520%253D%2520Swarm%28%29%250A%250A%2523%2520%25E6%259E%2584%25E5%25BB%25BA%25E6%25B5%2581%25E7%25A8%258B%250Aflow%255Bn1%255D%2520%253E%253E%2520s1%255Bn2%252C%2520n3%252C%2520n4%255D%2520%253E%253E%2520s2%255Bn5%252C%2520n6%255D%250A%2523%2520connections%2520%25E8%25A1%25A8%25E7%25A4%25BA%25E8%258A%2582%25E7%2582%25B9%25E4%25B9%258B%25E9%2597%25B4%25E7%259A%2584%25E8%25BF%259E%25E6%258E%25A5%25E5%2585%25B3%25E7%25B3%25BB%250Aprint%28flow.connections%29%250A%2523%2520hidden_connections%2520%25E8%25A1%25A8%25E7%25A4%25BA%25E8%258A%2582%25E7%2582%25B9%25E4%25B8%258E%25E5%25AE%25B9%25E5%2599%25A8%25E3%2580%2581%25E6%2588%2596%25E5%25AE%25B9%25E5%2599%25A8%25E4%25B9%258B%25E9%2597%25B4%25E7%259A%2584%25E8%25BF%259E%25E6%258E%25A5%25EF%25BC%2588%25E6%25B5%2581%25E7%25A8%258B%25E5%259B%25BE%25E4%25B8%25AD%25E4%25B8%258D%25E6%2598%25BE%25E7%25A4%25BA%25EF%25BC%2589%250Aprint%28flow.hidden_connections%29%250A%2523%2520conntainer%2520%25E8%25A1%25A8%25E7%25A4%25BA%25E8%258A%2582%25E7%2582%25B9%25E7%259A%2584%25E9%259B%2586%25E5%2590%2588%250Aprint%28flow.conntainer%29%250A%2523%2520%25E6%25B8%25B2%25E6%259F%2593%2520mermaid%25EF%25BC%258C%25E8%25BE%2593%25E5%2587%25BA%2520mermaid%2520%25E8%2584%259A%25E6%259C%25AC%25E5%2592%258C%25E4%25BF%259D%25E5%25AD%2598%25E8%25B7%25AF%25E5%25BE%2584%250Aprint%28flow.render_mermaid%28saved_file%253D%2522assets%252Frapid-dev.png%2522%29%255B0%255D%29%250A%2523%2520%25E8%25BF%2590%25E8%25A1%258C%25E6%25B5%2581%25E7%25A8%258B%252C%2520%25E4%25BB%258E%2520n1%2520%25E5%25BC%2580%25E5%25A7%258B%250Astate%253A%2520State%2520%253D%2520%257B%2522data%2522%253A%2520%2522hello%2522%257D%250Aflow.run%28state%253Dstate%252C%2520entry_action%253D%2522n1%2522%29&tb=AgnFlow%2520-%2520%25E5%25BF%25AB%25E9%2580%259F%25E5%25BC%2580%25E5%258F%2591%25E6%2599%25BA%25E8%2583%25BD%25E4%25BD%2593
