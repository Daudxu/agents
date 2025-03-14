import uuid

from langchain_core.messages import HumanMessage,SystemMessage,AIMessage
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent
import os
from pydantic import SecretStr
from dotenv import load_dotenv
from langchain.agents import AgentExecutor, create_openai_tools_agent, create_tool_calling_agent, tool
# 加载.env 文件中的环境变量
load_dotenv()

# 从环境变量中获取值
openai_api_key = os.getenv("OPENAI_API_KEY")
base_url = os.getenv("BASE_URL")
serp_api_key = os.getenv("SERP_API_KEY")

# 将此函数标记为工具
@tool
def get_user_age(name: str) -> str:
    """使用此工具来查找用户的年龄。"""
    # 这是实际实现的占位符
    if "bob" in name.lower():
        return "42岁"
    return "41岁"

# 创建一个内存保存器，用于保存对话历史
memory = MemorySaver()
# 初始化 OpenAI 聊天模型
model = ChatOpenAI(
    base_url=base_url,
    api_key=SecretStr(openai_api_key) if openai_api_key else None,
    model="doubao-1-5-pro-32k-250115",
    temperature=0.7,  # 直接设置温度
    max_tokens=1000,  # 直接设置最大令牌数
    streaming=True
)
#

# 创建一个 React 代理应用
app = create_react_agent(
    model,
    # 指定代理可以使用的工具列表
    tools=[get_user_age],
    # 指定用于保存对话历史的检查点
    checkpointer=memory,
)

# 线程 ID 是一个唯一的键，用于标识特定的对话。
# 我们在这里随机生成一个 UUID。
# 这使得单个应用程序可以管理多个用户之间的对话。
thread_id = uuid.uuid4()
# config = {"configurable": {"thread_id": thread_id}}

# 告诉 AI 我们的名字是 Bob，并要求它使用工具来确认
# 它能够像代理一样工作。
input_message = HumanMessage(content="你好！我是谁。我多少岁了？")

# 流式处理用户输入并打印 AI 的响应
for event in app.stream({"messages": [input_message]}, {"configurable": {"thread_id": thread_id}}, stream_mode="values"):
    event["messages"][-1].pretty_print()

# 确认聊天机器人可以访问之前的对话
# 并且可以回复用户，表明它记得用户的名字是 Bob。
input_message = HumanMessage(content="你还记得我的名字吗？")

# 流式处理用户输入并打印 AI 的响应
for event in app.stream({"messages": [input_message]}, {"configurable": {"thread_id": thread_id}}, stream_mode="values"):
    # event["messages"][-1].pretty_print()
    print(event["messages"][-1].content)
    