from langchain_community.document_loaders import (
    PyPDFLoader, 
    Docx2txtLoader, 
    UnstructuredFileLoader, 
    TextLoader
)
import os
import tempfile
from collections import defaultdict
from langchain_community.retrievers import BM25Retriever
from langchain_huggingface.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFacePipeline
from config import *
import torch
from transformers import pipeline
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM


def load_document(file):
    """
    根据用户上传的不同类型的文件使用不同的加载器进行加载
    :param file: 用户上传的文件
    :return: 加载后的文档
    """
    file_extension = os.path.splitext(file.name)[1].lower()

    with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as tmp:
        tmp.write(file.getvalue())
        tmp_path = tmp.name

    try:
        if file_extension == '.pdf':
            loader = PyPDFLoader(tmp_path)
        elif file_extension == '.docx':
            loader = Docx2txtLoader(tmp_path)
        elif file_extension == '.txt':
            loader = TextLoader(tmp_path)
        else:
            loader = UnstructuredFileLoader(tmp_path)

        return loader.load()
    except Exception as e:
        st.error(f"文档加载失败：{str(e)}")
        return []
    finally:
        os.unlink(tmp_path)


def process_documents(files):
    # 存储所有文档分割后的文本块
    all_chunks = []
    # 记录每个文档对应的文本块（键：文本名，值：文本块列表）
    doc_mappings = defaultdict(list)

    for file in files:
        if file.name in st.session_state.processed_files:
            continue
        
        with st.spinner(f"处理 {file.name}..."):
            documents = load_document(file)
            # 若加载失败跳过该文件
            if not documents:
                continue

            chunks = TEXT_SPLITER.split_documents(documents)

            # 为每个文本块添加来源文档标识
            for chunk in chunks:
                chunk.metadata["source_doc"] = file.name
            
            if len(st.session_state.doc_summaries) < 3:
                generate_document_summary(file.name, chunks)

            all_chunks.extend(chunks)
            doc_mappings[file.name] = chunks

            st.session_state.processed_files[file.name] = True
            st.session_state.active_docs.add(file.name)

    if not all_chunks:
        return None

    embeddings = HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL,
        model_kwargs={'device': 'cuda' if torch.cuda.is_available() else 'cpu'},
        encode_kwargs={'normalize_embeddings': True}
    )

    vector_db = Chroma.from_documents(
        documents=all_chunks,
        embedding=embeddings,
        persist_directory=CHROMA_PERSIST_DIR
    )

    texts = [doc.page_content for doc in all_chunks]
    metadatas = [doc.metadata for doc in all_chunks]
    keyword_retriever = BM25Retriever.from_texts(texts, metadatas=metadatas)

    return vector_db, keyword_retriever


def load_local_summary_model(model_path):
    summarizer = pipeline(
        "summarization",
        model=model_path,
        device=0,
        model_kwargs={"max_length": 1024, "min_length": 30}
    )
    return HuggingFacePipeline(pipeline=summarizer)


def generate_document_summary(doc_name, chunks):
    try:
        # 加载模型和 tokenizer
        model_name = SUMMARY_MODEL_ID
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        model = AutoModelForSeq2SeqLM.from_pretrained(model_name)

        # 将设备设置为 GPU（如果可用）
        device = 0 if torch.cuda.is_available() else -1
        if device == 0:
            model = model.cuda()

        # 提取前5个chunk的内容
        text = " ".join([chunk.page_content for chunk in chunks[:3]])

        # 标记化输入文本，并截断到最大长度
        inputs = tokenizer([text], max_length=1024, return_tensors="pt", truncation=True)

        # 将输入移动到模型所在的设备
        if device == 0:
            inputs = {k: v.cuda() for k, v in inputs.items()}

        # 生成摘要
        summary_ids = model.generate(
            inputs["input_ids"],
            num_beams=4,
            max_length=80,
            min_length=30,
            early_stopping=True
        )

        summary = tokenizer.decode(summary_ids[0], skip_special_tokens=True)
        st.session_state.doc_summaries[doc_name] = summary
    except Exception as e:
        st.session_state.doc_summaries[doc_name] = f"摘要生成失败: {str(e)}"
