import json
import re


def _extract_json_array(text: str) -> list:
    """Extract the first JSON array found in text."""
    match = re.search(r"\[[\s\S]*\]", text)
    if not match:
        return []
    try:
        return json.loads(match.group(0))
    except Exception:
        return []


def print_results(results: dict[str, list]):
    """Prints the search queries and papers with color formatting."""
    BLUE = "\033[94m"
    ORANGE = "\033[33m"
    RESET = "\033[0m"
    SEPARATOR = "=" * 80

    print(f"{BLUE}Generated Search Queries:{RESET}")
    if results['queries']:
        for query in results['queries']:
            print(f"{BLUE}- {query}{RESET}")
    else:
        print(f"{BLUE}- (No queries generated){RESET}")
    print(SEPARATOR)

    papers_list = results['papers']
    if not papers_list:
        print(f"{ORANGE}No papers found for the given topic.{RESET}")
    else:
        print(f"{ORANGE}Papers:{RESET}")
        for i, paper in enumerate(papers_list):
            if i > 0:
                print(f"{ORANGE}{SEPARATOR}{RESET}")
            print(f"{ORANGE}Title: {paper['title']}{RESET}")
            authors = paper.get('authors', [])
            if isinstance(authors, list):
                print(f"{ORANGE}Authors: {', '.join(authors)}{RESET}")
            else:
                print(f"{ORANGE}Authors: {authors}{RESET}")
            print(f"{ORANGE}Published: {paper['published']}{RESET}")
            print(f"{ORANGE}Summary (CN): {paper['summary_cn']}{RESET}")