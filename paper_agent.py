import argparse
import json
import re
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

try:
    from openai import OpenAI
except Exception:  # pragma: no cover - openai not installed
    OpenAI = None


class LLMClient:
    def __init__(self, api_key: str, base_url: str, model: str):
        if OpenAI is None:
            raise RuntimeError(
                "OpenAI client is not installed. Please install it with `pip install openai`."
            )
        self.client = OpenAI(api_key=api_key, base_url=base_url)
        self.model = model

    def translate(self, text: str) -> str: # language parameter removed, hardcoded to Chinese
        """Translate English text to Chinese using an OpenAI-compatible API."""
        # Note: The original function was translate_to_chinese.
        # If generic translation is needed, the prompt and signature must change.
        prompt = f"请将以下英文翻译成中文：\n{text}"
        messages = [
            {"role": "system", "content": "You are a helpful translation assistant."},
            {"role": "user", "content": prompt},
        ]
        resp = self.client.chat.completions.create(model=self.model, messages=messages, stream=False)
        return resp.choices[0].message.content.strip()

    def generate_queries(self, topic: str, num_queries: int) -> list[str]:
        """Use an LLM to generate refined arXiv search queries."""
        prompt = (
            f"请根据用户提供的主题`{topic}`生成 {num_queries} 个更细粒度的英语检索关键词，"
            "用于在 arXiv 上搜索相关论文。请仅返回一个 JSON 数组，每个元素为一个查询字符串。"
        )
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt},
        ]
        resp = self.client.chat.completions.create(model=self.model, messages=messages, stream=False)
        text = resp.choices[0].message.content.strip()
        queries = _extract_json_array(text)
        if not queries:
            queries = [topic]
        return [q.strip() for q in queries if isinstance(q, str) and q.strip()]

    def rank_papers(self, papers: list[dict[str, object]], topic: str) -> list[dict[str, object]]:
        """Rank papers by relevance and quality using an LLM."""
        if not papers:
            return []
        titles = [p["title"] for p in papers]
        paper_list = "\n".join(f"{i+1}. {t}" for i, t in enumerate(titles))
        prompt = (
            "请按照与主题`{topic}`的相关度和论文质量对以下论文进行排序，"
            "只返回一个 JSON 数组，数组中的元素应为排序后的编号。\n" + paper_list
        )
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt},
        ]
        resp = self.client.chat.completions.create(model=self.model, messages=messages, stream=False)
        text = resp.choices[0].message.content.strip()
        order = _extract_json_array(text)
        if not order:
            order = list(range(1, len(papers) + 1))
        ranked = []
        for i in order:
            idx = int(i) - 1
            if 0 <= idx < len(papers):
                ranked.append(papers[idx])
        return ranked


def _extract_json_array(text: str) -> list:
    """Extract the first JSON array found in text."""
    match = re.search(r"\[[\s\S]*\]", text)
    if not match:
        return []
    try:
        return json.loads(match.group(0))
    except Exception:
        return []


def search_arxiv_query(query: str, max_results: int = 5):
    """Search arXiv for the latest papers with a raw query string."""
    encoded = urllib.parse.quote(query)
    url = (
        f"http://export.arxiv.org/api/query?search_query=all:{encoded}"
        f"&sortBy=submittedDate&sortOrder=descending&max_results={max_results}"
    )
    try:
        with urllib.request.urlopen(url) as resp:
            data = resp.read()
    except Exception:
        return []
    root = ET.fromstring(data)
    ns = {
        'arxiv': 'http://arxiv.org/schemas/atom',
    }
    papers = []
    for entry in root.findall('{http://www.w3.org/2005/Atom}entry'):
        title = entry.findtext('{http://www.w3.org/2005/Atom}title', '').strip()
        summary = entry.findtext('{http://www.w3.org/2005/Atom}summary', '').strip()
        published = entry.findtext('{http://www.w3.org/2005/Atom}published', '')
        authors = []
        for author in entry.findall('{http://www.w3.org/2005/Atom}author'):
            name = author.findtext('{http://www.w3.org/2005/Atom}name', '')
            affiliation = author.findtext('arxiv:affiliation', default='', namespaces=ns)
            if affiliation:
                authors.append(f"{name} ({affiliation})")
            else:
                authors.append(name)
        papers.append({'title': title, 'authors': authors, 'summary': summary, 'published': published})
    return papers


