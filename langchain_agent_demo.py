from langchain_community.llms import FakeListLLM
from langchain_core.tools import Tool
from retriever_demo import db

def retrieve_papers_tool(query):
    results = db.similarity_search(query, k=3)
    output = []
    for r in results:
        output.append(f"Title: {r.metadata['title']}\nSummary: {r.page_content}\nURL: {r.metadata['url']}")
    return "\n\n".join(output)

tool = Tool(
    name="PaperRetriever",
    func=retrieve_papers_tool,
    description="Retrieves academic papers relevant to a query."
)

question = "Explain recent advances in agentic retrieval."
tool_output = tool.run(question)

# Simulate agentic answer using FakeListLLM
fake_llm = FakeListLLM(responses=[
    f"Agent found these relevant papers:\n{tool_output}\n\nFinal Answer: Here is your cited summary."
])

print(fake_llm.invoke(question))
