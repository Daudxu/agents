from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from dotenv import load_dotenv
from pydantic import SecretStr
import os

app = FastAPI()

# 加载.env 文件中的环境变量
load_dotenv()

# 从环境变量中获取值
openai_api_key = os.getenv("OPENAI_API_KEY")
base_url = os.getenv("BASE_URL")

class Master:
    def __init__(self):
        self.chatModel = ChatOpenAI(
            base_url=base_url,
            api_key=SecretStr(openai_api_key) if openai_api_key else None,
            model="doubao-1-5-lite-32k-250115",
            model_kwargs={
                "temperature": 0.7,
                "max_tokens": 1000,
            },
            streaming=True
        )
        self.MEMORY_KEY="chat_history"
        self.SYSTEMPL = ""
        # Fix the prompt initialization
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", "你是一个助手"),
            ("user", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad")
        ])
        self.memory = ""
        agent = create_openai_tools_agent(
            self.chatModel, 
            tools=[], 
            prompt=self.prompt
        )
        self.agent_executor = AgentExecutor(agent=agent, tools=[], verbose=True) 

    def run (self, query: str):
        result = self.agent_executor.invoke({"input": query})
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

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    # 接受客户端的 WebSocket 连接
    await websocket.accept()
    try:
        while True:
            # 接收客户端发送的消息
            data = await websocket.receive_text()
            # 向客户端发送响应消息
            # await websocket.send_text(f"你发送的消息是: {data}")
            await websocket.send_json({"response": data})
    except Exception as e:
        print(f"发生错误: {e}")
    finally: 
        # 关闭 WebSocket 连接
        await websocket.close()

# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=8000)
