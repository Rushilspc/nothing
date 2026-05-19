from langgraph.graph import END, StateGraph

from crag.nodes import generate, grade_documents, retrieve, transform_query, web_search
from crag.state import GraphState


def _route_after_grading(state: GraphState) -> str:
    return "transform_query" if state.get("web_search_needed") == "Yes" else "generate"


graph = StateGraph(GraphState)
graph.add_node("retrieve", retrieve)
graph.add_node("grade_documents", grade_documents)
graph.add_node("transform_query", transform_query)
graph.add_node("web_search", web_search)
graph.add_node("generate", generate)

graph.set_entry_point("retrieve")
graph.add_edge("retrieve", "grade_documents")
graph.add_conditional_edges(
    "grade_documents",
    _route_after_grading,
    {
        "transform_query": "transform_query",
        "generate": "generate",
    },
)
graph.add_edge("transform_query", "web_search")
graph.add_edge("web_search", "generate")
graph.add_edge("generate", END)

app_graph = graph.compile()
