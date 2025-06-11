import argparse
import arxiv

from llm import LLMClient
from utils import print_results


def search_arxiv_query(query: str, max_results: int = 5, search_mode: str = "latest"):
    # 查询关键词
    foramt_query = f"((ti:{query} OR abs:{query}) AND cat:cs*)"
    search = arxiv.Search(
        query=foramt_query,
        max_results=max_results * 10,
        sort_by=arxiv.SortCriterion.SubmittedDate if search_mode == "latest" else arxiv.SortCriterion.Relevance,
    )

    client = arxiv.Client()
    results = client.results(search)

    papers = []
    for result in results:
        paper = {
            "title": result.title,
            "authors": [author.name for author in result.authors],
            "summary": result.summary,
            "published": result.published,
            "link": result.entry_id
        }
        papers.append(paper)

    return papers


def build_paper_list(
        topic: str,
        llm_client: LLMClient,  # Added llm_client
        max_results: int,
) -> dict[str, list]:
    print(f"Searching for papers on topic: {topic}")
    res = search_arxiv_query(topic, max_results=max_results)

    for i in range(len(res)):
        print(f"Paper {i + 1}: {res[i]['title']}")

    ranked = llm_client.rank_papers(res, topic)  # Pass llm_client

    result = []
    for paper in ranked[:max_results]:
        translated = llm_client.translate(paper["summary"])  # Pass llm_client
        result.append(
            {
                "title": paper["title"],
                "authors": paper["authors"],
                "published": paper["published"],
                "summary_cn": translated,
            }
        )
    return {"queries": [topic], "papers": result}


def main():
    parser = argparse.ArgumentParser(description='Retrieve recent arXiv papers.')
    parser.add_argument('topic', help='Topic to search for')
    parser.add_argument('--max-results', type=int, default=5, help='Number of papers to output')
    parser.add_argument('--api-key', required=True, help='API key for LLM service')  # Changed help text slightly
    parser.add_argument('--base-url', default=None,
                        help='Base URL for OpenAI-compatible LLM API')  # Changed help text slightly
    parser.add_argument('--model', default='deepseek-chat',
                        help='Model name for the LLM API')  # Changed help text slightly
    args = parser.parse_args()

    # Initialize LLMClient
    llm_client = LLMClient(api_key=args.api_key, base_url=args.base_url, model=args.model)

    results = build_paper_list(
        args.topic,
        llm_client,  # Pass llm_client
        args.max_results,
    )

    print_results(results)


if __name__ == '__main__':
    main()
