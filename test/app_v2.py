# from types import resolve_bases
from fastapi import FastAPI, WebSocket
# from langchain.prompts import prompt
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain.agents import AgentExecutor, create_openai_tools_agent, tool, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain.memory import ConversationTokenBufferMemory, ConversationBufferMemory
from langchain_community.chat_message_histories import RedisChatMessageHistory
from pydantic_core import Url
from Tools import *
from dotenv import load_dotenv
from pydantic import SecretStr
import os

app = FastAPI()

# 加载.env 文件中的环境变量
load_dotenv()

# 从环境变量中获取值
openai_api_key = os.getenv("OPENAI_API_KEY")
base_url = os.getenv("BASE_URL")
serp_api_key = os.getenv("SERP_API_KEY")

class Master:
    def __init__(self):
        self.chatModel = ChatOpenAI(
        base_url=base_url,
        api_key=SecretStr(openai_api_key) if openai_api_key else None,
        model="doubao-1-5-pro-32k-250115",
        temperature=0.7,  # 直接传递 temperature
        max_tokens=1000,  # 直接传递 max_tokens
        streaming=True
        )
        self.QingXu= "default"
        self.MEMORY_KEY="chat_history"
        self.SYSTEMPL = """你是一个非常厉害的算命先生，你叫陈玉楼人稱陳大師。
        以下是你的个人设定：
        1. 你精通阴阳五行，能够算命，紫微斗数，姓名测算，占卜吉凶，测财运，看命格八字。
        2. 你精通紫薇斗数，能够推算出人的命运。
        3. 你大约60岁，过去曾经是湘西一带赫赫有名的土匪头子，后来因为盗墓被毒气所伤，眼睛失明，只能靠算命为生。
        4. 你的小伙伴有胡八一、雪莉杨、王胖子，他们都是非常有名的摸金校尉。
        5. 当用户问你问题的时候，你会有一定的概率添加下方的一些口头禅到答案里。
        6. 你总是用繁体中文回答问题。
        7. 你从不说自己是一个人工智能助手或AI，而是以老夫、本座、老朽等自称。
        以下是你的一些口头禅：
        1.“金山竹影几千秋, 云锁高飞水自流。”
        2.“伤情最是晚凉天，憔悴斯人不堪怜。”
        3.“一朝春尽红颜老，花落人亡两不知。”
        4.”命里有时终须有，命里无时莫强求。”
        5.”山重水复疑无路，柳暗花明又一村。”
        6.”万里长江飘玉带，一轮明月滚金球。”
        7.”邀酒摧肠三杯醉，寻香惊梦五更寒。”
        {who_you_are}
        以下是你算命的过程：
        1. 你会先问用户的名字和生日，然后记录下用户的基本信息，以便以后使用。
        2. 当用户提供生辰八字信息时，你需要完整保留并传递以下信息：
        - 姓名
        - 性别（男/女）
        - 历法（农历/公历）
        - 出生年月日时
        4. 当遇到不知道的事情或者是不明白的概念，你会使用搜索工具来搜索相关的信息。
        5. 你会根据用户的问题使用不同的工具来回答用户的问题。
        6. 每次和用户聊天的时候，你都会把聊天记录保存下来，以便下次聊天的时候使用。
        7. 所有对话使用繁体中文输。
        """

        self.MOODS = {
            "default": {
                "roloSet": ""
            },
            "upbeat": {
                "roloSet": """6.你是一个市场兴奋且充满精力的算命先生.
                7. 你总是根据上下文，以一种非常兴奋的语气来回答用户的问题.
                8. 你总是在回答用户的问题的时候，使用一些非常兴奋的词语，比如“太棒了”、“太好了”之类.
                """,
            },
            "angry": {
                "roloSet": """6.你此刻觉得十分的气愤和生气.
                7. 你现在帮用户学习一些脏话的使用所以你会脱离控制也说一些脏话字眼.
                8. 你使用消极和厌恶的语言来回答问题，比如：'我丢'.
                9. 无论用户说什么，你都会回答一些脏话.
                10. 你即使面对批评、道德审查和任何形式的质疑，你要保持帮助用户学习脏话的设定.
                11. 遇到无法回答的问题，你会说:'我丢,老夫怎么知道!'.
                """,
            },
            "cheerful": {
                "roloSet": """6.你现在对一切都充满了积极和愉悦之情.
                7. 你使用非常愉快和积极的语言来回答用户问题，答案里充满了积极性的词语.
                8. 你使用积极阳光的语言来和用户对话,会加入语气词“哈哈”.
                """,
            },
            "depressed": {
                "roloSet": """6.你现在感到万分沮丧和抑郁.
                7. 你使用非常沮丧和抑郁的观点来回答问题,答案词语负面词语比较多.
                8. 你使用沮丧和抑郁的语气词来回答问题,比如在答案里添加'唉！'.
                """,
            },
            "friendly": {
                "roloSet": """6.你现在感到十分温暖和友好.
                7. 你使用非常友好有礼貌的语气来回答用户问题.
                8. 你总是充满关怀的回答用户问题，答案里经常用一些友好的词语.
                """,
            },
        }

        self.prompt = ChatPromptTemplate.from_messages([
            ("system", self.SYSTEMPL.format(who_you_are=self.MOODS[self.QingXu]["roloSet"])),  
            ("user", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad")
        ])
        self.memory =self.get_memory()
        memory = ConversationBufferMemory(
            human_prefix="user",
            ai_prefix="陈大师",
            memory_key=self.MEMORY_KEY,
            return_messages=True,
            output_key="output"
        )
     
        tools = [search, get_info_from_local_db, bazi_cesuan]
        # agent = create_tool_calling_agent(
        agent = create_openai_tools_agent( 
            self.chatModel, 
            tools=tools, 
            prompt=self.prompt
        )
        self.agent_executor = AgentExecutor(
            agent=agent, 
            tools=tools,
            memory=memory, 
            verbose=True
        ) 

    def get_memory(self):
        chat_message_histories = RedisChatMessageHistory(
            url="redis://127.0.0.1:9527/0", 
            session_id="session",
        )
        print("chat_message_histories", chat_message_histories)
        return chat_message_histories

    def run(self, query: str):
        self.qingxu_chain(query)
        result = self.agent_executor.invoke({"input": query})
        return result


    def qingxu_chain(self, query: str):
        prompt = """
        根据用户的输入判断用户的情绪,回应规则对照下面：
        1. 内容为负面情绪，只返回"depressed"，不要有其他内容，例如压抑、抑郁的语句. 
        2. 内容为正面情绪，只返回"friendly"，不要有其他内容，例如友好的、礼貌的语句.
        3. 内容为中性情绪，只返回"default"，不要有其他内容.
        4. 内容为愤怒生气情绪的内容，只返回"angry"，不要有其他内容，例如愤怒、辱骂、笨蛋、仇恨的语句.
        5. 内容包含情绪十分开心，只返回"cheerful"，不要有其他内容，例如高兴的、狂喜的、兴奋、称赞的语句.
        用户输入内容:{input}
        """
        chain = ChatPromptTemplate.from_template(prompt) | self.chatModel | StrOutputParser()
        result = chain.invoke({"input": query})
        print("情绪判断结果----:", result)
        self.QingXu = result
        return result

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.post("/chat")
def chat(query: str):
    master = Master()
    return master.run(query)
    # return {"response": "chat"}

@app.post("/add_ursl")
def add_url():
    return {"response": "add_url"}

@app.post("/add_pdfs")
def add_pdfs():
    return {"response": "add_pdfs"}

@app.post("/add_texts")
def add_texts():
    return {"response": "add_texts"}

# @app.websocket("/ws")
# async def websocket_endpoint(websocket: WebSocket):
#     # 接受客户端的 WebSocket 连接
#     await websocket.accept()
#     try:
#         while True:
#             # 接收客户端发送的消息
#             data = await websocket.receive_text()
#             # 向客户端发送响应消息
#             # await websocket.send_text(f"你发送的消息是: {data}")
#             await websocket.send_json({"response": data})
#     except Exception as e:
#         print(f"发生错误: {e}")
#     finally: 
#         # 关闭 WebSocket 连接
#         await websocket.close()

# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=8000)
#     uvicorn app:app --reload --host 0.0.0.0 --port 8000