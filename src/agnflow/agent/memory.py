"""
记忆：
- 短期记忆（对话上下文、工具信息等，工程上用缓存、数据库实现）
- 长期记忆（可存储长时间信息，工程上用向量数据库实现）。
"""
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from typing import List
from collections import OrderedDict
import time


class ShortTermMemory(OrderedDict):
    def __init__(self, capacity=100, ttl=60):  # capacity最大容量，ttl存活时间（秒）
        self.memory = OrderedDict()  # 有序字典保持时序
        self.capacity = capacity
        self.ttl = ttl

    def add(self, key, value):
        # 移除过期数据
        self._remove_expired()
        # 保持容量限制（LRU策略）
        if len(self.memory) >= self.capacity:
            self.memory.popitem(last=False)  # 移除最早添加的
        self.memory[key] = (value, time.time())  # 存储值和时间戳

    def get(self, key):
        self._remove_expired()
        return self.memory.get(key, (None, None))[0]

    def _remove_expired(self):
        current_time = time.time()
        to_remove = [k for k, (v, ts) in self.memory.items() if current_time - ts > self.ttl]
        for k in to_remove:
            del self.memory[k]

    def get_all(self):
        self._remove_expired()
        return [v for v, _ in self.memory.values()]


class ShortTermMemory:
    """一个简单的基于字典的短期记忆实现。"""

    def __init__(self):
        self._memory = {}

    def add(self, key: str, value):
        """向短期记忆中添加或更新一个键值对。"""
        self._memory[key] = value

    def get(self, key: str):
        """从短期记忆中检索一个值。"""
        return self._memory.get(key)

    def delete(self, key: str):
        """从短期记忆中删除一个键。"""
        if key in self._memory:
            del self._memory[key]

    def clear(self):
        """清空所有短期记忆。"""
        self._memory.clear()


class LongTermMemory:
    """
    支持多种嵌入方式的长期记忆：
    - embedding_type: 'auto'（优先AI，缺依赖降级），'ai'（强制AI），'tfidf'，'keyword'
    """
    def __init__(self, embedding_type: str = 'auto', model_name='all-MiniLM-L6-v2'):
        self.embedding_type = embedding_type
        self.documents: List[str] = []
        self._embeddings = None
        self.model = None
        self.vectorizer = None
        self._mode = None  # 实际使用的模式
        self._init_embedding(model_name)

    def _init_embedding(self, model_name):
        # 优先AI嵌入
        if self.embedding_type in ('auto', 'ai'):
            try:
                from sentence_transformers import SentenceTransformer
                import torch
                self.model = SentenceTransformer(model_name)
                self._mode = 'ai'
            except ImportError:
                if self.embedding_type == 'ai':
                    raise ImportError("未安装 sentence-transformers/torch，无法使用 AI 嵌入。请安装后重试。")
                # auto 模式下降级
        if self._mode is None and self.embedding_type in ('auto', 'tfidf'):
            try:
                from sklearn.feature_extraction.text import TfidfVectorizer
                self.vectorizer = TfidfVectorizer()
                self._mode = 'tfidf'
            except ImportError:
                if self.embedding_type == 'tfidf':
                    raise ImportError("未安装 scikit-learn，无法使用 TF-IDF 嵌入。请安装后重试。")
        if self._mode is None:
            self._mode = 'keyword'

    def add(self, document: str):
        """向长期记忆中添加一篇文档。"""
        if document in self.documents:
            return
        self.documents.append(document)
        if self._mode == 'ai':
            emb = self.model.encode([document])
            if self._embeddings is None:
                self._embeddings = emb
            else:
                self._embeddings = np.vstack([self._embeddings, emb])
        elif self._mode == 'tfidf':
            # 重新拟合所有文档
            self._embeddings = self.vectorizer.fit_transform(self.documents)
        # keyword 模式无需处理

    def search(self, query: str, top_k=5):
        """根据查询在长期记忆中搜索最相关的文档。"""
        if not self.documents:
            return []
        if self._mode == 'ai':
            query_emb = self.model.encode([query])
            sims = cosine_similarity(query_emb, self._embeddings)
            top_k_indices = np.argsort(sims[0])[-top_k:][::-1]
            return [self.documents[i] for i in top_k_indices]
        elif self._mode == 'tfidf':
            query_vec = self.vectorizer.transform([query])
            sims = cosine_similarity(query_vec, self._embeddings)
            top_k_indices = np.argsort(sims[0])[-top_k:][::-1]
            return [self.documents[i] for i in top_k_indices]
        else:  # keyword 模式
            # 简单按包含关键词计分
            scores = [sum([1 for word in query.split() if word in doc]) for doc in self.documents]
            top_k_indices = np.argsort(scores)[-top_k:][::-1]
            return [self.documents[i] for i in top_k_indices if scores[i] > 0]

    @property
    def mode(self):
        return self._mode


