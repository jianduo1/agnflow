from zhipuai import ZhipuAI
from dotenv import load_dotenv
import os
import base64

load_dotenv()

# 读取本地图片并编码为 base64
image_path = "/Users/mac/Pictures/zzx.png"
with open(image_path, "rb") as img_file:
    img_base64 = base64.b64encode(img_file.read()).decode('utf-8')
image_data_url = f"data:image/png;base64,{img_base64}"

client = ZhipuAI(api_key=os.getenv("API_KEY")) 
question = "他的名字叫什么"
response = client.chat.completions.create(
    model="glm-4.1v-thinking-flashx",
    messages=[
        {
            "role": "user",
            "content": [
                {"type": "text", "text": question},
                {
                    "type": "image_url",
                    "image_url": {"url": image_data_url},
                },
            ],
        }
    ],
)
print(question)
print(response.choices[0].message.content)
