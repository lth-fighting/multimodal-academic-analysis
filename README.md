# 🎓 多模态学术文献分析问答系统

一个基于 Streamlit 构建的智能文献分析助手。该系统能够处理上传的学术文献（PDF, DOCX, TXT），通过混合检索技术（向量检索 + 关键词检索）快速定位信息，并利用大语言模型（DeepSeek）生成基于上下文的、引证详实的专业回答，助力研究人员高效进行文献回顾和知识发现。

## ✨ 核心功能

- **📄 多格式文档处理**: 支持批量上传并解析 PDF、DOCX、TXT 等多种格式的学术文献。
- **🤖 智能问答**: 基于上传的文献内容进行智能问答，答案均提供准确的文献来源和页码引用。
- **🔍 混合检索策略**: 结合 **ChromaDB 向量检索** 与 **BM25 关键词检索**，确保检索结果既语义相关又关键词匹配。
- **📊 可视化分析**: 提供文档统计、概念追踪和检索效果分析仪表盘，帮助用户优化查询策略。
- **🌐 跨文档分析**: 可同时处理多篇文献，并支持对比分析不同文献中的观点、方法和实验结果。
- **📝 自动摘要**: 自动为处理的文献生成内容摘要，方便快速了解文献概貌。

## 🛠 技术栈

- **前端框架**: [Streamlit](https://streamlit.io/)
- **大语言模型**: [DeepSeek](https://www.deepseek.com/) (`deepseek-chat`)
- **嵌入模型**: [BGE-small-zh-v1.5](https://huggingface.co/BAAI/bge-small-zh-v1.5)
- **摘要模型**: [Bart-large-chinese](https://huggingface.co/facebook/bart-large-chinese)
- **向量数据库**: [ChromaDB](https://www.trychroma.com/)
- **NLP 框架**: [LangChain](https://www.langchain.com/), [Transformers](https://huggingface.co/docs/transformers)
- **开发语言**: Python 3.9+

## 📦 安装与运行

### 前提条件

- Python 3.9 或更高版本
- Git
- 一个有效的 DeepSeek API Key (从[官网](https://platform.deepseek.com/)获取)

### 1. 克隆项目

git clone <你的项目仓库地址>
cd multimodal-academic-qa-system

### 2. 安装依赖
建议使用虚拟环境（如 conda 或 venv）。

# 创建虚拟环境 (可选)
conda create -n academic-qa python=3.10
conda activate academic-qa

# 安装依赖包
pip install -r requirements.txt
### 3. 配置 API 密钥
在 config.py 文件中，替换为您自己的 API 密钥：
# DeepSeek api_key
DEEPSEEK_KEY = "sk-your-deepseek-api-key-here"

### 4. 下载模型（可选）
项目默认使用 Hugging Face 的模型，运行时会自动下载。若需离线使用或加速，可提前下载并修改 config.py 中的路径：

# 创建模型存储目录
mkdir models

# 下载嵌入模型 (可选)
git lfs install
git clone https://huggingface.co/BAAI/bge-small-zh-v1.5 ./models/bge-small-zh-v1.5

# 下载摘要模型 (可选)
git clone https://huggingface.co/facebook/bart-large-chinese ./models/bart-large-chinese
然后修改 config.py：

EMBEDDING_MODEL = "./models/bge-small-zh-v1.5"
SUMMARY_MODEL_ID = "./models/bart-large-chinese"

### 5. 运行应用
bash
streamlit run main.py
终端会输出一个本地 URL (通常是 http://localhost:8501)，在浏览器中打开即可使用系统。

## 🚀 使用方法
上传文档: 在左侧边栏上传 PDF/DOCX/TXT 格式的学术文献。

选择文档: 在"激活文档"区域选择当前会话需要重点分析的文献。

开始问答: 在主界面选项卡的输入框提出您的问题，例如：

"请总结这篇文献的核心观点。"

"比较A文献和B文献中使用的研究方法。"

"在所有这些文献中，'气候变化'是如何被讨论的？"

查看答案与来源: 系统会生成回答，并可展开查看引用的具体文献片段及页码。

使用分析工具: 利用"重点文献分析"和"检索分析"选项卡进行深度数据探索和检索优化。

## 📁 项目结构

multimodal-academic-qa-system/

├── main.py                    # 主应用入口，Streamlit 界面逻辑

├── config.py                  # 全局配置（API密钥、模型路径、提示词模板等）

├── retrieval_qa.py            # 核心检索与问答链逻辑

├── documents_processor.py     # 文档加载、处理、向量化模块

├── deepseek_llm.py           # DeepSeek LLM 调用封装

├── visualization.py           # 检索历史可视化绘图

├── requirements.txt           # Python 项目依赖

└── chroma_db/                 # 向量数据库持久化存储目录（运行时自动生成）

## ⚙️ 配置说明
主要配置选项均在 config.py 文件中：

模型路径: 可切换为其他 Hugging Face 模型或本地路径。

文本分割: 可调整 chunk_size 和 chunk_overlap 以优化检索粒度。

提示词模板: QA_SYS_PROMPT 定义了系统的角色和行为，可根据需要进行定制。

检索数量: 在 retrieval_qa.py 中可调整混合检索返回的文档数量 (unique_docs[:6])。

## ❓ 常见问题
Q: 处理文档时出现 CUDA Out of Memory 错误？
A: 尝试在 config.py 中将嵌入模型设备改为 cpu： model_kwargs={'device': 'cpu'}，或减小 chunk_size。

Q: 如何提高问答的准确性？
A: 确保问题与上传的文献相关。对于复杂问题，尝试拆分成多个简单问题。在侧边栏精选"激活文档"范围也能有效提升准确性。

Q: 支持英文或其他语言的文献吗？
A: 支持。但系统提示词模板和嵌入模型主要针对中文优化。处理英文文献时，建议将 EMBEDDING_MODEL 切换为 BAAI/bge-small-en-v1.5 等英文模型，并相应修改提示词。

## 👥 致谢
感谢 DeepSeek 提供强大的大语言模型接口。

感谢 LangChain 和 Chroma 社区提供的优秀框架和工具。

感谢所有开源模型提供者，包括 BAAI 和 Facebook。
