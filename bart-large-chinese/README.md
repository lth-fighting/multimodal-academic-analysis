# 📁 模型存放指南

## 🤖 本地模型配置

为了让系统能够使用本地的 `bart-large-chinese` 摘要模型，请按照以下步骤操作：

### 1. 下载模型文件

首先从 Hugging Face 下载 `bart-large-chinese` 模型：

```bash
# 使用 git lfs 下载（推荐）
git lfs install
git clone https://huggingface.co/facebook/bart-large-chinese ./models/bart-large-chinese

# 或者直接下载压缩包并解压到此文件夹
```

### 2. 所需模型文件

请确保 `models/bart-large-chinese/` 文件夹中包含以下必要文件：

```
models/bart-large-chinese/
├── config.json              # 模型配置文件
├── pytorch_model.bin        # 模型权重文件
├── vocab.json               # 词汇表文件
├── merges.txt               # BPE 合并文件
├── tokenizer.json           # 分词器配置
└── special_tokens_map.json  # 特殊令牌映射
```

### 3. 修改配置文件

在 `config.py` 中更新模型路径：

```python
# 修改摘要模型路径指向本地模型
SUMMARY_MODEL_ID = "./models/bart-large-chinese"
```

### 4. 验证安装

运行系统后，如果看到以下提示说明配置成功：
```
✅ 成功加载本地 bart-large-chinese 模型
```

## ⚡ 优势

- **更快的加载速度**：无需每次从网络下载
- **离线使用**：无网络环境下仍可使用
- **稳定性**：避免因网络问题导致的模型加载失败

## ❓ 常见问题

**Q: 如果我不想使用本地模型怎么办？**
**A:** 保持 `SUMMARY_MODEL_ID = "./bart-large-chinese"` 不变，系统会自动从 Hugging Face 下载（需要网络连接）。

**Q: 模型文件太大无法上传到GitHub？**
**A:** 是的，因此我们使用 `.gitignore` 排除了模型文件。请用户自行下载放置。

**Q: 如何知道模型是否加载成功？**
**A:** 查看系统启动日志，成功加载会显示模型信息。

---

💡 **提示**：使用本地模型可以显著提升系统性能和稳定性，推荐在有足够磁盘空间的情况下配置。
