from langchain_community.vectorstores import FAISS
from langchain_text_splitters import CharacterTextSplitter
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings
from sentence_transformers import SentenceTransformer
import json

# 1. Define a LangChain-compatible embedding class for SBERT
class SBertEmbeddings(Embeddings):
    def __init__(self, model_name="all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)
    def embed_documents(self, texts):
        return self.model.encode(texts, convert_to_numpy=True).tolist()
    def embed_query(self, text):
        return self.model.encode([text], convert_to_numpy=True)[0].tolist()

# 2. Load papers.json
with open("papers.json", "r", encoding="utf-8") as f:
    papers = json.load(f)

# 3. Prepare LangChain Document objects
docs = [
    Document(page_content=p["summary"], metadata={"title": p["title"], "url": p["url"]})
    for p in papers
]

# 4. Split long abstracts for better retrieval
splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=50)
split_docs = []
for doc in docs:
    chunks = splitter.split_text(doc.page_content)
    for c in chunks:
        split_docs.append(Document(page_content=c, metadata=doc.metadata))

# 5. Build FAISS vector store using SBert embeddings
embedding = SBertEmbeddings()
db = FAISS.from_documents(split_docs, embedding)

# 6. Example retrieval: user query
query = "What are recent innovations in multilingual NLP?"
results = db.similarity_search(query, k=3)
for r in results:
    print(r.metadata["title"], "\n", r.page_content, "\n", r.metadata["url"])
