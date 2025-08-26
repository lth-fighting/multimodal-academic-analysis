from documents_processor import *
import streamlit as st
from retrieval_qa import get_answer
from visualization import plot_retrieval_history
from types import SimpleNamespace

# 系统初始化
st.set_page_config(page_title="多模态学术分析系统", page_icon="📚", layout="wide")
init_session_state()

# 侧边栏
st.sidebar.title("📚 文档管理仓库")
uploaded_files = st.sidebar.file_uploader(
    "上传文献: pdf/txt/docx...",
    type=["pdf", "txt", "docx"],
    accept_multiple_files=True
)

if uploaded_files:
    file_to_process = [f for f in uploaded_files if f.name not in st.session_state.processed_files]

    if file_to_process:
        with st.spinner("正在处理文档中..."):
            vector_db, keyword_retriever = process_documents(file_to_process)

            if not vector_db:
                st.warning("未处理到有效文档")
            else:
                st.session_state.vector_db = vector_db
                st.session_state.keyword_retriever = keyword_retriever
                st.sidebar.success(f"成功处理 {len(file_to_process)} 个新文档")

if st.session_state.active_docs:
    st.sidebar.subheader("激活文档")
    active_docs = st.sidebar.multiselect(
        "选择重点分析的文档",
        options=list(st.session_state.active_docs),
        default=list(st.session_state.active_docs)
    )
    st.session_state.active_docs = set(active_docs)

if st.session_state.doc_summaries:
    st.sidebar.subheader("文献精彩摘要")
    for doc_name, doc_summary in st.session_state.doc_summaries.items():
        if doc_name in st.session_state.active_docs:
            with st.sidebar.expander(f"📝 {doc_name}"):
                st.caption(doc_summary)

st.title("🎓 多模态学术文献分析问答系统")
st.caption("上传文献后，即可进行跨文档智能问答与分析...")

tab1, tab2, tab3, tab4 = st.tabs(["问答系统", "重点文献分析", "检索分析", "系统信息"])

with tab1:
    if st.session_state.messages is None:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

            if message.get("sources"):
                with st.expander("来源文献详情"):
                    for i, doc in enumerate(message["sources"]):
                        sources = doc.metadata.get("source_doc", "Unknown Document")
                        page = doc.metadata.get("page", 0) + 1
                        st.markdown(f"**Original {i+1}**: {sources} (Page {page})")

                        st.info(doc.page_content[:500] + ("..." if len(doc.page_content) > 500 else ""))

    if question := st.chat_input():
        st.session_state.messages.append({"role": "user", "content": question})
        with st.chat_message("user"):
            st.markdown(question)

        with st.spinner("正在分析文献..."):
            answer, sources = get_answer(question)

        st.session_state.messages.append({
            "role": "assistant",
            "content": answer,
            "sources": sources
        })

        with st.chat_message("assistant"):
            st.markdown(answer)

            if sources:
                with st.expander("来源文献详情"):
                    for i, doc in enumerate(sources):
                        source = doc.metadata.get("source_doc", "Unknown Document")
                        page = doc.metadata.get("page", 0) + 1
                        st.markdown(f"**Original {i+1}**: {source} (Page {page})")
                        st.info(doc.page_content[:500] + ("..." if len(doc.page_content) > 500 else ""))

