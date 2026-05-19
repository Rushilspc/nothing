from __future__ import annotations

import json
from typing import Any, Dict, List

from langchain_core.documents import Document
from tavily import TavilyClient

from crag.state import GraphState
from crag.vectorstore import load_vectorstore
from utils.helpers import get_tavily_client, run_gemini_prompt


def retrieve(state: GraphState) -> GraphState:
    trace = list(state.get("pipeline_trace", []))
    retriever = load_vectorstore()
    docs = retriever.invoke(state["question"])

    trace.append(f"🔍 Retrieved {len(docs)} documents")

    state["documents"] = docs
    state["pipeline_trace"] = trace
    return state


def grade_documents(state: GraphState) -> GraphState:
    question = state["question"]
    docs = state.get("documents", [])
    trace = list(state.get("pipeline_trace", []))

    grading_results: List[Dict[str, Any]] = []
    irrelevant_found = False

    for idx, doc in enumerate(docs, start=1):
        prompt = (
            f"Is this document relevant to the question: '{question}'? "
            "Answer only: YES or NO\n\n"
            f"Document:\n{doc.page_content}"
        )
        verdict = run_gemini_prompt(prompt).strip().upper()
        is_relevant = verdict.startswith("YES")
        if not is_relevant:
            irrelevant_found = True

        result = {
            "doc_index": idx,
            "verdict": "relevant" if is_relevant else "irrelevant",
            "raw": verdict,
        }
        grading_results.append(result)
        trace.append(f"🧪 Doc {idx} graded as {result['verdict']}")

    state["grading_results"] = grading_results
    state["web_search_needed"] = "Yes" if irrelevant_found else "No"
    trace.append(f"🧭 Web search needed: {state['web_search_needed']}")
    state["pipeline_trace"] = trace
    return state


def transform_query(state: GraphState) -> GraphState:
    question = state["question"]
    trace = list(state.get("pipeline_trace", []))
    prompt = f"Rewrite this query for better web search: '{question}'"
    new_query = run_gemini_prompt(prompt).strip()

    state["question"] = new_query
    trace.append(f"🔄 Query rewritten to: {new_query}")
    state["pipeline_trace"] = trace
    return state


def web_search(state: GraphState) -> GraphState:
    trace = list(state.get("pipeline_trace", []))
    client: TavilyClient = get_tavily_client()
    response = client.search(query=state["question"], max_results=4)

    results = response.get("results", [])
    new_docs = [
        Document(
            page_content=item.get("content") or item.get("snippet") or "",
            metadata={"url": item.get("url", "")},
        )
        for item in results
        if (item.get("content") or item.get("snippet"))
    ]

    state["documents"] = list(state.get("documents", [])) + new_docs
    trace.append(f"🌐 Web search returned {len(new_docs)} results")
    state["pipeline_trace"] = trace
    return state


def generate(state: GraphState) -> GraphState:
    trace = list(state.get("pipeline_trace", []))
    docs = state.get("documents", [])
    grading_results = state.get("grading_results", [])

    relevant_ids = {
        item["doc_index"]
        for item in grading_results
        if item.get("verdict") == "relevant"
    }

    selected_docs = [
        doc for idx, doc in enumerate(docs, start=1) if not relevant_ids or idx in relevant_ids
    ]
    context = "\n\n".join(doc.page_content for doc in selected_docs if doc.page_content)

    prompt = (
        "Answer the question based on this context:\n"
        f"{context}\n\n"
        f"Question: {state['question']}"
    )
    answer = run_gemini_prompt(prompt)

    state["generation"] = answer.strip()
    trace.append("✅ Answer generated")
    state["pipeline_trace"] = trace
    return state
