# visualization.py
import matplotlib.pyplot as plt
import numpy as np
import streamlit as st


def plot_retrieval_history():
    if st.session_state.retrieval_history is None:
        return

    history = st.session_state.retrieval_history[-10:]

    plt.rcParams['font.family'] = ["SimHei"]
    plt.rcParams['axes.unicode_minus'] = False
    fig, ax = plt.subplots(figsize=(10, 6))

    queries = [f"Question {i+1}" for i in range(len(history))]
    vector_results = [h["vector_results"] for h in history]
    keyword_results = [h["keyword_results"] for h in history]
    final_results = [h["final_results"] for h in history]

    bar_width = 0.25
    index = np.arange(len(queries))

    ax.bar(index, vector_results, bar_width, label="向量检索")
    ax.bar(index + bar_width, keyword_results, bar_width, label="关键词检索")
    ax.bar(index + 2 * bar_width, final_results, bar_width, label="最终结果")

    ax.set_xlabel('查询序列')
    ax.set_ylabel('结果数量')
    ax.set_title('混合检索效果分析')
    ax.set_xticks(index + bar_width)
    ax.set_xticklabels(queries)
    ax.legend()

    st.pyplot(fig)

