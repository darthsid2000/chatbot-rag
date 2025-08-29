from pathlib import Path
from typing import List
from dotenv import load_dotenv

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS

from settings import INDEX_DIR, XML_PATH
from utils_wiki import strip_wiki, normalize_title, iter_mediawiki_pages

load_dotenv()

def xml_to_documents(xml_path: str, min_len: int = 200) -> List[Document]:
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200, separators=["\n\n", "\n", " ", ""])
    docs: List[Document] = []
    skipped = 0
    for title, raw in iter_mediawiki_pages(xml_path):
        if not raw:
            continue
        clean = strip_wiki(raw)
        if not clean or len(clean) < min_len:
            skipped += 1
            continue
        t_norm = normalize_title(title)
        for i, chunk in enumerate(splitter.split_text(clean)):
            docs.append(Document(page_content=chunk, metadata={"source": "stormlight_fandom", "title": title, "title_norm": t_norm, "chunk_id": i}))
    print(f"[ingest] chunks={len(docs)} skipped={skipped}")
    return docs

def build_faiss_index(docs: List[Document]) -> None:
    embeddings = OpenAIEmbeddings(model="text-embedding-3-large")
    vectordb = FAISS.from_documents(docs, embedding=embeddings)
    Path(INDEX_DIR).mkdir(parents=True, exist_ok=True)
    vectordb.save_local(INDEX_DIR)
    print(f"[ingest] saved -> {INDEX_DIR}")

if __name__ == "__main__":
    build_faiss_index(xml_to_documents(XML_PATH))