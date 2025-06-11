import io
import unittest
from unittest.mock import patch
from paper_agent import print_results

# ANSI escape codes used in print_results
BLUE = "\033[94m"
GREEN = "\033[92m"
RESET = "\033[0m"
SEPARATOR = "=" * 80

class TestPaperAgentOutput(unittest.TestCase):

    def test_print_results_formatting(self):
        mock_results_data = {
            "queries": ["query1", "query2"],
            "papers": [
                {
                    "title": "Test Paper 1",
                    "authors": ["Author A", "Author B"],
                    "published": "2023-01-01",
                    "summary_cn": "测试总结1"
                },
                {
                    "title": "Test Paper 2",
                    "authors": ["Author C"],
                    "published": "2023-02-01",
                    "summary_cn": "测试总结2"
                }
            ]
        }

        # Capture stdout
        captured_output = io.StringIO()
        with patch('sys.stdout', new=captured_output):
            print_results(mock_results_data)

        output_str = captured_output.getvalue()

        # Check for "Generated Search Queries" section formatting
        self.assertIn(f"{BLUE}Generated Search Queries:{RESET}", output_str)
        self.assertIn(f"{BLUE}- query1{RESET}", output_str)
        self.assertIn(f"{BLUE}- query2{RESET}", output_str)

        # Check for "Papers" section header
        self.assertIn(f"{GREEN}Papers:{RESET}", output_str)

        # Check for paper 1 formatting
        self.assertIn(f"{GREEN}Title: Test Paper 1{RESET}", output_str)
        self.assertIn(f"{GREEN}Authors: Author A, Author B{RESET}", output_str)
        self.assertIn(f"{GREEN}Published: 2023-01-01{RESET}", output_str)
        self.assertIn(f"{GREEN}Summary (CN): 测试总结1{RESET}", output_str)

        # Check for separator between paper 1 and paper 2
        # The separator is printed *before* the second paper, so it will be GREEN + SEPARATOR + RESET
        # followed by GREEN + Title...
        self.assertIn(f"{GREEN}{SEPARATOR}{RESET}\n{GREEN}Title: Test Paper 2{RESET}", output_str)

        # Check for paper 2 formatting
        self.assertIn(f"{GREEN}Title: Test Paper 2{RESET}", output_str)
        self.assertIn(f"{GREEN}Authors: Author C{RESET}", output_str)
        self.assertIn(f"{GREEN}Published: 2023-02-01{RESET}", output_str)
        self.assertIn(f"{GREEN}Summary (CN): 测试总结2{RESET}", output_str)

    def test_print_results_no_queries(self):
        mock_results_data = {
            "queries": [],
            "papers": [
                {
                    "title": "Test Paper 1",
                    "authors": ["Author A"],
                    "published": "2023-01-01",
                    "summary_cn": "测试总结1"
                }
            ]
        }
        captured_output = io.StringIO()
        with patch('sys.stdout', new=captured_output):
            print_results(mock_results_data)
        output_str = captured_output.getvalue()

        self.assertIn(f"{BLUE}Generated Search Queries:{RESET}", output_str)
        self.assertIn(f"{BLUE}- (No queries generated){RESET}", output_str)
        self.assertIn(f"{GREEN}Title: Test Paper 1{RESET}", output_str) # Check paper is still printed

    def test_print_results_no_papers(self):
        mock_results_data = {
            "queries": ["query1"],
            "papers": []
        }
        captured_output = io.StringIO()
        with patch('sys.stdout', new=captured_output):
            print_results(mock_results_data)
        output_str = captured_output.getvalue()

        self.assertIn(f"{BLUE}- query1{RESET}", output_str)
        self.assertIn(f"{GREEN}No papers found for the given topic.{RESET}", output_str)

if __name__ == '__main__':
    unittest.main()
