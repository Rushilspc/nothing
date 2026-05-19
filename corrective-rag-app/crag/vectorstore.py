from __future__ import annotations

from pathlib import Path
from typing import Iterable, List

from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings

INDEX_DIR = Path("faiss_index")
EMBEDDING_MODEL = "all-MiniLM-L6-v2"


def _embeddings() -> HuggingFaceEmbeddings:
    return HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)


def build_vectorstore(docs: List[str]) -> None:
    texts: Iterable[str] = [doc for doc in docs if doc and doc.strip()]
    documents = [Document(page_content=text) for text in texts]

    if not documents:
        raise ValueError("No valid text chunks found to index.")

    vectorstore = FAISS.from_documents(documents, _embeddings())
    INDEX_DIR.mkdir(parents=True, exist_ok=True)
    vectorstore.save_local(str(INDEX_DIR))


def load_vectorstore():
    if not INDEX_DIR.exists():
        raise FileNotFoundError(
            "FAISS index not found. Please upload PDFs and build the knowledge base first."
        )

    vectorstore = FAISS.load_local(
        str(INDEX_DIR),
        _embeddings(),
        allow_dangerous_deserialization=True,
    )
    return vectorstore.as_retriever(search_kwargs={"k": 4})
