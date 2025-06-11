import argparse
from PaperAgent import paper_agent_main, PaperAgentLLM


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
    llm_client = PaperAgentLLM(api_key=args.api_key, base_url=args.base_url, model=args.model)
    paper_agent_main(
        topic=args.topic,
        llm_client=llm_client,
        max_results=args.max_results
    )


if __name__ == '__main__':
    main()