class Memory:
    """一个组合了短期和长期记忆的统一记忆模块。"""
    def __init__(self, embedding_type: str = 'auto'):
        self.short_term = ShortTermMemory()
        self.long_term = LongTermMemory(embedding_type=embedding_type)

    def add_short_term(self, key: str, value):
        """在短期记忆中存储键值对。"""
        self.short_term.add(key, value)

    def get_short_term(self, key: str):
        """从短期记忆中获取值。"""
        return self.short_term.get(key)

    def remember(self, document: str):
        """在长期记忆中记住一篇文档。"""
        self.long_term.add(document)

    def recall(self, query: str, top_k=3):
        """从长期记忆中回忆与查询相关的信息。"""
        return self.long_term.search(query, top_k=top_k)


if __name__ == "__main__":
    # --- 短期记忆示例 ---
    print("--- 短期记忆演示 ---")
    short_term_mem = ShortTermMemory()
    short_term_mem.add("user_id", "12345")
    short_term_mem.add("session_id", "abc-xyz")
    print(f"用户ID: {short_term_mem.get('user_id')}")
    print(f"会话ID: {short_term_mem.get('session_id')}")
    short_term_mem.delete("session_id")
    print(f"删除会话ID后: {short_term_mem.get('session_id')}")
    print("-" * 20)

    # --- 长期记忆示例 ---
    # 注意: 第一次运行时，会下载嵌入模型，需要一些时间。
    print("\n--- 长期记忆演示 ---")
    long_term_mem = LongTermMemory()
    print("向长期记忆中添加文档...")
    long_term_mem.add("用户的爱好是爬山和摄影。")
    long_term_mem.add("用户的名字叫张伟。")
    long_term_mem.add("用户居住在一个沿海城市。")
    long_term_mem.add("用户是一名数据分析师。")

    query = "这个用户是做什么工作的？"
    print(f"\n查询: '{query}'")
    results = long_term_mem.search(query, top_k=1)
    print(f"最相关的结果: {results[0] if results else '未找到结果'}")

    query_hobby = "他有什么爱好？"
    print(f"\n查询: '{query_hobby}'")
    results_hobby = long_term_mem.search(query_hobby, top_k=1)
    print(f"最相关的结果: {results_hobby[0] if results_hobby else '未找到结果'}")
    print("-" * 20)

    # --- 组合记忆示例 ---
    print("\n--- 组合记忆演示（支持多种长期记忆嵌入方式）---")
    memory = Memory(embedding_type='auto')
    print(f"长期记忆实际使用模式: {memory.long_term.mode}")
    memory.add_short_term("current_topic", "AI记忆系统")
    print(f"当前主题 (来自短期记忆): {memory.get_short_term('current_topic')}")
    memory.remember("AI智能体应该遵循有益、无害和诚实的原则。")
    recalled_info = memory.recall("AI智能体应遵循什么原则？")
    print(f"回忆的信息 (来自长期记忆): {recalled_info}")
