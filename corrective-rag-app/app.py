from __future__ import annotations

import tempfile
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components
from pypdf import PdfReader

from crag.graph import app_graph
from crag.vectorstore import build_vectorstore

st.set_page_config(layout="wide", page_title="CRAG — Corrective RAG")


def extract_pdf_texts(uploaded_files) -> list[str]:
    texts = []
    for uploaded in uploaded_files:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(uploaded.getvalue())
            tmp_path = Path(tmp.name)
        reader = PdfReader(str(tmp_path))
        content = "\n".join([(page.extract_text() or "") for page in reader.pages]).strip()
        if content:
            texts.append(content)
        tmp_path.unlink(missing_ok=True)
    return texts


def render_architecture_tab() -> None:
    html = """
    <div style="background:#020617;color:#f1f5f9;padding:20px;border-radius:16px;font-family:Inter,Segoe UI,sans-serif;">
      <svg viewBox="0 0 1200 320" style="width:100%;height:auto;">
        <defs>
          <filter id="glow"><feGaussianBlur stdDeviation="3.5" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
          <marker id="arrowGray" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto"><path d="M0,0 L0,6 L9,3 z" fill="#64748b"/></marker>
          <marker id="arrowGreen" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto"><path d="M0,0 L0,6 L9,3 z" fill="#22c55e"/></marker>
          <marker id="arrowRed" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto"><path d="M0,0 L0,6 L9,3 z" fill="#ef4444"/></marker>
        </defs>
        <g id="nodes" fill-opacity="0">
          <rect x="20" y="110" rx="16" ry="16" width="150" height="64" fill="#1e293b" stroke="#3b82f6"/><text x="95" y="148" text-anchor="middle" fill="#f1f5f9">User Query</text>
          <rect x="210" y="110" rx="16" ry="16" width="170" height="64" fill="#1e293b" stroke="#3b82f6"/><text x="295" y="148" text-anchor="middle" fill="#f1f5f9">Retrieve Docs</text>
          <rect x="430" y="110" rx="16" ry="16" width="170" height="64" fill="#1e293b" stroke="#3b82f6"/><text x="515" y="148" text-anchor="middle" fill="#f1f5f9">Grade Docs</text>
          <polygon points="675,95 740,142 675,189 610,142" fill="#f59e0b" stroke="#f59e0b" filter="url(#glow)" class="pulse"/>
          <text x="675" y="147" text-anchor="middle" fill="#020617" font-weight="700">Decision</text>
          <rect x="810" y="40" rx="16" ry="16" width="210" height="64" fill="#1e293b" stroke="#3b82f6"/><text x="915" y="78" text-anchor="middle" fill="#f1f5f9">Rewrite + Web Search</text>
          <rect x="810" y="200" rx="16" ry="16" width="210" height="64" fill="#1e293b" stroke="#3b82f6"/><text x="915" y="238" text-anchor="middle" fill="#f1f5f9">Generate Answer</text>
        </g>
        <g id="lines" fill="none" stroke-width="3">
          <path class="line" d="M170 142 L210 142" stroke="#64748b" marker-end="url(#arrowGray)"/>
          <path class="line" d="M380 142 L430 142" stroke="#64748b" marker-end="url(#arrowGray)"/>
          <path class="line" d="M600 142 L610 142" stroke="#64748b" marker-end="url(#arrowGray)"/>
          <path class="line" d="M740 130 L810 72" stroke="#ef4444" marker-end="url(#arrowRed)"/>
          <path class="line" d="M740 154 L810 232" stroke="#22c55e" marker-end="url(#arrowGreen)"/>
        </g>
      </svg>
      <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:14px;margin-top:10px;">
        <div style="background:#0f172a;padding:12px;border-radius:12px;"><h4>Standard RAG</h4><p>Retrieve then generate directly. ❌ If retrieval is poor, answers can hallucinate.</p></div>
        <div style="background:#0f172a;padding:12px;border-radius:12px;"><h4>What CRAG Adds</h4><p>CRAG grades retrieved evidence and conditionally rewrites the query + triggers web fallback.</p></div>
        <div style="background:#0f172a;padding:12px;border-radius:12px;"><h4>Why It Matters</h4><p>Adaptive correction improves robustness and answer quality when local KB misses context.</p></div>
      </div>
      <div style="margin-top:12px;background:#0f172a;border-radius:12px;padding:14px;display:grid;grid-template-columns:1fr 1fr;gap:12px;">
        <div><h4>Standard RAG</h4><p>Query → Retrieve → Generate</p></div>
        <div><h4>CRAG</h4><p>Query → Retrieve → <span class="hl">Grade</span> → Decision → Generate / Web Fallback</p></div>
      </div>
    </div>
    <style>
      .line{stroke-dasharray:220;stroke-dashoffset:220;animation:draw 1.1s ease forwards;}
      #nodes > *{animation:fade .45s ease forwards;}
      #nodes > *:nth-child(1){animation-delay:.1s} #nodes > *:nth-child(2){animation-delay:.3s} #nodes > *:nth-child(3){animation-delay:.5s}
      #nodes > *:nth-child(4){animation-delay:.7s} #nodes > *:nth-child(5){animation-delay:.7s} #nodes > *:nth-child(6){animation-delay:.9s} #nodes > *:nth-child(7){animation-delay:1.1s}
      .pulse{animation:pulse 1.8s infinite ease-in-out;}
      .hl{background:#facc15;color:#111827;padding:1px 6px;border-radius:6px;animation:blink 1.2s infinite;}
      @keyframes draw {to{stroke-dashoffset:0;}}
      @keyframes fade {to{fill-opacity:1;opacity:1;}}
      @keyframes pulse {0%,100%{opacity:.8}50%{opacity:1;filter:brightness(1.1)}}
      @keyframes blink {0%,100%{box-shadow:0 0 0 rgba(250,204,21,0)}50%{box-shadow:0 0 16px rgba(250,204,21,.5)}}
    </style>
    """
    components.html(html, height=700)


