from langchain_openai import ChatOpenAI

llm = ChatOpenAI(
    base_url="https://ark.cn-beijing.volces.com/api/v3",
    openai_api_key="e2e9e3f3-050e",
    model="doubao-1-5-lite-32k-250115",
    max_tokens=1000,  # 设置最大 token 数
    temperature=0.7,  # 设置温度参数
    streaming=True  # 启用流式输出
)

# 使用流式输出
for chunk in llm.stream("常见的十字花科植物有哪些,请用中文回答,只需要回答植物名称,不需要回答其他内容"):
    print(chunk.content, end="", flush=True)
print()  # 最后打印换行
