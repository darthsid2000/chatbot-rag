from typing import List, Dict
from langchain.chat_models import init_chat_model
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain.retrievers.multi_query import MultiQueryRetriever
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser

from settings import INDEX_DIR, TOP_K, GOOGLE_API_KEY

if not GOOGLE_API_KEY:
    raise RuntimeError("GOOGLE_API_KEY or GEMINI_API_KEY not set.")

llm = init_chat_model("gemini-2.5-flash", model_provider="google_genai")

embeddings = OpenAIEmbeddings(model="text-embedding-3-large")
vectordb = FAISS.load_local(INDEX_DIR, embeddings, allow_dangerous_deserialization=True)
retriever = vectordb.as_retriever(search_kwargs={"k": TOP_K})
mq = MultiQueryRetriever.from_llm(retriever=retriever, llm=llm)

rewrite_prompt = ChatPromptTemplate.from_messages([
    ("system", "Rewrite the user question so it is self-contained."),
    MessagesPlaceholder("chat_history"),
    ("human", "Question: {question}\nRewrite:")
])
rewrite_chain = rewrite_prompt | llm | StrOutputParser()

qa_prompt = ChatPromptTemplate.from_messages([
    ("system", "Answer only from the provided context. If insufficient, say 'Insufficient context.' Ask a concise follow-up. Be brief. Cite sources as [Title]."),
    MessagesPlaceholder("chat_history"),
    ("human", "Question: {question}\n\nContext:\n{context}")
])
qa_chain = qa_prompt | llm | StrOutputParser()

_SESSIONS: Dict[str, List[Dict[str, str]]] = {}

def ask(session_id: str, question: str, k: int = TOP_K) -> Dict:
    hist = _SESSIONS.setdefault(session_id, [])
    q = rewrite_chain.invoke({"chat_history": hist, "question": question})
    docs = mq.invoke(q)

    ctx_blocks, sources = [], []
    for d in docs[:k]:
        title = d.metadata.get("title", "Unknown")
        ctx_blocks.append(f"[{title}]\n{d.page_content}")
        sources.append({"title": title, "chunk_id": d.metadata.get("chunk_id"), "source": d.metadata.get("source")})
    context = "\n\n".join(ctx_blocks)

    answer = qa_chain.invoke({"chat_history": hist, "question": question, "context": context})

    hist.append({"role": "user", "content": question})
    hist.append({"role": "assistant", "content": answer})
    if len(hist) > 12:
        del hist[: len(hist) - 12]

    return {"answer": answer, "sources": sources}