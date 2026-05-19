from typing import List, TypedDict

from langchain_core.documents import Document


class GraphState(TypedDict, total=False):
    question: str
    documents: List[Document]
    generation: str
    web_search_needed: str
    grading_results: List[dict]
    pipeline_trace: List[str]
