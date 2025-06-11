# Paper Agent

使用 `smolagent` 框架思路实现的一个自动检索整理论文的工作流示例。该脚本会从 arXiv 上检索用户指定主题的最新论文，并返回包含如下信息的列表：

- 论文标题
- 作者及其单位（如果 arXiv 提供）
- 论文摘要的中文翻译
- 论文的发表日期

## 安装依赖

脚本依赖 `openai` 包用于调用兼容的 LLM 接口完成翻译，使用前需先安装：

```bash
pip install openai
```

## 使用方法

```bash
python paper_agent.py "查询主题" \
  --max-results 5 \
  --num-queries 3 \
  --per-query 5 \
  --api-key YOUR_API_KEY \
  --base-url https://api.deepseek.com \
  --model deepseek-chat
```

- `查询主题`：需要检索的论文主题关键词，例如 `LLM推理优化`。
- `--max-results`：最终输出的论文数量，默认 5 篇。
- `--num-queries`：由主题生成的检索子查询数量，默认 3 个。
- `--per-query`：每个子查询从 arXiv 检索的论文数量，默认 5 篇。
- `--api-key`：用于翻译的 LLM 服务 API Key。
- `--base-url`：可选参数，指定与 OpenAI 接口兼容的服务地址，例如 DeepSeek。
- `--model`：调用翻译 API 所用的模型名称，默认 `deepseek-chat`。

执行后脚本将输出包含论文标题、作者及机构、发表日期以及中文摘要的 JSON 列表。脚本会先利用 LLM 生成多条检索语句并对结果排序，内部会自动从回复中提取 JSON 数组，因此对模型回复中的附加文本具有一定容错能力。
