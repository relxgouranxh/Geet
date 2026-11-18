import pandas as pd
from sklearn.preprocessing import MinMaxScaler

FEATURES = ["valence", "energy", "danceability", "acousticness", "tempo", "loudness"]

BOLLY = ["Arijit Singh", "A.R. Rahman", "Shreya Ghoshal", "Atif Aslam",
         "Sonu Nigam", "Neha Kakkar", "Badshah", "Jubin Nautiyal", "Armaan Malik",
         "KK", "Kishore Kumar", "Lata Mangeshkar", "Mohit Chauhan", "Sunidhi Chauhan","Diljit Dosanjh", "Yo Yo Honey Singh", "Mika Singh", "Udit Narayan",
"Kumar Sanu", "Alka Yagnik", "Sukhwinder Singh", "Vishal Dadlani",
"Benny Dayal", "Shalmali Kholgade", "Darshan Raval", "B Praak",
"Guru Randhawa", "Tony Kakkar", "Mohammed Rafi", "Asha Bhosle","Mohit Chauhan", "Mithoon", "Ankit Tiwari", "Palak Muchhal", "Papon"]

HOLLY = ["Taylor Swift", "Ed Sheeran", "The Weeknd", "Dua Lipa", "Coldplay",
         "Billie Eilish", "Justin Bieber", "Ariana Grande", "Post Malone",
         "Imagine Dragons", "Bruno Mars","Maroon 5", "Harry Styles", "Eminem"]

df = pd.read_csv("data/spotify_raw.csv")

bolly = df[df["artist_name"].isin(BOLLY)].copy()
bolly["industry"] = "Bollywood"
holly = df[df["artist_name"].isin(HOLLY)].copy()
holly["industry"] = "Hollywood"

data = pd.concat([bolly, holly]).drop_duplicates(subset="track_id").reset_index(drop=True)

data = data[["track_id", "track_name", "artist_name", "industry"] + FEATURES]

# Har industry ke andar alag normalize (0-1)
for ind in data["industry"].unique():
    mask = data["industry"] == ind
    data.loc[mask, FEATURES] = MinMaxScaler().fit_transform(data.loc[mask, FEATURES])

data.to_csv("songs_normalized.csv", index=False)

print(data["industry"].value_counts())
print("Missing artists:", set(BOLLY + HOLLY) - set(data["artist_name"]))
print(data.groupby("industry")[FEATURES].agg(["min", "max"]))