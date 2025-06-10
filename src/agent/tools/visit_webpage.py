from src.agent.utils.tooling import tool
from src.agent.utils.vector_store import chunk_content, load_in_vector_db



@tool
def visit_webpage(url: str) -> str:
    """
    Visits a webpage at the given URL and reads its content as a markdown string.
    This tool is useful for extracting information from web pages in a structured format after a search.
    Args:
        url (str): The URL of the webpage to visit.
    """
    try:
        from src.web2llm.app.scraper import scrape_url
        from src.web2llm.app.converter import html_to_markdown
        import re
        import requests
        from markdownify import markdownify
        from requests.exceptions import RequestException
        from smolagents.utils import truncate_content
        from urllib.parse import urlparse

    except ImportError as e:
        raise ImportError(
            f"You must install packages `markdownify` and `requests` to run this tool: for instance run `pip install markdownify requests` : {e}"
        ) from e

    forbidden_domains = ["universetoday.com"]

    parsed_url = urlparse(url)
    domain = parsed_url.netloc

    if domain in forbidden_domains:
        return "This domain is forbidden and cannot be accessed, please try another one."

    try:
        # Web2LLM app
        result = scrape_url(url, clean=True)
        markdown_content = html_to_markdown(result["clean_html"])

        load_in_vector_db(
            markdown_content,
            metadatas={
                "title": result["title"],
                "url": url,
            }
        )
        return "The webpage has been successfully visited: content has been vectorized and stored in the knowledge base."

    except requests.exceptions.Timeout:
        return "The request timed out. Please try again later or check the URL."

    except RequestException as e:
        return f"Error fetching the webpage: {str(e)}"

    except Exception as e:
        return f"An unexpected error occurred: {str(e)}"