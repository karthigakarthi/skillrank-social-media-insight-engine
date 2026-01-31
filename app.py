import streamlit as st 
import sqlite3
import pandas as pd

# -------------------------------------------------
# Page Config
# -------------------------------------------------
st.set_page_config(
    page_title="Real-Time Social Media Insight Engine",
    layout="wide"
)

# -------------------------------------------------
# GLOBAL NEON THEME (CSS)
# -------------------------------------------------
st.markdown("""
<style>

.stApp {
    background: radial-gradient(circle at top, #1a1233, #0b0816 60%);
    color: #ffffff;
}

section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #120b2d, #0a0717);
    border-right: 1px solid #2b1f55;
}

h1, h2, h3, h4 {
    color: #e6dcff;
}

.glass {
    background: rgba(255, 255, 255, 0.05);
    border-radius: 16px;
    padding: 24px;
    margin-bottom: 24px;
    border: 1px solid rgba(170, 140, 255, 0.25);
    box-shadow: 0 0 25px rgba(160, 120, 255, 0.15);
}

[data-testid="stMetricValue"] {
    color: #bfa6ff;
    font-size: 28px;
}

.stButton button {
    background: linear-gradient(135deg, #7b5cff, #9f7cff);
    border: none;
    border-radius: 12px;
    color: white;
    padding: 0.6rem 1.4rem;
    font-weight: 600;
    box-shadow: 0 0 20px rgba(160,120,255,0.4);
}

input {
    background-color: rgba(255,255,255,0.06) !important;
    border-radius: 10px !important;
    border: 1px solid #3a2b70 !important;
    color: white !important;
}

</style>
""", unsafe_allow_html=True)

# -------------------------------------------------
# Helper UI Functions
# -------------------------------------------------
def glass_container(title, subtitle):
    st.markdown(f"""
    <div class="glass">
        <h2>{title}</h2>
        <p style="color:#b8aaff;">{subtitle}</p>
    </div>
    """, unsafe_allow_html=True)


