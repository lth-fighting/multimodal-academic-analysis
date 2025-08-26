# deepseek_llm.py
from langchain_openai import ChatOpenAI
from config import *


def paper_answer(prompt):
    try:
        llm = ChatOpenAI(
            openai_api_key=DEEPSEEK_KEY,
            openai_api_base=DEEPSEEK_URL,
            model_name="deepseek-chat",
            temperature=0.5
        )

        response = llm.invoke(prompt)
        answer = response.content

        return answer
    except Exception as e:
        return f"调用DeepSeek API时出错: {str(e)}"


