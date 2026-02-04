#!/usr/bin/env python3
"""Command-line profile search using Exa.ai"""

import os
import sys
from dotenv import load_dotenv
from exa_py import Exa

load_dotenv()

def search_profiles(query: str, num_results: int = 10):
    """Search for profiles using Exa.ai's people search."""
    api_key = os.getenv("EXA_API_KEY")
    if not api_key:
        print("Error: EXA_API_KEY not set. Create a .env file with your API key.")
        sys.exit(1)

    exa = Exa(api_key=api_key)

    print(f"\nSearching for: {query}")
    print("-" * 50)

    try:
        response = exa.search(
            query=query,
            category="people",
            num_results=num_results
        )

        if not response.results:
            print("No profiles found.")
            return

        print(f"Found {len(response.results)} profiles:\n")

        for i, result in enumerate(response.results, 1):
            print(f"{i}. {result.title or 'Untitled'}")
            print(f"   URL: {result.url}")
            snippet = getattr(result, 'snippet', None) or getattr(result, 'text', None)
            if snippet:
                snippet = snippet[:200] + "..." if len(snippet) > 200 else snippet
                print(f"   {snippet}")
            print()

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python search_cli.py <query>")
        print('Example: python search_cli.py "VP of Engineering at fintech startups"')
        sys.exit(1)

    query = " ".join(sys.argv[1:])
    search_profiles(query)