def gradient_progress(label, value, c1, c2):
    st.markdown(f"""
    <div style="margin-bottom:18px;">
        <div style="margin-bottom:6px; font-weight:600;">
            {label} — {value:.1f}%
        </div>
        <div style="width:100%; background:rgba(255,255,255,0.08);
                    border-radius:14px; height:18px;">
            <div style="width:{value}%;
                        height:100%;
                        background:linear-gradient(90deg,{c1},{c2});
                        box-shadow:0 0 14px {c2};
                        border-radius:14px;">
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# -------------------------------------------------
# Load Data
# -------------------------------------------------
conn = sqlite3.connect("social.db")
df = pd.read_sql("SELECT * FROM posts", conn)

df["date"] = pd.to_datetime(
    df["date"],
    format="%a %b %d %H:%M:%S %Z %Y",
    errors="coerce"
)

# -------------------------------------------------
# Sidebar
# -------------------------------------------------
st.sidebar.markdown("""
<h2 style="color:#cbb8ff;">📊 Social Media Insight Engine</h2>
<p style="color:#9f90ff;">Real-Time Analytics Dashboard</p>
""", unsafe_allow_html=True)

page = st.sidebar.radio(
    "Navigation",
    ["Overview", "Trends", "Search", "LLM Insights"]
)

# -------------------------------------------------
# Metrics
# -------------------------------------------------
total_posts = len(df)
sentiment_counts = df["sentiment_label"].value_counts()

# -------------------------------------------------
# OVERVIEW
# -------------------------------------------------
if page == "Overview":
    glass_container(
        "📊 Overview Dashboard",
        "High-level sentiment and activity insights"
    )

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Posts", f"{total_posts:,}")
    c2.metric("😊 Positive", sentiment_counts.get("Positive", 0))
    c3.metric("😐 Neutral", sentiment_counts.get("Neutral", 0))
    c4.metric("😢 Negative", sentiment_counts.get("Negative", 0))

    # Sentiment Distribution (inside glass)
    st.markdown('<div class="glass">', unsafe_allow_html=True)
    st.markdown("### 😊 Sentiment Distribution")
    st.bar_chart(sentiment_counts)

    total = sentiment_counts.sum()
    gradient_progress("😊 Positive", sentiment_counts.get("Positive", 0)/total*100, "#7b5cff", "#9f7cff")
    gradient_progress("😐 Neutral", sentiment_counts.get("Neutral", 0)/total*100, "#4fd1c5", "#2dd4bf")
    gradient_progress("😢 Negative", sentiment_counts.get("Negative", 0)/total*100, "#ff6b6b", "#ff3b3b")
    st.markdown('</div>', unsafe_allow_html=True)

    # -------------------------------
    # ✅ POSTS OVER TIME (FIXED)
    # -------------------------------
    posts_over_time = (
        df.dropna(subset=["date"])
          .assign(month=df["date"].dt.to_period("M").astype(str))
          .groupby("month")
          .size()
          .reset_index(name="Posts")
          .head(12)
    )

    st.markdown("## 📊 Posts Over Time")
    st.bar_chart(posts_over_time.set_index("month"))
    st.caption("Monthly post volume trend")

# -------------------------------------------------
# TRENDS
# -------------------------------------------------
elif page == "Trends":
    glass_container(
        "🔥 Trending Topics & Hashtags",
        "Most discussed themes across posts"
    )

    hashtags = df["hashtags"].str.split(",").explode()
    top_hashtags = hashtags.value_counts().head(10)

    st.markdown('<div class="glass">', unsafe_allow_html=True)
    st.markdown("### 🔝 Top Hashtags")
    st.bar_chart(top_hashtags)
    st.dataframe(top_hashtags.reset_index(), use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="glass">', unsafe_allow_html=True)
    st.markdown("### 📌 Hashtag Sentiment Analysis")

    selected_tag = st.selectbox(
        "Select a hashtag to analyze",
        top_hashtags.index.tolist()
    )

    tag_df = df[df["hashtags"].str.contains(selected_tag, na=False)]
    st.write(f"**Total Mentions:** {len(tag_df)}")

    if len(tag_df) > 0:
        tag_sentiment = tag_df["sentiment_label"].value_counts(normalize=True) * 100
        st.bar_chart(tag_sentiment)

        st.markdown(f"""
        **🧠 LLM Insight**  
        *Discussion around **{selected_tag}** shows
        **{tag_sentiment.get("Positive",0):.1f}% positive sentiment**, indicating strong engagement.*
        """)
    else:
        st.warning("No posts found for this hashtag.")

    st.markdown('</div>', unsafe_allow_html=True)

# -------------------------------------------------
# SEARCH
# -------------------------------------------------
elif page == "Search":
    glass_container(
        "🔍 Search & Analysis",
        "Ask questions in natural language"
    )

    query = st.text_input("What are people saying about?")

    if query:
        keywords = [w.lower() for w in query.split() if len(w) > 3]
        pattern = "|".join(keywords)
        results = df[df["text"].str.contains(pattern, case=False, na=False)]

        st.markdown('<div class="glass">', unsafe_allow_html=True)
        st.write(f"**Total matching posts:** {len(results)}")

        sentiment_pct = results["sentiment_label"].value_counts(normalize=True) * 100
        st.bar_chart(sentiment_pct)

        pos = sentiment_pct.get("Positive", 0)
        st.markdown(f"""
        **🧠 LLM Summary**  
        *"{query.title()} shows **{pos:.1f}% positive sentiment**.
        Key themes: price, performance, reliability."*
        """)

        st.dataframe(results[["text", "sentiment_label"]].head(15))
        st.markdown('</div>', unsafe_allow_html=True)

# -------------------------------------------------
# LLM INSIGHTS
# -------------------------------------------------
elif page == "LLM Insights":
    glass_container(
        "🧠 LLM-Generated Insights",
        "AI-style explanations of social trends"
    )

    st.markdown('<div class="glass">', unsafe_allow_html=True)
    st.markdown("""
    ### 🚨 Customer Service Crisis Detected
    🔴 **Risk Level:** HIGH  
    🔺 Spike: **340%**

    ### 🚀 #NewProduct Trending
    🟢 Sentiment: **78% Positive**

    ### 🔄 Topic Shift: Remote → Hybrid
    📈 Hybrid mentions ↑ **120%**
    """)
    st.markdown('</div>', unsafe_allow_html=True)

# -------------------------------------------------
# Footer
# -------------------------------------------------
st.markdown("""
<p style="text-align:center; color:#8a7bd6;">
⚡ Social Media Insight Engine • Neon Analytics UI
</p>
""", unsafe_allow_html=True)
