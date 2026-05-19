# Corrective RAG Streamlit App

Corrective RAG (CRAG) is an adaptive retrieval-augmented generation workflow that checks document relevance before final answer generation. When retrieval quality is weak, CRAG rewrites the query and falls back to web search, then regenerates with improved context.

## Architecture (text description)
The app runs a LangGraph state machine: user query → retrieve from FAISS → grade each document with Gemini → conditional decision. If evidence is weak, the query is rewritten and Tavily search augments context; otherwise, generation proceeds directly. Finally, Gemini produces the answer from refined context.

## Setup
1. Clone this repository.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Copy `.env.example` to `.env` and add your keys:
   - `GEMINI_API_KEY`
   - `TAVILY_API_KEY`
4. Run the app:
   ```bash
   streamlit run app.py
   ```

## How to use
- **💬 Ask CRAG tab**:
  1. Upload one or more PDFs.
  2. Click **Build Knowledge Base**.
  3. Ask a question and click **Ask**.
  4. Inspect the generated answer and pipeline trace.
- **🏗️ Architecture tab**:
  - Explore the animated CRAG flow diagram and side-by-side CRAG vs Standard RAG explanation.
