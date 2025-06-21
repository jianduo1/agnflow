"""

### TODO 清单

- [ ] llm
- [ ] memory
- [ ] rag
- [ ] mcp tool
- [ ] ReAct(reasoning + action) 
- [ ] TAO(thought + action + observation)
- [ ] ToT(Chain of Thought) 
- [ ] CoT(Chain of Thought)
- [ ] hitl(human in the loop)
- [ ] supervisor swarm

"""

from typing import Literal
import os
import requests
from openai import OpenAI
from duckduckgo_search import DDGS
from dotenv import load_dotenv
import numpy as np

load_dotenv()


def call_llm(user_prompt, system_prompt=None, model="glm-4-flashx-250414", output_format: Literal["yaml", "json", "text"]="text"):
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    messages = [{"role": "user", "content": user_prompt}]
    if system_prompt:
        messages.insert(0, {"role": "system", "content": system_prompt})
    completion = client.chat.completions.create(model=model, messages=messages)
    res = completion.choices[0].message.content
    if output_format == "text":
        return res
    if output_format == "yaml":
        res = res.strip().removeprefix("```yaml").removesuffix("```").strip()
        return yaml.safe_load(res)
    elif output_format == "json":
        res = res.strip().removeprefix("```json").removesuffix("```").strip()
        return json.loads(res)
    raise ValueError(f"不支持的输出格式: {output_format}")


def search_web_duckduckgo(query):
    results = DDGS().text(query, max_results=5)
    # Convert results to a string
    results_str = "\n\n".join([f"Title: {r['title']}\nURL: {r['href']}\nSnippet: {r['body']}" for r in results])
    return results_str


def search_web_brave(query):

    url = f"https://api.search.brave.com/res/v1/web/search?q={query}"
    api_key = os.getenv("BRAVE_SEARCH_API_KEY")

    headers = {"accept": "application/json", "Accept-Encoding": "gzip", "x-subscription-token": api_key}

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        results = data['web']['results']
        results_str = "\n\n".join([f"Title: {r['title']}\nURL: {r['url']}\nDescription: {r['description']}" for r in results])
        return results_str
    else:
        print(f"请求失败，状态码: {response.status_code}")


def get_embedding(text):
    client = OpenAI(base_url=os.getenv("EMBEDDING_BASE_URL"), api_key=os.getenv("EMBEDDING_API_KEY"))

    response = client.embeddings.create(model=os.getenv("EMBEDDING_MODEL_NAME"), input=text)

    # 从响应中提取 embedding 向量
    embedding = response.data[0].embedding

    # 转换为 numpy array 用于一致性
    return np.array(embedding, dtype=np.float32)


def get_similarity(text1, text2):
    emb1 = get_embedding(text1)
    emb2 = get_embedding(text2)
    return np.dot(emb1, emb2)


if __name__ == "__main__":
    print("## 测试 call_llm")
    prompt = "用几句话解释一下生命的意义是什么？"
    print(f"## 提示词: {prompt}")
    response = call_llm(prompt)
    print(f"## 响应: {response}")

    print("## 测试 search_web")
    query = "谁获得了2024年诺贝尔物理学奖？"
    print(f"## 查询: {query}")
    results = search_web_duckduckgo(query)
    print(f"## 结果: {results}")
