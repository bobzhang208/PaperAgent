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
    GREEN = "\033[92m"
    RESET = "\033[0m"
    SEPARATOR = "=" * 80

    print(f"{BLUE}Generated Search Queries:{RESET}")
    if results['queries']:
        for query in results['queries']:
            print(f"{BLUE}- {query}{RESET}")
    else:
        print(f"{BLUE}- (No queries generated){RESET}")
    print(SEPARATOR)  # This separator can remain as is or be changed/removed if desired.

    papers_list = results['papers']
    if not papers_list:
        print(f"{GREEN}No papers found for the given topic.{RESET}")
    else:
        print(f"{GREEN}Papers:{RESET}")  # Adding a "Papers" header in green
        for i, paper in enumerate(papers_list):
            if i > 0:  # Add separator for subsequent papers
                print(f"{GREEN}{SEPARATOR}{RESET}")
            print(f"{GREEN}Title: {paper['title']}{RESET}")
            authors = paper.get('authors', [])
            if isinstance(authors, list):
                print(f"{GREEN}Authors: {', '.join(authors)}{RESET}")
            else:
                print(f"{GREEN}Authors: {authors}{RESET}")
            print(f"{GREEN}Published: {paper['published']}{RESET}")
            print(f"{GREEN}Summary (CN): {paper['summary_cn']}{RESET}")
