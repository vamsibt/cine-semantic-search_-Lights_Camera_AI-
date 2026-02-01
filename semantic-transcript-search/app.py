import os
import streamlit as st
from semantic_search import load_or_create_faiss, semantic_search

# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------
st.set_page_config(page_title="Semantic Video Search", layout="wide")

# --------------------------------------------------
# GLOBAL CSS
# --------------------------------------------------
st.markdown(
    """
<style>

/* Page background */
.stApp {
    background: linear-gradient(180deg, #ffffff 0%, #eef5ff 100%);
}

/* Force readable text */
html, body, [class*="css"] {
    color: #0f172a !important;
}

/* ---------------- FIXED HEADER ---------------- */
.fixed-header {
    position: sticky;
    top: 0;
    z-index: 999;
    background: linear-gradient(180deg, #ffffff 0%, #eef5ff 100%);
    padding: 1.2rem 1.2rem 1.5rem 1.2rem;
    border-bottom: 1px solid #e2e8f0;
    text-align: center;
}

/* Header title */
.header-title {
    font-size: 4rem;
    font-weight: 900;
    color: #0b3c91;
    margin-bottom: 0.25rem;
}

/* Header tagline */
.header-tagline {
    font-size: 1.25rem;
    color: #475569;
    margin-bottom: 1rem;
}

/* Search input */
div[data-baseweb="input"] input {
    color: #0b3c91 !important;
    background-color: #ffffff !important;
    caret-color: #0b3c91 !important;
    font-size: 1rem;
}

/* Placeholder */
div[data-baseweb="input"] input::placeholder {
    color: #94a3b8 !important;
}

/* Focus */
div[data-baseweb="input"] input:focus {
    border: 2px solid #3b82f6 !important;
    box-shadow: 0 0 0 2px rgba(59,130,246,0.15);
}

/* Content spacing */
.content {
    margin-top: 2rem;
}

/* Hero section */
.hero {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    margin-top: 5rem;
    text-align: center;
}

.hero-title {
    font-size: 3rem;
    font-weight: 800;
    color: #0b3c91;
    text-align: center;
}

.hero-subtitle {
    font-size: 1.1rem;
    color: #475569;
    margin-bottom: 3rem;
    text-align: center;
}

/* Center logo */
.logo-container {
    display: flex;
    justify-content: center;
    align-items: center;
    margin-top: 2rem;
}

/* Result card */
.result-card {
    background: white;
    border-left: 6px solid #3b82f6;
    border-radius: 14px;
    padding: 1.4rem;
    margin-top: 1.8rem;
    box-shadow: 0 10px 28px rgba(0,0,0,0.06);
}

.result-card h3 {
    color: #0b3c91 !important;
    font-weight: 800;
}

.result-card p {
    color: #334155 !important;
    line-height: 1.6;
}

</style>
""",
    unsafe_allow_html=True,
)

# --------------------------------------------------
# LOAD FAISS
# --------------------------------------------------
index, metadata = load_or_create_faiss()

# --------------------------------------------------
# FIXED HEADER (TITLE + TAGLINE + SEARCH)
# --------------------------------------------------
st.markdown('<div class="fixed-header">', unsafe_allow_html=True)


co1, col2, col3 = st.columns([1, 1, 1])
with col2:
    st.markdown(
        '<div class="header-title">Editor Search Engine</div>', unsafe_allow_html=True
    )

    st.markdown(
        '<div class="header-tagline">'
        "Search video scenes by meaning, emotion, and narrative intent"
        "</div>",
        unsafe_allow_html=True,
    )

query = st.text_input(
    "",
    placeholder="🔍 Search video by intent / meaning (e.g. intense courtroom argument)",
)

st.markdown("</div>", unsafe_allow_html=True)

# --------------------------------------------------
# CONTENT BELOW HEADER
# --------------------------------------------------
st.markdown('<div class="content">', unsafe_allow_html=True)

# ---------------- HOME STATE ----------------
if not query:
    st.markdown(
        """
    <div class="hero">
        <div class="hero-title">Find scenes by meaning</div>
        <div class="hero-subtitle">
            Built for editors to instantly locate the right moment
        </div>
    </div>
    """,
        unsafe_allow_html=True,
    )

    # Center the logo with custom container
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        st.image("logo.jpeg", width=600)

    st.stop()

# ---------------- RESULTS STATE ----------------
results = semantic_search(query, index, metadata, k=1)

if not results:
    st.warning("No matching video found")
else:
    for shot in results:
        source_video = shot.get("source_video", "")
        video_name = os.path.basename(source_video)

        st.markdown(
            f"""
        <div class="result-card">
            <h3>🎞 {shot.get("shot_id", "Unknown Shot")}</h3>
            <p><b>Video:</b> {video_name}</p>
            <p>{shot.get("description", "")}</p>
        </div>
        """,
            unsafe_allow_html=True,
        )

        video_path = source_video
        if video_path and not os.path.exists(video_path):
            video_path = os.path.join("..", video_path)

        if video_path and os.path.exists(video_path):
            st.video(video_path)
        else:
            st.warning(f"Video file not found: {video_path}")

st.markdown("</div>", unsafe_allow_html=True)