def main():
    st.title("🧠 Corrective RAG (CRAG) with Gemini + FAISS")
    ask_tab, arch_tab = st.tabs(["💬 Ask CRAG", "🏗️ Architecture"])

    with ask_tab:
        left, right = st.columns([3, 7])

        with left:
            st.subheader("Upload & Index")
            uploads = st.file_uploader("Upload PDF files", type=["pdf"], accept_multiple_files=True)
            if st.button("Build Knowledge Base"):
                try:
                    if not uploads:
                        st.warning("Please upload at least one PDF before building the knowledge base.")
                    else:
                        texts = extract_pdf_texts(uploads)
                        build_vectorstore(texts)
                        st.success("Knowledge base built successfully and saved to ./faiss_index/")
                except Exception as exc:
                    st.error(f"Failed to build knowledge base: {exc}")

        with right:
            st.subheader("Chat")
            question = st.text_input("Ask a question")
            if st.button("Ask"):
                try:
                    if not question.strip():
                        st.warning("Please enter a question.")
                    else:
                        state = app_graph.invoke({"question": question, "pipeline_trace": []})
                        st.success(state.get("generation", "No answer generated."))

                        grading = state.get("grading_results", [])
                        relevant = sum(1 for g in grading if g.get("verdict") == "relevant")
                        irrelevant = sum(1 for g in grading if g.get("verdict") == "irrelevant")
                        st.caption(
                            f"Web search triggered: {state.get('web_search_needed', 'No')} | "
                            f"Relevant docs: {relevant} | Irrelevant docs: {irrelevant}"
                        )

                        with st.expander("🔍 Pipeline Trace", expanded=True):
                            for step in state.get("pipeline_trace", []):
                                st.write(step)
                except FileNotFoundError as exc:
                    st.info(str(exc))
                except Exception as exc:
                    st.error(f"Request failed: {exc}")

    with arch_tab:
        render_architecture_tab()


if __name__ == "__main__":
    main()
