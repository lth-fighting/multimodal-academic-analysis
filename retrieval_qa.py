# retrieval_qa.py
from config import *
from deepseek_llm import paper_answer
import torch
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM


def hybrid_retrieval(query, vector_retriever, keyword_retriever):
    """
    向量数据库和关键词检索器混合检索
    :param query: 用户问题
    :param vector_retriever: 向量检索器
    :param keyword_retriever: 关键词检索器
    :return: 返回前6个检索结果
    """
    # 向量检索
    vector_docs = vector_retriever.invoke(query)

    # 关键词检索
    keyword_docs = keyword_retriever.invoke(query)

    # 组合结果并去重
    all_docs = vector_docs + keyword_docs
    seen = set()
    unique_docs = []

    for doc in all_docs:
        identifier = (doc.page_content[:50], doc.metadata.get("source_doc", ""), doc.metadata.get("page", 0))
        if identifier not in seen:
            seen.add(identifier)
            unique_docs.append(doc)

    st.session_state.retrieval_history.append({
        "query": query,
        "vector_results": len(vector_docs),
        "keyword_results": len(keyword_docs),
        "final_results": len(unique_docs)
    })

    return unique_docs[:6]


def get_answer(query):
    """
    处理用户问题并返回答案
    :param query: 用户问题
    :return: 返回检索获得的答案
    """
    if st.session_state.vector_db is None:
        return "请先上传并处理文档", []

    vector_retriever = st.session_state.vector_db.as_retriever(
        search_type="similarity",
        search_kwargs={"k": 4}
    )

    docs = hybrid_retrieval(query, vector_retriever, st.session_state.keyword_retriever)

    context = "\n\n".join([
        f"来源文档: {doc.metadata.get("source_doc", '未知')}\n"
        f"所在页码: {doc.metadata.get("page", 0)+1}\n"
        f"具体内容: {doc.page_content[:500]}{"..." if len(doc.page_content) > 500 else ''}"
        for doc in docs
    ])

    try:
        prompt_text = f"{QA_SYS_PROMPT.format(context=context, question=query)}"
        answer = paper_answer(prompt_text)

    except Exception as e:
        answer = f"生成答案时错误: {str(e)}"

    return answer, docs


