from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.runnables.history import RunnableWithMessageHistory
import streamlit as st
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_community.chat_message_histories import ChatMessageHistory

# DeepSeek 基址
DEEPSEEK_URL = "https://api.deepseek.com"
# DeepSeek api_key
DEEPSEEK_KEY = "your-deepseek-api-key"

# 向量嵌入模型
EMBEDDING_MODEL = "./bge-small-zh-v1.5"
# 摘要模型
SUMMARY_MODEL_ID = "./bart-large-chinese"
# 向量库存储路径
CHROMA_PERSIST_DIR = "./chroma_db"

# 文本分割配置
TEXT_SPLITER = RecursiveCharacterTextSplitter(
    chunk_size=400,
    chunk_overlap=100,
    length_function=len,
    separators=[r"\n\n", r"\n", "。", "！", "？", r"\nChapter", r"(?<=\. )", " ", ""]
)

# 问答系统提示词模板
QA_SYS_PROMPT = """
【角色与任务】
你是一个专业的学术文献分析助手，请严格基于以下文献上下文进行问题的回答：
{context}

【你需要回答的问题】
{question}

【注意】
1.你要给出详细准确的答案，并指出引用的文献来源、具体页码等，使用中文进行回答，回答中不要重复文中的话语，你只需要根据用户的问题结合文献进行总结性的回答。
2.若文献的内容为非中文，请结合文献的具体内容翻译成中文，要求翻译准确、结合文献的具体场景，禁止偏离文献主题。
3.你可能拿到的是多篇文献的上下文，所以你最好能将不同文献进行串联，找到不同文献的异同，建议比较它们的观点和方法。
4.在回答的最后，你可以向用户提供一些易于用户理解文献的建议，并向用户询问是否还有什么不懂的地方，但禁止偏离用户问题的方向。
5.语言简洁明了、逻辑清晰、分点说明，最好能加上一些emoji进行美化（如果适用）。
6.如果用户的问题不涉及文献中的内容，你只需要回答“抱歉，我无法在文献中找到你提及的相关内容”。
"""

PROMPT_TEMPLATE = ChatPromptTemplate.from_messages([
    ("system", QA_SYS_PROMPT),
    MessagesPlaceholder(variable_name="history"),  # 对话历史占位符
    ("human", "{question}")  # 用户当前问题
])


def init_history_store():
    return {}


def get_session_history(session_id: str, store):
    if session_id not in store:
        store[session_id] = ChatMessageHistory()
    return store[session_id]


def init_session_state(reset=False):
    if reset:
        st.session_state.vector_db = None
        st.session_state.keyword_retriever = None
        st.session_state.processed_files = {}
        st.session_state.doc_summaries = {}
        st.session_state.active_docs = set()
        st.session_state.retrieval_history = []
        st.session_state.messages = []
        st.session_state.chat_history_store = init_history_store()

    if "vector_db" not in st.session_state:
        st.session_state.vector_db = None
    if "keyword_retriever" not in st.session_state:
        st.session_state.keyword_retriever = None
    if "processed_files" not in st.session_state:
        st.session_state.processed_files = {}
    if "doc_summaries" not in st.session_state:
        st.session_state.doc_summaries = {}
    if "active_docs" not in st.session_state:
        st.session_state.active_docs = set()
    if "retrieval_history" not in st.session_state:
        st.session_state.retrieval_history = []
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "chat_history_store" not in st.session_state:
        st.session_state.chat_history_store = init_history_store()

