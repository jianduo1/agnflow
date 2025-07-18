from agnflow.chatbot.server import Server
from agent_nodes import VisionNode, WritingNode, ImageNode, VideoNode


if __name__ == "__main__":
    # 创建VisionNode实例
    vision_node = VisionNode()
    writing_node = WritingNode()
    image_node = ImageNode()
    video_node = VideoNode()

    # 创建Server实例，并传递VisionNode实例
    server = Server(agent_nodes=[vision_node, writing_node, image_node, video_node])

    # 运行Server
    server.run(port=8000)
