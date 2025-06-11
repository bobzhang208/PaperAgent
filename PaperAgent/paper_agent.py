from tqdm import tqdm
from .llm import PaperAgentLLM
from .search_paper import search_arxiv_query
from .utils import print_results


def get_paper_list(
        topic: str,
        llm_client: PaperAgentLLM,  # Added llm_client
        max_results: int,
) -> dict[str, list]:
    print(f"Searching for papers on topic: {topic}")
    res = search_arxiv_query(topic, max_results=max_results)

    for i in range(len(res)):
        print(f"Paper {i + 1}: {res[i]['title']}")

    ranked = llm_client.rank_papers(res, topic)  # Pass llm_client

    result = []
    for paper in tqdm(ranked[:max_results], desc="Translating summaries"):
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


def paper_agent_main(
        topic: str,
        llm_client: PaperAgentLLM,  # Added llm_client
        max_results: int = 5,
):
    """
    Main function to retrieve and process recent arXiv papers on a given topic.

    Args:
        topic (str): The topic to search for.
        llm_client (LLMClient): An instance of LLMClient for LLM interactions.
        max_results (int): Maximum number of papers to return.
    """
    results = get_paper_list(topic, llm_client, max_results)
    print_results(results)
