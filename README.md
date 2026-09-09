# ZAIO Student Assistant — Multi-Source RAG API


## Architecture

```
                 ┌───────────────────┐        ┌───────────────────────┐
                 │  Student Handbook │        │     ZAIO Website       │
                 │      (PDF)        │        │  (crawled, cleaned)    │
                 └─────────┬─────────┘        └───────────┬────────────┘
                           │  pdf_loader.py                │  web_crawler.py
                           ▼                                ▼
                     ┌───────────────────────────────────────────┐
                     │           chunker.py (split_into_chunks)   │
                     └───────────────────┬─────────────────────────┘
                                          ▼
                     ┌───────────────────────────────────────────┐
                     │  vector_store.py                            │
                     │  - sentence-transformers embeddings         │
                     │  - ChromaDB (persistent, metadata: source,  │
                     │    page, url, display_source)               │
                     └───────────────────┬─────────────────────────┘
                                          ▲
                                          │ query embedding
                     ┌───────────────────┴─────────────────────────┐
   POST /ask  ──────▶│  rag.py: retrieve top-k, filter by relevance,│
   {question}        │  build context, call llm.py (Claude)          │
                     └───────────────────┬─────────────────────────┘
                                          ▼
                          { "answer": "...", "source": "..." }
```

## Project layout

```
zaio-rag-assistant/
├── app/
│   ├── config.py         # paths, chunk size, model names, thresholds
│   ├── pdf_loader.py      # Part 1: PDF text extraction (per page)
│   ├── web_crawler.py     # Part 1: crawl + clean ZAIO website
│   ├── chunker.py         # Part 1: text splitting
│   ├── vector_store.py    # Part 1/2: embeddings + ChromaDB
│   ├── llm.py             # Part 2: Claude-based grounded generation
│   └── rag.py             # Part 2: retrieval + relevance gating + answer
├── build_index.py         # Part 1: ingestion CLI (run this first)
├── main.py                 # Part 3/5: FastAPI app, POST /ask
├── data/
│   ├── handbook/Student_Handbook.pdf   # <- replace with the real handbook
│   ├── make_sample_handbook.py         # generates the placeholder above
│   ├── web_cache/                       # cached raw HTML (speeds up re-crawls)
│   └── chroma_db/                       # persistent vector DB (generated)
├── tests/
│   ├── test_cases.json     # Part 4: question bank (handbook/website/none)
│   ├── run_tests.py         # Part 4: hits the live API, writes a report
│   ├── test_results.md      # generated after running run_tests.py
│   └── test_results.json    # generated after running run_tests.py
├── n8n/
│   └── zaio_rag_workflow.json   # Part 5: importable n8n workflow
├── requirements.txt
└── .env.example
```

