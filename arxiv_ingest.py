import arxiv
import json

def fetch_papers(query="natural language processing", max_results=5):
    search = arxiv.Search(
        query=query,
        max_results=max_results,
        sort_by=arxiv.SortCriterion.SubmittedDate
    )
    papers = []
    for result in search.results():
        paper = {
            "title": result.title,
            "summary": result.summary,
            "url": result.entry_id,
            "authors": [author.name for author in result.authors],
            "published": result.published.isoformat()
        }
        papers.append(paper)
    with open("papers.json", "w", encoding="utf-8") as f:
        json.dump(papers, f, indent=2, ensure_ascii=False)
    return papers

if __name__ == "__main__":
    papers = fetch_papers()
    for p in papers:
        print(p["title"], "\n", p["summary"], "\n")
