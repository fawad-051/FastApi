import os
import requests
import streamlit as st
from dotenv import load_dotenv

load_dotenv()
BASE_URL = os.getenv("SERVER_BASE_URL", "https://your-backend-url.railway.app").rstrip("/")
TIMEOUT = float(os.getenv("CLIENT_TIMEOUT_SEC", "30"))

st.set_page_config(
    page_title="LangChain Chatbot - Dr. Fawad Hussain",
    page_icon="🤖",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ============= Theming / CSS =============
PRIMARY = "#5B2E91"   # purple
ACCENT = "#18BC9C"    # teal
BG_SOFT = "#0b0f19"   # dark-ish bg
TEXT_SOFT = "#e8e8f0"

st.markdown(
    f"""
    <style>
      /* Remove Streamlit header & spacing */
      .block-container {{
        padding-top: 0 !important;
        margin-top: 0 !important;
      }}
      .stAppHeader, header {{ display: none !important; }}

      /* Global font */
      html, body, [class*="css"] {{
        font-family: -apple-system, Inter, Segoe UI, Roboto, Helvetica, Arial, sans-serif;
      }}

      /* Hero */
      .hero {{
        background: linear-gradient(135deg, {PRIMARY} 0%, {ACCENT} 100%);
        padding: 24px 24px;
        border-radius: 18px;
        color: white;
        margin-bottom: 18px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.15);
      }}
      .hero h1 {{ margin: 0; font-size: 1.8rem; }}
      .hero p {{ margin: 4px 0 0 0; opacity: 0.9; }}

      /* Card */
      .card {{
        background: #1b1f27;
        border: 1px solid rgba(255,255,255,0.05);
        border-radius: 16px;
        padding: 18px;
        box-shadow: 0 6px 18px rgba(0,0,0,0.2);
        margin-top: 6px;
      }}

      /* Section title */
      .section-title {{
        font-weight: 700;
        font-size: 1.05rem;
        margin-bottom: 6px;
        color: #ffffff;
      }}

      /* Result box */
      .result {{
        background: #10141c;
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 12px;
        padding: 14px;
        white-space: pre-wrap;
        font-size: 0.95rem;
        color: #f0f0f0;
      }}

      /* Footer note */
      .soft-note {{
        color: #6b7280;
        font-size: 0.85rem;
      }}

      /* Buttons */
      div.stButton > button:first-child {{
        background: {PRIMARY} !important;
        color: white !important;
        border-radius: 12px !important;
        border: none !important;
        padding: 0.55rem 0.9rem !important;
        font-weight: 600 !important;
      }}
      div.stButton > button:hover {{
        background: {ACCENT} !important;
        color: black !important;
      }}

      /* Inputs — remove white bar */
      .stTextInput > div > div > input,
      .stTextArea textarea {{
        background: #161921 !important;
        color: #f2f2f2 !important;
        border-radius: 10px !important;
        border: 1px solid rgba(255,255,255,0.08) !important;
        box-shadow: none !important;
      }}
      .stTextInput > div > div {{
        background: transparent !important;
      }}
    </style>
    """,
    unsafe_allow_html=True,
)

# ============= Helpers =============
def _invoke(route: str, payload: dict) -> dict:
    """POST to a LangServe /invoke endpoint with basic error handling."""
    url = f"{BASE_URL}/{route.strip('/')}/invoke"
    try:
        resp = requests.post(url, json=payload, timeout=TIMEOUT)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        st.error(f"❌ Request failed: {e}")
        return {}

def _extract_text(result: dict) -> str:
    """Extract readable text from LangServe-style responses."""
    if not isinstance(result, dict) or "output" not in result:
        return "⚠️ Unexpected response format."

    out = result["output"]
    if isinstance(out, str):
        return out.strip()

    if isinstance(out, dict) and isinstance(out.get("content"), str):
        return out["content"].strip()

    if isinstance(out, dict) and isinstance(out.get("content"), list):
        parts = [c.get("text", "") for c in out["content"] if isinstance(c, dict)]
        joined = "\n".join([p for p in parts if p]).strip()
        return joined or "⚠️ Empty response."

    return str(out)

def get_essay_response(topic: str) -> str:
    return _extract_text(_invoke("essay", {"input": {"topic": topic}}))

def get_poem_response(topic: str) -> str:
    return _extract_text(_invoke("poem", {"input": {"topic": topic}}))

# ============= Header / Hero =============
st.markdown(
    """
    <div class="hero">
      <h1>🤖 LangChain Playground</h1>
      <p>Developed by Dr. Fawad Hussain · OpenAI & Groq via LangServe</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# Tiny status row
c1, c2 = st.columns([0.7, 0.3])
with c1:
    st.caption(f"**Server:** {BASE_URL}")
with c2:
    st.caption(f"**Timeout:** {int(TIMEOUT)}s")

# Tabs
tab1, tab2 = st.tabs(["📝 Essay (OpenAI)", "🎵 Poem (Groq)"])

with tab1:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Generate a concise 100 word essay</div>', unsafe_allow_html=True)
    topic_essay = st.text_input("Topic", key="essay_topic", placeholder="e.g, AI in Pakistan")
    col_a, col_b = st.columns([0.25, 0.75])

    with col_a:
        btn_essay = st.button("Generate Essay", key="btn_essay")
    with col_b:
        st.caption("Uses OpenAI route `/essay`. Make sure `OPENAI_API_KEY` is set on the server.")

    result_placeholder_essay = st.empty()
    if btn_essay and topic_essay:
        with st.spinner("Thinking..."):
            text = get_essay_response(topic_essay)
        with result_placeholder_essay.container():
            st.markdown('<div class="result">', unsafe_allow_html=True)
            st.write(text)
            st.markdown("</div>", unsafe_allow_html=True)
            st.download_button(
                "Download Essay",
                data=text.encode("utf-8"),
                file_name=f"essay_{topic_essay.replace(' ', '_')}.txt",
                use_container_width=True,
            )
    st.markdown("</div>", unsafe_allow_html=True)

with tab2:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Write a playful 100 word poem</div>', unsafe_allow_html=True)
    topic_poem = st.text_input("Topic", key="poem_topic", placeholder="e.g., friendly robots")
    col_c, col_d = st.columns([0.37, 0.73])

    with col_c:
        btn_poem = st.button("Generate Poem", key="btn_poem")
    with col_d:
        st.caption("Uses Groq route `/poem`. Make sure `GROQ_API_KEY` is set on the server.")

    result_placeholder_poem = st.empty()
    if btn_poem and topic_poem:
        with st.spinner("Rhyming..."):
            text = get_poem_response(topic_poem)
        with result_placeholder_poem.container():
            st.markdown('<div class="result">', unsafe_allow_html=True)
            st.write(text)
            st.markdown("</div>", unsafe_allow_html=True)
            st.download_button(
                "Download Poem",
                data=text.encode("utf-8"),
                file_name=f"poem_{topic_poem.replace(' ', '_')}.txt",
                use_container_width=True
            )
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("---")
st.markdown(
    f"""
    <div class="soft-note">
      Developed by <b>Dr. Fawad Hussain</b> · Tip: Edit your <code>.env</code> to change <b>SERVER_BASE_URL</b> or <b>CLIENT_TIMEOUT_SEC</b>.
    </div>
    """,
    unsafe_allow_html=True,

)