def translate_to_chinese(text: str, llm_client: LLMClient) -> str:
    """Translate English text to Chinese using an OpenAI-compatible API."""
    # OpenAI is None check is handled by LLMClient.__init__
    return llm_client.translate(text)


def generate_queries(topic: str, llm_client: LLMClient, num_queries: int = 3) -> list[str]:
    """Use an LLM to generate refined arXiv search queries."""
    # OpenAI is None check is handled by LLMClient.__init__
    return llm_client.generate_queries(topic, num_queries)


def rank_papers(
    papers: list[dict[str, object]], topic: str, llm_client: LLMClient
) -> list[dict[str, object]]:
    """Rank papers by relevance and quality using an LLM."""
    # OpenAI is None check is handled by LLMClient.__init__
    if not papers: # Keep the early exit for empty paper list
        return []
    return llm_client.rank_papers(papers, topic)


def build_paper_list(
    topic: str,
    llm_client: LLMClient, # Added llm_client
    max_results: int,
    # api_key, base_url, model removed
    num_queries: int = 3,
    per_query: int = 5,
) -> dict[str, list]:
    """Build a ranked list of papers with translated summaries."""
    queries = generate_queries(topic, llm_client, num_queries=num_queries) # Pass llm_client
    all_papers: list[dict[str, object]] = []
    seen = set()
    for q in queries:
        for p in search_arxiv_query(q, per_query):
            if p["title"] not in seen:
                seen.add(p["title"])
                all_papers.append(p)
    ranked = rank_papers(all_papers, topic, llm_client) # Pass llm_client
    result = []
    for paper in ranked[:max_results]:
        translated = translate_to_chinese(paper["summary"], llm_client) # Pass llm_client
        result.append(
            {
                "title": paper["title"],
                "authors": paper["authors"],
                "published": paper["published"],
                "summary_cn": translated,
            }
        )
    return {"queries": queries, "papers": result}


def main():
    parser = argparse.ArgumentParser(description='Retrieve recent arXiv papers.')
    parser.add_argument('topic', help='Topic to search for')
    parser.add_argument('--max-results', type=int, default=5, help='Number of papers to output')
    parser.add_argument('--num-queries', type=int, default=3, help='Number of queries generated from the topic')
    parser.add_argument('--per-query', type=int, default=5, help='Papers fetched for each query')
    parser.add_argument('--api-key', required=True, help='API key for LLM service') # Changed help text slightly
    parser.add_argument('--base-url', default=None, help='Base URL for OpenAI-compatible LLM API') # Changed help text slightly
    parser.add_argument('--model', default='deepseek-chat', help='Model name for the LLM API') # Changed help text slightly
    args = parser.parse_args()

    # Initialize LLMClient
    llm_client = LLMClient(api_key=args.api_key, base_url=args.base_url, model=args.model)

    results = build_paper_list(
        args.topic,
        llm_client, # Pass llm_client
        args.max_results,
        # api_key, base_url, model removed
        num_queries=args.num_queries,
        per_query=args.per_query,
    )

    print("Generated Search Queries:")
    if results['queries']:
        for query in results['queries']:
            print(f"- {query}")
    else:
        print("- (No queries generated)") # Handle case of no queries
    print("---")

    papers_list = results['papers']
    if not papers_list:
        print("No papers found for the given topic.")
    else:
        for i, paper in enumerate(papers_list):
            if i > 0:  # Add separator for subsequent papers
                print("---")
            print(f"Title: {paper['title']}")
            # Ensure authors is a list and join, handle if not a list (though it should be)
            authors = paper.get('authors', [])
            if isinstance(authors, list):
                print(f"Authors: {', '.join(authors)}")
            else: # Should not happen based on current code, but good for robustness
                print(f"Authors: {authors}")
            print(f"Published: {paper['published']}")
            print(f"Summary (CN): {paper['summary_cn']}")


if __name__ == '__main__':
    main()
