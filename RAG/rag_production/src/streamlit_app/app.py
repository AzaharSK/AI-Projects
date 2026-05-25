"""
Agentic RAG — Streamlit UI
Consumes the FastAPI microservice via api_client.py.
"""

from __future__ import annotations

import os
import time
from datetime import datetime
from typing import List

import streamlit as st
from src.streamlit_app.api_client import APIClient

# ── page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Agentic RAG",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── styling ───────────────────────────────────────────────────────────────────
st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display&family=DM+Sans:wght@300;400;500;600&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}

/* Header */
.rag-header {
    background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
    border-radius: 16px;
    padding: 2rem 2.5rem;
    margin-bottom: 1.5rem;
    display: flex;
    align-items: center;
    gap: 1.2rem;
}
.rag-header h1 {
    font-family: 'DM Serif Display', serif;
    color: #fff;
    font-size: 2.1rem;
    margin: 0;
    letter-spacing: -0.5px;
}
.rag-header p {
    color: #b8b8d0;
    margin: 0.25rem 0 0;
    font-size: 0.9rem;
}

/* Status badge */
.badge {
    display: inline-block;
    padding: 0.2rem 0.7rem;
    border-radius: 99px;
    font-size: 0.75rem;
    font-weight: 600;
    letter-spacing: 0.04em;
}
.badge-ok   { background: #22c55e22; color: #22c55e; border: 1px solid #22c55e55; }
.badge-warn { background: #f59e0b22; color: #f59e0b; border: 1px solid #f59e0b55; }
.badge-err  { background: #ef444422; color: #ef4444; border: 1px solid #ef444455; }

/* Answer card */
.answer-card {
    background: linear-gradient(135deg, #0f172a, #1e293b);
    border: 1px solid #334155;
    border-left: 4px solid #6366f1;
    border-radius: 12px;
    padding: 1.5rem 1.8rem;
    color: #e2e8f0;
    font-size: 0.97rem;
    line-height: 1.75;
    white-space: pre-wrap;
}

/* Source chip */
.source-chip {
    background: #1e293b;
    border: 1px solid #334155;
    border-radius: 8px;
    padding: 0.7rem 1rem;
    margin-bottom: 0.6rem;
    font-size: 0.82rem;
    color: #94a3b8;
    overflow-wrap: break-word;
}
.source-chip strong { color: #cbd5e1; }

/* Metric tile */
.metric-tile {
    background: #1e293b;
    border: 1px solid #334155;
    border-radius: 10px;
    padding: 1rem 1.2rem;
    text-align: center;
}
.metric-tile .val {
    font-size: 1.8rem;
    font-weight: 700;
    color: #a5b4fc;
    font-family: 'DM Serif Display', serif;
}
.metric-tile .lbl {
    font-size: 0.75rem;
    color: #64748b;
    margin-top: 0.2rem;
    text-transform: uppercase;
    letter-spacing: 0.06em;
}

/* History item */
.history-item {
    background: #0f172a;
    border: 1px solid #1e293b;
    border-radius: 10px;
    padding: 1rem 1.2rem;
    margin-bottom: 0.6rem;
}
.history-item .q { font-weight: 600; color: #e2e8f0; font-size: 0.88rem; }
.history-item .a { color: #94a3b8; font-size: 0.84rem; margin-top: 0.3rem; line-height: 1.5; }
.history-item .ts { color: #475569; font-size: 0.73rem; margin-top: 0.4rem; }

/* Sidebar tweaks */
section[data-testid="stSidebar"] {
    background: #0f172a;
}
</style>
""",
    unsafe_allow_html=True,
)


# ── session state defaults ────────────────────────────────────────────────────
def _init_state() -> None:
    defaults = {
        "history": [],
        "last_answer": None,
        "last_sources": [],
        "last_latency": None,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


_init_state()


# ── api client ────────────────────────────────────────────────────────────────
@st.cache_resource
def _client() -> APIClient:
    url = os.getenv("BACKEND_URL", "http://localhost:8000")
    return APIClient(base_url=url)


client = _client()


# ── header ────────────────────────────────────────────────────────────────────
st.markdown(
    """
<div class="rag-header">
  <div style="font-size:3rem">🧠</div>
  <div>
    <h1>Agentic RAG</h1>
    <p>Retrieval-Augmented Generation · ReAct Agent · LangGraph Pipeline</p>
  </div>
</div>
""",
    unsafe_allow_html=True,
)

# ── sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ⚙️ Configuration")

    # ── backend health ──
    st.markdown("### Backend Status")
    if st.button("🔄 Refresh Status"):
        st.cache_data.clear()

    try:
        health_data = client.health()
        ready = health_data.get("is_ready", False)
        status = health_data.get("status", "unknown")
        uptime = health_data.get("uptime_s", 0)
        badge_cls = "badge-ok" if ready else "badge-warn"
        st.markdown(
            f'<span class="badge {badge_cls}">● {status.upper()}</span>&nbsp;&nbsp;'
            f'<small style="color:#64748b">uptime {uptime:.0f}s</small>',
            unsafe_allow_html=True,
        )
    except Exception:
        st.markdown('<span class="badge badge-err">● UNREACHABLE</span>', unsafe_allow_html=True)
        st.warning("Cannot connect to backend. Is the FastAPI server running?")

    st.markdown("---")

    # ── ingest panel ──
    st.markdown("### 📥 Ingest Documents")
    st.caption("Add URLs, file paths, or PDF directories (one per line).")

    default_sources = "\n".join(
        [
            "https://lilianweng.github.io/posts/2023-06-23-agent/",
            "https://lilianweng.github.io/posts/2024-04-12-diffusion-video/",
        ]
    )
    sources_text = st.text_area(
        "Sources",
        value=default_sources,
        height=130,
        label_visibility="collapsed",
    )

    if st.button("⚡ Ingest", use_container_width=True):
        sources: List[str] = [s.strip() for s in sources_text.splitlines() if s.strip()]
        if not sources:
            st.error("Please enter at least one source.")
        else:
            with st.spinner(f"Ingesting {len(sources)} source(s) …"):
                try:
                    resp = client.ingest(sources)
                    st.success(
                        f"✅ {resp['chunks_created']} chunks from "
                        f"{resp['sources_processed']} source(s) in {resp['duration_s']:.1f}s"
                    )
                except Exception as exc:
                    st.error(f"Ingest failed: {exc}")

    st.markdown("---")

    # ── metrics panel ──
    st.markdown("### 📊 Live Metrics")
    try:
        m = client.metrics()
        vs = m.get("vectorstore", {})

        c1, c2 = st.columns(2)
        with c1:
            st.markdown(
                f'<div class="metric-tile"><div class="val">{m.get("query_count", 0)}</div>'
                f'<div class="lbl">Queries</div></div>',
                unsafe_allow_html=True,
            )
        with c2:
            st.markdown(
                f'<div class="metric-tile"><div class="val">{vs.get("chunk_count", 0)}</div>'
                f'<div class="lbl">Chunks</div></div>',
                unsafe_allow_html=True,
            )
        st.markdown(
            f'<div class="metric-tile" style="margin-top:0.5rem">'
            f'<div class="val">{m.get("avg_latency_ms", 0):.0f}ms</div>'
            f'<div class="lbl">Avg Latency</div></div>',
            unsafe_allow_html=True,
        )
    except Exception:
        st.caption("Metrics unavailable.")


# ── main area: two columns ────────────────────────────────────────────────────
col_q, col_hist = st.columns([3, 2], gap="large")

with col_q:
    st.markdown("### 💬 Ask a Question")

    question = st.text_area(
        "question_input",
        placeholder="What are the key components of LLM-powered autonomous agents?",
        height=110,
        label_visibility="collapsed",
    )

    ask_btn = st.button("🔍 Ask", use_container_width=True, type="primary")

    if ask_btn:
        q = question.strip()
        if not q:
            st.warning("Please enter a question.")
        else:
            with st.spinner("Thinking …"):
                try:
                    resp = client.query(q)
                    st.session_state.last_answer = resp["answer"]
                    st.session_state.last_sources = resp.get("sources", [])
                    st.session_state.last_latency = resp.get("latency_ms")
                    st.session_state.history.insert(
                        0,
                        {
                            "q": q,
                            "a": resp["answer"],
                            "ts": datetime.now().strftime("%H:%M:%S"),
                            "latency_ms": resp.get("latency_ms", 0),
                        },
                    )
                except RuntimeError as exc:
                    st.error(str(exc))
                except Exception as exc:
                    st.error(f"Query failed: {exc}")

    # ── answer display ──
    if st.session_state.last_answer:
        st.markdown("#### 💡 Answer")
        st.markdown(
            f'<div class="answer-card">{st.session_state.last_answer}</div>',
            unsafe_allow_html=True,
        )
        if st.session_state.last_latency:
            st.caption(f"⏱ {st.session_state.last_latency:.0f} ms")

        # sources
        sources = st.session_state.last_sources
        if sources:
            with st.expander(f"📄 Source passages ({len(sources)})", expanded=False):
                for i, src in enumerate(sources, 1):
                    meta = src.get("metadata", {})
                    label = meta.get("title") or meta.get("source") or f"Source {i}"
                    content_preview = src.get("content", "")[:300]
                    st.markdown(
                        f'<div class="source-chip"><strong>[{i}] {label}</strong><br>{content_preview}…</div>',
                        unsafe_allow_html=True,
                    )

with col_hist:
    st.markdown("### 📜 History")
    if not st.session_state.history:
        st.caption("Your questions will appear here.")
    else:
        if st.button("🗑 Clear", use_container_width=True):
            st.session_state.history = []
            st.session_state.last_answer = None
            st.session_state.last_sources = []
            st.rerun()

        for item in st.session_state.history[:15]:
            a_preview = item["a"][:160] + ("…" if len(item["a"]) > 160 else "")
            st.markdown(
                f"""<div class="history-item">
  <div class="q">Q: {item['q']}</div>
  <div class="a">{a_preview}</div>
  <div class="ts">{item['ts']} · {item['latency_ms']:.0f}ms</div>
</div>""",
                unsafe_allow_html=True,
            )
