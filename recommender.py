import numpy as np
import pandas as pd

FEATURES = ["valence", "energy", "danceability", "acousticness", "tempo", "loudness"]
WEIGHTS = np.array([3.0, 2.0, 1.0, 1.0, 0.5, 0.5])

# Order: valence, energy, danceability, acousticness, tempo, loudness
MOOD_VECTORS = {
    "happy":    [0.85, 0.75, 0.75, 0.25, 0.60, 0.75],
    "calm":     [0.50, 0.25, 0.40, 0.75, 0.35, 0.40],
    "sad": [0.10, 0.20, 0.30, 0.70, 0.30, 0.35],
    "party":    [0.75, 0.90, 0.85, 0.10, 0.70, 0.85],
    "romantic": [0.55, 0.40, 0.50, 0.60, 0.40, 0.50],
}
def dedupe(df):
    # brackets aur " - Live/Remix/From..." 
    base = (df["track_name"]
            .str.replace(r"\s*[\(\[].*?[\)\]]", "", regex=True)
            .str.replace(r"\s+-\s.*$", "", regex=True)
            .str.strip().str.lower())
    return df.assign(_base=base).drop_duplicates(["_base", "artist_name"]).drop(columns="_base")

def recommend(data, mood_probs, industry="Both", top_n=10):
    target = sum(np.array(MOOD_VECTORS[m]) * p for m, p in mood_probs.items())

    songs = data if industry == "Both" else data[data["industry"] == industry]

    diff = (songs[FEATURES].values - target) * WEIGHTS
    dist = np.linalg.norm(diff, axis=1)

    out = songs.assign(distance=dist).sort_values("distance")
    out = dedupe(out)                                  
    out = out.groupby("artist_name").head(3)          
    out = out.sort_values("distance")

    pool = out.head(top_n * 3)
    w = np.exp(-(pool["distance"].values - pool["distance"].min()) / 0.15)
    w = w / w.sum()
    n = min(top_n, len(pool))
    idx = np.random.choice(len(pool), size=n, replace=False, p=w)

    out = pool.iloc[idx].sort_values("distance")
    return out[["track_id", "track_name", "artist_name", "industry", "distance"]]







if __name__ == "__main__":
    data = pd.read_csv("songs_normalized.csv")
    for mood in MOOD_VECTORS:
        for ind in ["Bollywood", "Hollywood"]:
            print(f"\n=== {mood.upper()} | {ind} ===")
            print(recommend(data, {mood: 1.0}, ind, top_n=5).to_string(index=False))