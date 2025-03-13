import os, requests
from dotenv import load_dotenv
# llm
from langchain_openai import OpenAIEmbeddings,ChatOpenAI
# 工具
from langchain_community.utilities import SerpAPIWrapper
from langchain_community.vectorstores import Qdrant
from langchain.agents import tool
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from qdrant_client import QdrantClient
from pydantic import SecretStr
from langchain_qdrant import QdrantVectorStore
from langchain_core.output_parsers import JsonOutputParser

# 加载.env 文件中的环境变量
load_dotenv()

# 从环境变量中获取值
openai_api_key = os.getenv("OPENAI_API_KEY")
base_url = os.getenv("BASE_URL")
serp_api_key = os.getenv("SERP_API_KEY")  
yfj_api_key = os.getenv("YFJ_API_KEY")  

@tool
def test():
    """"test tool"""
    return "test"  

@tool
def search(query: str):
    """"需要搜索的时候搜索"""
    try:
        print("query==================: ", query)
        serpapi = SerpAPIWrapper(serpapi_api_key=serp_api_key)
        return serpapi.run(query)
    except Exception as e:
        print(f"搜索出错: {str(e)}")
        return "搜索过程中发生错误，请稍后重试"

@tool
def get_info_from_local_db(query: str):
    """只有搜索2025年才会使用这个工具"""
    client = Qdrant(
        QdrantClient(path="D:\testWork\agents\local_qdrant"),
        "local_documents",
        OpenAIEmbeddings(api_key=SecretStr(openai_api_key) if openai_api_key else None),
    )
    retriever = client.as_retriever(search_type="mmr")   
    result = retriever.get_relevant_documents(query)
    return result

@tool
def bazi_cesuan(query:str):
    """只有做八字排盘的时候才会使用这个工具,需要输入用户姓名，性别，出生公历/农历年月日时,如果缺少
    用户姓名和出生年月日时则不可用."""
    prompt = ChatPromptTemplate.from_template("""
        你是一个参数查询助手，根据用户输入内容找出相关的参数并按json格式返回。
        JSON字段如下:
        - "name": "姓名"
        - "sex": "性别 0代表男 1代表女 (如果用户输入的时男则为sex为0，如果用户输入的是女则sex为1 如果没写就根据名字判断) "
        - "type": "历类型 0农历 1公历，(默认是公历1)"
        - "year": "出生年份,例:1998"
        - "month": "出生月份,例:8"
        - "day": "出生日期,例:8"
        - "hours": "出生小时,例:14"
        - "minute": "出生分 例: 30 (如果不知道具体分，可以传数字 0) "
        如果没有找到相关参数,则需要提醒用户告诉你这些内容,只返回数据结构,不要有其他的评论。
        用户输入: {query}
    """)
    parser = JsonOutputParser()
    prompt = prompt.partial(format_instructions=parser.get_format_instructions())
    llm =  ChatOpenAI(
        base_url=base_url,
        api_key=SecretStr(openai_api_key) if openai_api_key else None,
        model="doubao-1-5-lite-32k-250115",
        model_kwargs={
            "temperature": 0,
            "max_tokens": 1000,
        },
        streaming=True
    ) 
    chain = prompt| llm | parser
    data = chain.invoke({"query": query})
    url = "https://api.yuanfenju.com/index.php/v1/Bazi/paipan"
    data['api_key'] = yfj_api_key
    print("===data===:", data)
    result = requests.post(url, data=data)
    if result.status_code == 200:
        print("=======返回数据=======")
        try:
            json_data = result.json()
            print("API返回数据结构：", json_data)
            
            if json_data.get('errcode') == 0 and 'data' in json_data:
                data = json_data['data']
                base_info = data.get('base_info', {})
                bazi_info = data.get('bazi_info', {})
                
                # 构建返回信息
                response = f"""
                        姓名：{base_info.get('name')}
                        性别：{base_info.get('sex')}
                        公历：{base_info.get('gongli')}
                        农历：{base_info.get('nongli')}
                        八字：{' '.join(bazi_info.get('bazi', []))}
                        纳音：{' '.join(bazi_info.get('na_yin', []))}
                        起运：{base_info.get('qiyun')}
                        交运：{base_info.get('jiaoyun')}
                        主星：{' '.join(bazi_info.get('tg_cg_god', []))}
                        """
                return response.strip()
            else:
                print("API返回数据结构不符合预期：", json_data)
                return "抱歉，八字排盘结果解析失败，请稍后重试"
                
        except Exception as e: 
            print("数据解析错误：", str(e))
            return "八字排盘数据解析出错，请检查输入信息是否完整"
    else:
        print("API请求失败，状态码：", result.status_code)
        return "八字排盘服务暂时不可用，请稍后重试"

@tool
def yaoyiguan(query:str):
    """需要占卜测算的时调用"""