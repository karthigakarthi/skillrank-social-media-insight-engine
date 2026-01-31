import pandas as pd
import sqlite3
import re

print("Loading dataset...")

df = pd.read_csv(
    "training.1600000.processed.noemoticon.csv",
    encoding="latin-1",
    header=None
)

df.columns = ["sentiment", "id", "date", "query", "user", "text"]

print("Total rows in dataset:", len(df))

# Take 500K posts
df = df.sample(500000)

# Map sentiment labels
df["sentiment_label"] = df["sentiment"].map({
    0: "Negative",
    2: "Neutral",
    4: "Positive"
})

# Extract hashtags as STRING (SQLite-safe)
df["hashtags"] = df["text"].apply(
    lambda x: ",".join(re.findall(r"#\w+", x.lower()))
)

print("Saving to database...")

conn = sqlite3.connect("social.db")
df.to_sql("posts", conn, if_exists="replace", index=False)
conn.close()

print("✅ Analyzed 500,000 posts")
