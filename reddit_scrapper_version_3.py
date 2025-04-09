import streamlit as st
import praw
import pandas as pd
from datetime import datetime, timedelta
import os

# Set Streamlit app title
st.title("📥 Reddit Subreddit Scraper")
st.markdown("Scrape top 100 posts from any subreddit within the last 6 months.")

# Sidebar for credentials (use secrets when deploying!)
st.sidebar.title("🔐 Reddit API Credentials")
client_id = st.sidebar.text_input("Client ID", type="password", value=os.getenv("REDDIT_CLIENT_ID", ""))
client_secret = st.sidebar.text_input("Client Secret", type="password", value=os.getenv("REDDIT_CLIENT_SECRET", ""))
user_agent = st.sidebar.text_input("User Agent", value=os.getenv("REDDIT_USER_AGENT", "streamlit app"))

# Get subreddit from user
subreddit_name = st.text_input("Enter Subreddit Name (without r/)", value="fitness")

# Button to run scraper
if st.button("Scrape Reddit"):
    if not all([client_id, client_secret, user_agent]):
        st.error("Please fill in all Reddit API credentials.")
    else:
        # Initialize Reddit instance
        reddit = praw.Reddit(
            client_id=client_id,
            client_secret=client_secret,
            user_agent=user_agent
        )

        try:
            subreddit = reddit.subreddit(subreddit_name)
            six_months_ago = datetime.utcnow() - timedelta(days=180)
            six_months_ago_timestamp = six_months_ago.timestamp()

            data = []
            count = 0

            for post in subreddit.top(limit=300):
                if post.created_utc >= six_months_ago_timestamp:
                    data.append({
                        "Post ID": post.id,
                        "Title": post.title,
                        "Author": post.author.name if post.author else "Unknown",
                        "Timestamp": datetime.utcfromtimestamp(post.created_utc),
                        "Text": post.selftext,
                        "Score": post.score,
                        "Comments": post.num_comments,
                        "URL": post.url
                    })
                    count += 1
                if count >= 100:
                    break

            if data:
                df = pd.DataFrame(data)
                st.success(f"✅ Scraped {len(df)} posts from r/{subreddit_name}")
                st.dataframe(df)

                # Download CSV
                csv = df.to_csv(index=False).encode("utf-8")
                st.download_button(
                    label="📥 Download CSV",
                    data=csv,
                    file_name=f"{subreddit_name}_last_6_months.csv",
                    mime="text/csv"
                )
            else:
                st.warning("No posts found in the last 6 months.")

        except Exception as e:
            st.error(f"Error: {e}")
