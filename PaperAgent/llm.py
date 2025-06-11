from openai import OpenAI
from tqdm import tqdm


class LLM:
    def __init__(self, api_key: str, base_url: str, model: str):
        self.client = OpenAI(api_key=api_key, base_url=base_url)
        self.model = model

    def generate(self, prompt):
        """Generate text using the LLM."""
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt},
        ]
        resp = self.client.chat.completions.create(model=self.model, messages=messages, stream=False)
        return resp.choices[0].message.content.strip()


class PaperAgentLLM(LLM):
    def __init__(self, api_key: str, base_url: str, model: str = "gpt-3.5-turbo"):
        super().__init__(api_key, base_url, model)

    def translate(self, text: str) -> str:  # language parameter removed, hardcoded to Chinese
        """Translate English text to Chinese using an OpenAI-compatible API."""
        prompt = f"假设你是一名计算机专业的博士，请将以下英文翻译成中文：\n{text}, 除了翻译内容外不需要任何其他输出"
        return self.generate(prompt)  # Reuse the generate method for consistency

    def rank_papers(self, papers: list[dict[str, object]], topic: str) -> list[dict[str, object]]:
        def build_score_prompt(topic: str, title: str, summary: str) -> str:
            return (
                f"你是一名论文评估专家，请根据主题 `{topic}`，判断以下论文与该主题的相关性。\n\n"
                f"论文标题：{title}\n"
                f"论文摘要：{summary}\n\n"
                f"请你给出一个从 0 到 100 的相关性得分（越相关分数越高），"
                f"只输出一个整数，不要附加任何解释或文字。"
            )

        scored_papers = []
        for i, paper in enumerate(tqdm(papers, desc="Ranking papers")):
            prompt = build_score_prompt(topic, paper["title"], paper["summary"])
            score_text = self.generate(prompt).strip()
            try:
                score = int(score_text)
                if not (0 <= score <= 100):
                    raise ValueError
            except:
                score = 0  # 或者使用默认值/跳过等处理策略
            scored_papers.append((score, paper))

        scored_papers.sort(key=lambda x: -x[0])
        ranked_papers = [paper for _, paper in scored_papers]

        # for score, paper in scored_papers:
        #     print(f"{score}: {paper['title']}")
        return ranked_papers
