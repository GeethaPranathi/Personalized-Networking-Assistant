"""
streamlit_app.py
----------------
Full-featured Streamlit frontend for the Personalized Network Assistant.

This version calls service functions DIRECTLY (no FastAPI backend required),
making it fully deployable on Streamlit Cloud as a standalone app.

Sections:
  1. Sidebar — User profile (name + interests)
  2. Main — Event description input + Generate button
  3. Results — Conversation starters with 👍/👎 feedback
  4. Fact-Check — Wikipedia lookup widget
  5. History — Expandable previous conversation sessions
  6. Feedback History — Table of all recorded feedback
  7. Session state management for caching and UI coordination
"""

import os
import sys

# ---------------------------------------------------------------------------
# Critical: Add the project root to sys.path so that 'app.services' can be
# imported from the frontend/ subdirectory regardless of the working directory
# from which 'streamlit run' is invoked.
# ---------------------------------------------------------------------------
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st

# ---------------------------------------------------------------------------
# Page configuration (must be first Streamlit call)
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Network Assistant",
    page_icon="🤝",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# Custom CSS — premium dark glassmorphism design
# ---------------------------------------------------------------------------
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    /* ── Dark background ── */
    .stApp {
        background: linear-gradient(135deg, #0f0c29 0%, #1a1a3e 50%, #24243e 100%);
        min-height: 100vh;
    }

    /* ── Force White text and labels for visibility ── */
    p, span, label, h1, h2, h3, h4, h5, h6, .stSubheader, .stTitle, [data-testid="stWidgetLabel"] p {
        color: #ffffff !important;
    }
    
    .stMarkdown div, .stMarkdown p {
        color: #f1f5f9 !important;
    }

    /* ── Tabs Visibility ── */
    button[data-baseweb="tab"] p {
        color: rgba(255, 255, 255, 0.6) !important;
        font-weight: 500 !important;
    }
    button[data-baseweb="tab"][aria-selected="true"] p {
        color: #ffffff !important;
        font-weight: 700 !important;
    }

    /* ── Hero banner ── */
    .hero-banner {
        background: linear-gradient(135deg, rgba(102,126,234,0.25) 0%, rgba(118,75,162,0.25) 100%);
        border: 1px solid rgba(255,255,255,0.1);
        border-radius: 20px;
        padding: 2rem 2.5rem;
        margin-bottom: 2rem;
        backdrop-filter: blur(12px);
        text-align: center;
    }
    .hero-banner h1 {
        color: #ffffff !important;
        font-size: 2.4rem;
        font-weight: 700;
        margin: 0 0 0.5rem 0;
        background: linear-gradient(90deg, #a78bfa, #60a5fa, #34d399);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .hero-banner p {
        color: rgba(255,255,255,0.8) !important;
        font-size: 1.05rem;
        margin: 0;
    }

    /* ── Glass cards ── */
    .glass-card {
        background: rgba(255,255,255,0.05);
        border: 1px solid rgba(255,255,255,0.1);
        border-radius: 16px;
        padding: 1.5rem;
        backdrop-filter: blur(10px);
        margin-bottom: 1.2rem;
    }

    /* ── Starter cards ── */
    .starter-card {
        background: linear-gradient(135deg, rgba(102,126,234,0.15) 0%, rgba(118,75,162,0.15) 100%);
        border: 1px solid rgba(167,139,250,0.3);
        border-radius: 14px;
        padding: 1.2rem 1.5rem;
        margin: 0.6rem 0;
        color: #e2e8f0 !important;
        font-size: 0.97rem;
        line-height: 1.6;
        transition: all 0.2s ease;
    }
    .starter-card:hover {
        border-color: rgba(167,139,250,0.7);
        transform: translateX(4px);
    }

    /* ── Theme badges ── */
    .theme-badge {
        display: inline-block;
        background: linear-gradient(90deg, #7c3aed, #2563eb);
        color: white !important;
        font-size: 0.78rem;
        font-weight: 600;
        padding: 0.25rem 0.75rem;
        border-radius: 999px;
        margin: 0.2rem 0.2rem 0.2rem 0;
        letter-spacing: 0.03em;
    }

    /* ── Fact-check box ── */
    .fact-box {
        background: rgba(16,185,129,0.08);
        border: 1px solid rgba(52,211,153,0.3);
        border-radius: 12px;
        padding: 1.2rem;
        color: #a7f3d0 !important;
        font-size: 0.93rem;
        line-height: 1.7;
    }

    /* ── Section headings ── */
    .section-heading {
        color: #a78bfa !important;
        font-size: 1.15rem;
        font-weight: 600;
        margin: 1.5rem 0 0.75rem 0;
        border-bottom: 1px solid rgba(167,139,250,0.2);
        padding-bottom: 0.4rem;
    }

    /* ── Sidebar polish ── */
    section[data-testid="stSidebar"] {
        background: rgba(15,12,41,0.9) !important;
        border-right: 1px solid rgba(255,255,255,0.08);
    }

    /* ── Inputs & textareas (Baseweb overrides) ── */
    div[data-baseweb="input"] input, div[data-baseweb="textarea"] textarea {
        background-color: rgba(255, 255, 255, 0.08) !important;
        color: #ffffff !important;
        border-radius: 10px !important;
    }
    
    /* Input/textarea placeholders */
    div[data-baseweb="input"] input::placeholder, div[data-baseweb="textarea"] textarea::placeholder {
        color: rgba(255, 255, 255, 0.5) !important;
    }

    /* ── Buttons ── */
    .stButton > button {
        background: linear-gradient(135deg, #7c3aed, #2563eb) !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        font-weight: 600 !important;
        transition: all 0.2s ease !important;
        padding: 0.5rem 1.5rem !important;
    }
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 25px rgba(124,58,237,0.4) !important;
    }

    /* ── Status messages ── */
    .success-msg {
        background: rgba(16,185,129,0.15);
        border: 1px solid rgba(52,211,153,0.4);
        border-radius: 10px;
        padding: 0.75rem 1rem;
        color: #6ee7b7 !important;
        font-size: 0.9rem;
    }
    .error-msg {
        background: rgba(239,68,68,0.12);
        border: 1px solid rgba(239,68,68,0.35);
        border-radius: 10px;
        padding: 0.75rem 1rem;
        color: #fca5a5 !important;
        font-size: 0.9rem;
    }

    /* ── Metrics ── */
    [data-testid="metric-container"] {
        background: rgba(255,255,255,0.05) !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
        border-radius: 12px !important;
        padding: 1rem !important;
    }

    /* ── Divider ── */
    hr {
        border-color: rgba(255,255,255,0.08) !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Lazy-load services (imported here to avoid errors before sys.path is set)
# ---------------------------------------------------------------------------
@st.cache_resource(show_spinner="⚙️ Loading AI models (first run only)…")
def _load_services():
    """Load and cache the ML services — called once per Streamlit session."""
    from app.services.event_analyzer import extract_event_themes
    from app.services.topic_generator import generate_topics
    from app.services.fact_checker import fact_check
    from app.services.feedback_logger import log_feedback, load_feedback
    from app.services.history_logger import log_conversation, load_history
    return {
        "extract_event_themes": extract_event_themes,
        "generate_topics": generate_topics,
        "fact_check": fact_check,
        "log_feedback": log_feedback,
        "load_feedback": load_feedback,
        "log_conversation": log_conversation,
        "load_history": load_history,
    }


svc = _load_services()

# ---------------------------------------------------------------------------
# Session state initialisation
# ---------------------------------------------------------------------------
defaults = {
    "generated": False,
    "themes": [],
    "starters": [],
    "feedback_given": {},   # {starter_text: 'like'|'dislike'}
    "history_cache": None,
    "feedback_cache": None,
}
for key, val in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = val

# ---------------------------------------------------------------------------
# Hero banner
# ---------------------------------------------------------------------------
st.markdown(
    """
    <div class="hero-banner">
        <h1>🤝 Personalized Network Assistant</h1>
        <p>AI-powered conversation starters tailored to your next networking event</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ===========================================================================
# SIDEBAR — User Profile
# ===========================================================================
with st.sidebar:
    st.markdown("## 👤 Your Profile")
    st.markdown("---")

    user_name = st.text_input(
        "Full Name",
        placeholder="e.g. Alex Johnson",
        key="user_name_input",
    )

    interests_raw = st.text_area(
        "Professional Interests",
        placeholder="e.g. machine learning, fintech, product design",
        help="Separate interests with commas",
        height=120,
        key="interests_input",
    )
    interests = [i.strip() for i in interests_raw.split(",") if i.strip()]

    st.markdown("---")
    st.markdown("### 📊 Session Stats")

    col_a, col_b = st.columns(2)
    with col_a:
        st.metric("Starters", len(st.session_state.starters))
    with col_b:
        st.metric("Feedback", len(st.session_state.feedback_given))

    st.markdown("---")
    st.markdown(
        "<small style='color:rgba(255,255,255,0.4)'>Powered by DistilBERT + GPT-2</small>",
        unsafe_allow_html=True,
    )

# ===========================================================================
# MAIN AREA — Tabs
# ===========================================================================
tab_generate, tab_factcheck, tab_history, tab_feedback = st.tabs(
    ["✨ Generate", "🔍 Fact-Check", "📖 History", "📋 Feedback Log"]
)

# ---------------------------------------------------------------------------
# TAB 1 — Generate conversation starters
# ---------------------------------------------------------------------------
with tab_generate:
    st.markdown('<p class="section-heading">📝 Event Description</p>', unsafe_allow_html=True)

    event_description = st.text_area(
        "Describe the networking event",
        placeholder=(
            "e.g. A tech summit bringing together founders and investors to discuss "
            "the future of AI in healthcare and sustainable finance..."
        ),
        height=160,
        key="event_description_input",
        label_visibility="collapsed",
    )

    generate_btn = st.button("🚀 Generate Conversation Starters", use_container_width=True)

    if generate_btn:
        # Input validation
        if not user_name.strip():
            st.markdown(
                '<div class="error-msg">⚠️ Please enter your name in the sidebar.</div>',
                unsafe_allow_html=True,
            )
        elif not interests:
            st.markdown(
                '<div class="error-msg">⚠️ Please add at least one professional interest in the sidebar.</div>',
                unsafe_allow_html=True,
            )
        elif len(event_description.strip()) < 10:
            st.markdown(
                '<div class="error-msg">⚠️ Please provide a more detailed event description (min 10 characters).</div>',
                unsafe_allow_html=True,
            )
        else:
            try:
                with st.spinner("🤖 Analysing event themes with DistilBERT…"):
                    themes = svc["extract_event_themes"](event_description.strip())

                with st.spinner("✍️ Generating conversation starters with GPT-2…"):
                    starters = svc["generate_topics"](themes, interests)

                # Persist to history
                svc["log_conversation"]({
                    "user_name": user_name.strip(),
                    "event_description": event_description.strip(),
                    "themes": themes,
                    "starters": starters,
                })

                st.session_state.generated = True
                st.session_state.themes = themes
                st.session_state.starters = starters
                st.session_state.feedback_given = {}
                st.session_state.history_cache = None  # invalidate cache
                st.markdown(
                    '<div class="success-msg">✅ Conversation starters generated successfully!</div>',
                    unsafe_allow_html=True,
                )
            except Exception as exc:
                st.error(f"❌ Error generating starters: {exc}")

    # ── Results display ──
    if st.session_state.generated and st.session_state.starters:
        st.markdown('<p class="section-heading">🏷️ Detected Themes</p>', unsafe_allow_html=True)
        themes_html = "".join(
            f'<span class="theme-badge">{t}</span>' for t in st.session_state.themes
        )
        st.markdown(f'<div class="glass-card">{themes_html}</div>', unsafe_allow_html=True)

        st.markdown('<p class="section-heading">💬 Conversation Starters</p>', unsafe_allow_html=True)

        for idx, starter in enumerate(st.session_state.starters):
            with st.container():
                st.markdown(
                    f'<div class="starter-card">💡 {starter}</div>',
                    unsafe_allow_html=True,
                )
                col_like, col_dislike, col_copy = st.columns([1, 1, 4])

                fb_status = st.session_state.feedback_given.get(starter)

                with col_like:
                    liked = fb_status == "like"
                    if st.button(
                        "👍 Like" if not liked else "✅ Liked",
                        key=f"like_{idx}",
                        disabled=fb_status is not None,
                    ):
                        try:
                            svc["log_feedback"](starter, "like")
                            st.session_state.feedback_given[starter] = "like"
                            st.session_state.feedback_cache = None
                            st.rerun()
                        except Exception as exc:
                            st.error(f"Failed to save feedback: {exc}")

                with col_dislike:
                    disliked = fb_status == "dislike"
                    if st.button(
                        "👎 Dislike" if not disliked else "❌ Disliked",
                        key=f"dislike_{idx}",
                        disabled=fb_status is not None,
                    ):
                        try:
                            svc["log_feedback"](starter, "dislike")
                            st.session_state.feedback_given[starter] = "dislike"
                            st.session_state.feedback_cache = None
                            st.rerun()
                        except Exception as exc:
                            st.error(f"Failed to save feedback: {exc}")

        st.markdown("---")
        st.caption(
            "💾 This session has been automatically saved to your conversation history."
        )

# ---------------------------------------------------------------------------
# TAB 2 — Fact-Check
# ---------------------------------------------------------------------------
with tab_factcheck:
    st.markdown('<p class="section-heading">🔍 Wikipedia Fact-Check</p>', unsafe_allow_html=True)
    st.markdown(
        "<p style='color:rgba(255,255,255,0.6);font-size:0.93rem;'>Enter any topic, technology, or concept "
        "to fetch its Wikipedia summary in real time.</p>",
        unsafe_allow_html=True,
    )

    fc_query = st.text_input(
        "Query",
        placeholder="e.g. Large Language Models, Blockchain, DistilBERT…",
        key="fact_check_query",
        label_visibility="collapsed",
    )
    fc_btn = st.button("🔎 Look Up on Wikipedia", key="fact_check_btn", use_container_width=True)

    if fc_btn and fc_query.strip():
        with st.spinner("Fetching Wikipedia summary…"):
            try:
                result = svc["fact_check"](fc_query.strip())
                st.markdown(
                    f'<div class="fact-box"><strong>📖 {fc_query.strip()}</strong><br><br>{result}</div>',
                    unsafe_allow_html=True,
                )
            except Exception as exc:
                st.error(f"Fact-check failed: {exc}")
    elif fc_btn:
        st.warning("Please enter a query first.")

# ---------------------------------------------------------------------------
# TAB 3 — Conversation History
# ---------------------------------------------------------------------------
with tab_history:
    st.markdown('<p class="section-heading">📖 Previous Conversations</p>', unsafe_allow_html=True)

    refresh_history = st.button("🔄 Refresh History", key="refresh_history")

    if refresh_history or st.session_state.history_cache is None:
        try:
            st.session_state.history_cache = svc["load_history"]() or []
        except Exception:
            st.session_state.history_cache = []

    history = st.session_state.history_cache or []

    if not history:
        st.info("No conversation history yet. Generate some starters first!")
    else:
        st.markdown(
            f"<p style='color:rgba(255,255,255,0.5);font-size:0.85rem;'>{len(history)} session(s) on record.</p>",
            unsafe_allow_html=True,
        )
        for i, entry in enumerate(reversed(history), 1):
            ts = entry.get("timestamp", "Unknown time")
            name = entry.get("user_name", "Unknown user")
            themes = entry.get("themes", [])
            starters = entry.get("starters", [])
            desc_preview = entry.get("event_description", "")[:80]

            with st.expander(f"Session {len(history) - i + 1} — {name} · {ts[:10]}"):
                st.markdown(f"**👤 User:** {name}")
                st.markdown(f"**🕒 Time:** {ts}")
                st.markdown(f"**📝 Event:** {desc_preview}{'…' if len(entry.get('event_description','')) > 80 else ''}")
                themes_html = "".join(f'<span class="theme-badge">{t}</span>' for t in themes)
                st.markdown(f"**🏷️ Themes:** {themes_html}", unsafe_allow_html=True)
                st.markdown("**💬 Starters:**")
                for s in starters:
                    st.markdown(f"- {s}")

# ---------------------------------------------------------------------------
# TAB 4 — Feedback History
# ---------------------------------------------------------------------------
with tab_feedback:
    st.markdown('<p class="section-heading">📋 Feedback Log</p>', unsafe_allow_html=True)

    refresh_fb = st.button("🔄 Refresh Feedback Log", key="refresh_feedback")

    if refresh_fb or st.session_state.feedback_cache is None:
        try:
            st.session_state.feedback_cache = svc["load_feedback"]() or []
        except Exception:
            st.session_state.feedback_cache = []

    feedback = st.session_state.feedback_cache or []

    if not feedback:
        st.info("No feedback recorded yet. Rate some conversation starters first!")
    else:
        # Summary metrics
        likes = sum(1 for f in feedback if f.get("action") == "like")
        dislikes = len(feedback) - likes

        m1, m2, m3 = st.columns(3)
        m1.metric("Total Feedback", len(feedback))
        m2.metric("👍 Likes", likes)
        m3.metric("👎 Dislikes", dislikes)

        st.markdown("---")

        for entry in reversed(feedback):
            action_icon = "👍" if entry.get("action") == "like" else "👎"
            ts = entry.get("timestamp", "")[:16].replace("T", " ")
            suggestion = entry.get("suggestion", "")
            with st.container():
                st.markdown(
                    f'<div class="glass-card">'
                    f'<span style="font-size:1.2rem">{action_icon}</span> '
                    f'<span style="color:#a78bfa;font-size:0.78rem">{ts}</span><br>'
                    f'<span style="color:#e2e8f0;font-size:0.93rem">{suggestion}</span>'
                    f'</div>',
                    unsafe_allow_html=True,
                )
