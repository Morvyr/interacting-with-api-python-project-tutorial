import os
import time
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from dotenv import load_dotenv

# load the .env file variables
load_dotenv()

api_key = os.environ.get("LASTFM_API")
api_secret = os.environ.get("LASTFM_SECRET")

import pylast

network = pylast.LastFMNetwork(
    api_key = api_key,
    api_secret = api_secret
)


artist_name = "Zach Bryan"
artist = network.get_artist("Zach Bryan")

top_tracks = artist.get_top_tracks(limit=10)

rows = []
for track_obj, weight_obj in top_tracks:
    start = time.time()
    track_name = track_obj.get_title()
    playcount = track_obj.get_playcount()
    listeners = track_obj.get_listener_count()
    duration_ms = track_obj.get_duration() or 0

    print(f"API calls took: {time.time() - start:.3f}s")

    duration_s = duration_ms / 1000 if duration_ms else 0
    duration_m = int(duration_s // 60)
    duration_rs = int(duration_s % 60)
    duration_t = f"{duration_m}:{duration_rs:02d}" if duration_ms else None

    rows.append({
        "track_name": track_name,
        "playcount": int(playcount) if playcount is not None else 0,
        "listeners": int(listeners) if listeners is not None else 0,
        "duration": duration_t,
        "duration_m": (duration_ms / 1000 / 60) if duration_ms else None
    })

df = pd.DataFrame(rows)
print(df)

df_sorted = df.sort_values("listeners", ascending=False)
print(df_sorted.head(3))

df_clean = df.dropna(subset=["duration_m"]).copy()

plt.figure()
sns.scatterplot(data=df_clean, x="duration_m", y="listeners")
plt.title(f"{artist_name}: Duration vs Listeners (Last.fm)")
plt.xlabel("Duration (minutes)")
plt.ylabel("Listeners")
plt.show()


# There is no real trend with Zach Bryan, as his songs tend to gain listeners based on emotional relation, not length, as seen above.

def get_top_tags(track_obj, max_tags=5):
    tags = track_obj.get_top_tags(limit=max_tags)
    return [tag.item.get_name() for tag in tags]

df["top_tags"] = [
    get_top_tags(network.get_track(artist_name, name), max_tags=5)
    for name in df["track_name"]
]

df["n_tags"] = df["top_tags"].apply(len)

tags_exploded = df[["track_name", "listeners", "top_tags"]].explode("top_tags")
tag_counts = tags_exploded["top_tags"].value_counts()
print(tag_counts.head(10))

plt.figure()
tag_counts.head(10).plot(kind="bar")
plt.title(f"{artist_name}: Most Common Track Tags (Top 10 Tracks)")
plt.xlabel("Tag")
plt.ylabel("Count")
plt.show()

# Among Zach Bryan's top tracks on Last.fm, the most common tags were 'americana' and 'country'. Track duration was not a good indicator of song popularity, as Zach's songs are tied to emotions, not logic.