with tab2:
    if not st.session_state.processed_files:
        st.info("请先上传文档")
    else:
        st.subheader("文档分析工具")

        col1, col2 = st.columns(2)
        with col1:
            st.markdown("### 📊 文档统计")
            doc_stats = []
            for doc_name in st.session_state.active_docs:
                chunks = []
                vector_data = st.session_state.vector_db.get()
                for i, metadata in enumerate(vector_data["metadatas"]):
                    if metadata.get("source_doc") == doc_name:
                        chunks.append(vector_data["documents"][i])

                if chunks:  # 确保chunks不为空
                    doc_stats.append({
                        "文档": doc_name,
                        "段落数": len(chunks),
                        "平均长度": sum(len(c) for c in chunks) // len(chunks)
                    })

            if doc_stats:
                st.dataframe(doc_stats)

        with col2:
            st.markdown("### 🔍 概念分析")
            concept = st.text_input("请输入需要分析的概念")
            if concept:
                concept_docs = []
                vector_data = st.session_state.vector_db.get()
                for i in range(len(vector_data["documents"])):
                    if vector_data["metadatas"][i].get("source_doc") in st.session_state.active_docs:
                        if concept.lower() in vector_data["documents"][i].lower():
                            doc_obj = SimpleNamespace()
                            doc_obj.page_content = vector_data["documents"][i]
                            doc_obj.metadata = vector_data["metadatas"][i]
                            concept_docs.append(doc_obj)

                if concept_docs:
                    st.success(f"找到 {len(concept_docs)} 处提及'{concept}'")
                    for doc in concept_docs[:3]:
                        source = doc.metadata.get("source_doc", "未知文档")
                        page = doc.metadata.get("page", 0) + 1
                        st.markdown(f"📄 **{source}** (页码: {page})")
                        st.caption(doc.page_content[:300] + "...")
                else:
                    st.warning(f"未找到提及到'{concept}'概念的文献内容")

with tab3:
    if not st.session_state.retrieval_history:
        st.info("检索的历史为空，快去检索你的关键词吧!")
    else:
        st.subheader("检索效果分析")
        plot_retrieval_history()

        st.markdown("### 📈 检索统计")
        last_query = st.session_state.retrieval_history[-1]
        st.metric("向量检索结果:", last_query["vector_results"])
        st.metric("关键词检索结果:", last_query["keyword_results"])
        st.metric("最终检索结果:", last_query["final_results"])

        st.markdown("### 🔧 检索优化建议")
        if last_query["vector_results"] == 0:
            st.warning("向量数据库检索未返回结果，建议尝试不同表述方式或添加更多文献上下文")
        elif last_query["keyword_results"] > last_query["vector_results"] * 2:
            st.info("关键词检索效果明显优于向量数据库检索，建议在问题中使用更具体的概念或术语")
        elif last_query["final_results"] < 3:
            st.error("最终返回的检索结果较少，请尝试简化问题或扩大检索范围")
        else:
            st.info("当前检索效果良好")


with tab4:
    st.subheader("系统配置")
    st.markdown(f"""
    - **嵌入模型**: {EMBEDDING_MODEL}
    - **摘要模型**: {SUMMARY_MODEL_ID}
    - **已处理文档数**: {len(st.session_state.processed_files)}
    - **内存中的段落数**: {len(st.session_state.vector_db.get()["documents"]) if st.session_state.vector_db else 0}
    """)

    st.subheader("使用指南")
    st.markdown(f"""
    1. **上传文档**: 在左侧侧栏上传PDF/DOCX/TXT格式的学术文献
    2. **文档选择**: 在左侧激活文档中选择激活或取消需要重点分析的学术文档
    3. **摘要查看**: 在左侧侧栏最下方可通过展开对应文献查看相关文献的具体摘要信息
    4. **智能问答**: 
        - 问题提问: 在输入框中输入具体问题并点击发送
          例如: 请告诉我该文献在具身智能领域做出的突破是什么？
        - 跨文档分析: 支持将上传的多篇文献进行跨文档分析，提供更综合的问答体验
          例如: 请比较这三篇文献的实验结果
    5. **检索分析与统计**:
        - 文档统计: 查看各文档的段落分布 
        - 概念追踪: 定位特定术语在所有文档中的位置
    6. **检索优化**: 根据检索分析调整查询策略  
    """)

    if st.button("清空文档"):
        init_session_state(True)
        st.rerun()

st.sidebar.divider()
st.sidebar.info(
    f"系统状态: {len(st.session_state.active_docs)} 个激活文档\n"
    "技术栈: Langchain + ChromaDB + HuggingFace"
)

