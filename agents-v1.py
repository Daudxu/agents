from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.agents import initialize_agent, AgentType
from dotenv import load_dotenv
import os

# 加载.env 文件中的环境变量
load_dotenv()

# 从环境变量中获取值
openai_api_key = os.getenv("OPENAI_API_KEY")
base_url = os.getenv("BASE_URL")

# 创建 ChatOpenAI 实例，配置相关参数
llm = ChatOpenAI(
    base_url=base_url,
    openai_api_key=openai_api_key,
    model="doubao-1-5-lite-32k-250115",
    max_tokens=1000,  # 设置最大 token 数
    temperature=0.7,  # 设置温度参数
    streaming=True  # 启用流式输出
)

# 定义提示词模板，变量名使用英文
prompt_template = PromptTemplate(
    input_variables=["word"],
    template="同学你好，我是资深英语老师，针对{word}，还有什么想要了解的？比如它的用法、例句或者同义词等方面。",
)

# 模拟系统已知的单词
system_word = "apple"

# 格式化提示词并输出
formatted_prompt = prompt_template.format(word=system_word)
print(formatted_prompt)

# 这里不使用工具，仅让 Agent 基于语言模型进行交互
tools = []
agent = initialize_agent(
    tools,
    llm,
    agent=AgentType.CHAT_ZERO_SHOT_REACT_DESCRIPTION,
    verbose=False  # 设置为 True 以查看详细的执行过程
)

while True:
    # 等待用户输入想了解的内容
    user_input = input("请输入你想了解的具体内容（输入 '退出' 结束本次对话）: ")
    if user_input.lower() == "退出":
        print("本次对话结束。")
        break
    elif system_word.lower() not in user_input.lower():
        print(f"请输入与 {system_word} 相关的内容，谢谢！")
        continue

    try:
        # 使用 Agent 处理用户输入，按照提示替换 run 为 invoke
        response = agent.invoke({"input": formatted_prompt + "\n" + user_input})
        # 提取回复内容并格式化输出
        reply = response['output']
        print("AI老师:\n", reply.replace('\n', '\n  '))  # 添加缩进使输出更美观
    except Exception as e:
        print(f"出现错误: {str(e)}")
