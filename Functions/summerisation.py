from googlesearch import search
from bs4 import BeautifulSoup
from summarizer import Summarizer
import requests

def google_search(query, num_results=5):
    search_results = list(search(query, num_results=num_results))
    return search_results

def get_page_content(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"Error fetching page content: {e}")
        return None

def summarize_text(text):
    summarizer = Summarizer()
    summary = summarizer(text, min_length=50, max_length=200)
    return summary

if __name__ == "__main__":
    user_query = input("Enter your query: ")

    search_results = google_search(user_query)
    if search_results:
        best_result_url = search_results[0]

        page_content = get_page_content(best_result_url)
        if page_content:
            soup = BeautifulSoup(page_content, 'html.parser')
            visible_text = soup.get_text()

            summary = summarize_text(visible_text)
            print("\nSummary:")
            print(summary)
        else:
            print("Could not fetch page content.")
    else:
        print("No search results found.")
