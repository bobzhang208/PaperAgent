import arxiv


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
