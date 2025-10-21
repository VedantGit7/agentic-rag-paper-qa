import streamlit as st
from retriever_demo import db
from langchain_core.tools import Tool
from ollama import Client
import random
import time

st.set_page_config(page_title="🧠 Agentic RAG Paper Q&A", page_icon="🤖", layout="wide", initial_sidebar_state="expanded")

# --- SIDEBAR ---
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/9/90/ArXiv_logo.png", width=90)
    st.title("Agentic RAG Demo 🤖📚")
    st.caption("Made by Vedant")
    st.markdown(
        """
        ### How this works
        - Enter any **research question** (AI, NLP, biomedical, agentic systems)
        - Results: synthesized, cited answer using real research papers from your dataset
        - Powered by local LLM, RAG, FAISS semantic search
        ---
        **Pro Tips:**
        - Try: `What is agentic retrieval?`\n
        - Try: `How is prompt optimization used in clinical AI?`\n
        - Try: `Research on continual learning in web agents?`
        """)
    st.markdown("---")
    st.markdown("**Theme:**")
    theme = st.radio("Choose your mode:", ["🌞 Light", "🌚 Dark"], key="theme")
    st.markdown("---")
    st.caption("App: v1.0")

if theme == "🌚 Dark":
    st.markdown("""
        <style>
            body {background-color: #222;}
            .stApp {background: linear-gradient(135deg,#0f2027,#2c5364);}
            .stTextInput, .stButton, .stForm {background: #222; color: #FAFAFA;}
            .stMarkdown {color: #FAFAFA;}
        </style>
        """, unsafe_allow_html=True)

# --- MAIN CHAT EXPERIENCE ---
st.markdown("<h1 style='margin-bottom:1rem;'>🧠 <span style='color:#2c5364;'>Agentic RAG Paper Q&A</span></h1>", unsafe_allow_html=True)
st.write("Ask your question about academic papers. Results are generated, referenced, and explained by the assistant.")

# Session history for chat
if 'chat_history' not in st.session_state: st.session_state.chat_history = []

# --- RETRIEVER TOOL ---
def retrieve_papers_tool(query, k=4):
    results = db.similarity_search(query, k=k)
    papers = []
    for r in results:
        papers.append({
            "title": r.metadata["title"],
            "summary": r.page_content,
            "url": r.metadata["url"]
        })
    return papers

tool = Tool(
    name="PaperRetriever", func=retrieve_papers_tool, description="Retrieves academic papers relevant to a query."
)

# --- CHAT FORM INPUT ---
with st.form("chat_form", clear_on_submit=True):
    user_input = st.text_input("Type your question...", placeholder="E.g., What's new in biomedical NLP?")
    submitted = st.form_submit_button("Send")

if submitted and user_input:
    with st.chat_message("user"):
        st.markdown(f"**You:** {user_input}")

    # Show animated loader while retrieving/generating
    with st.spinner("🔍 Searching papers and generating answer..."):
        time.sleep(random.uniform(0.5,1.2))  # Demo effect

        top_papers = tool.run(user_input)
        context = ""
        for idx, p in enumerate(top_papers, 1):
            context += f"\nPaper {idx}: {p['title']}\nSummary: {p['summary']}\nURL: {p['url']}"

        prompt = (
            f"You are an expert research assistant. Use the following papers to answer the question, referencing specific papers and summarizing clearly. "
            f"Include links and bold paper titles in results.\n"
            f"Question: {user_input}\nContext:{context}"
        )
        try:
            client = Client()
            llm_response = client.generate(model='mistral', prompt=prompt)['response']
        except Exception as ex:
            llm_response = "Error: Unable to connect to LLM server (ensure Ollama is running)."

        # Save to chat
        st.session_state.chat_history.append({
            'role': "user", 'content': user_input
        })
        st.session_state.chat_history.append({
            'role': "assistant", 'content': llm_response, 'papers': top_papers
        })

# --- DISPLAY FULL CHAT HISTORY ---
for idx, msg in enumerate(st.session_state.chat_history):
    avatar = "🧑" if msg["role"] == "user" else "🤖"
    st.chat_message(msg["role"], avatar=avatar).markdown(f"{msg['content']}")

    # Show best papers as clickable cards for assistant turns
    if msg["role"] == "assistant" and "papers" in msg:
        with st.expander("Top Papers Used", expanded=True):
            for p in msg["papers"]:
                st.markdown(f"""
                    <div style='background:#f0f6fc;padding:10px;border-radius:7px;margin-bottom:8px;'>
                        <b><a href="{p['url']}" target="_blank">{p['title']}</a></b>
                        <br><span style='color:#333;font-size:0.98rem'>{p['summary']}</span>
                    </div>
                """, unsafe_allow_html=True)

# --- FOOTER ---
st.markdown("<hr style='margin-top:2rem'><div style='text-align:center;font-size:0.9rem;color:#aaa;'>Built with LangChain, FAISS, Ollama, and Streamlit</div>", unsafe_allow_html=True)
