# Geet 🎧

Upload a photo and get songs that match its mood. Choose Bollywood, Hollywood, or both.

> **Status: Prototype.** This is a proof of concept, not a full music search engine. It does **not** cover all songs. See [Dataset scope](#dataset-scope) below.

**Stack:** CLIP (zero-shot mood detection), FastAPI, HTML/CSS/JS

## How it works

Photo → CLIP → mood probabilities → target audio vector → industry filter → nearest songs

1. CLIP compares the photo against text prompts for five moods: happy, calm, sad, party, romantic.
2. The mood probabilities are blended into a target vector of Spotify audio features (valence, energy, danceability, acousticness, tempo, loudness).
3. Songs are filtered by the selected industry and ranked by weighted Euclidean distance to the target.
4. Results are de-duplicated, limited per artist, and sampled with some randomness so each search gives fresh songs.

## Dataset scope

The song pool is intentionally small:

- Songs come from a Kaggle Spotify audio-features dataset.
- Only tracks by a **hand-picked list of Bollywood and Hollywood artists** are included (roughly a few hundred songs in total).
- Industry labels come from that artist list, not from Spotify metadata.
- Many popular songs and artists are **not** in the dataset, so a song you expect may never appear.
- The dataset has no release year, so there is no true "new vs old" filter.

Adding more artists means editing the artist lists in `data_prep.py` and re-running it.

## Known limitations

- **Audio only, no lyrics.** A devotional or bittersweet song can look "sad" or "happy" purely from its audio features.
- **Moods are rough.** The mood-to-audio vectors are hand-tuned, so results are about 70 to 80% sensible, not perfect.
- **Small Bollywood pool.** Many Bollywood tracks in the data are ballads, so "happy" and "sad" results are weaker than for Hollywood.
- **Some regional songs** (Telugu, Malayalam) appear because the same artists sing in multiple languages.
- **Photo understanding is simple.** CLIP picks the closest of five moods, and one photo can only be matched to those five.
- **Playback** uses Spotify embeds. Without a logged-in Spotify account, only 30-second previews play, and some tracks may be unavailable in some regions.

## Roadmap

- Larger, more diverse dataset with release years (Spotify API)
- Lyrics sentiment analysis
- More moods and scene/caption understanding
- User feedback loop (like/dislike)
- Language and era filters

## Run locally

```bash
git clone https://github.com/relxgouranxh/geet.git
cd geet
pip install -r requirements.txt
python data_prep.py        # builds songs_normalized.csv (needs the raw Kaggle CSV in data/)
uvicorn server:app --port 8000
```

Open http://127.0.0.1:8000

## Project structure

```
geet/
├── server.py            # FastAPI app
├── image_mood.py        # CLIP mood detection
├── recommender.py       # filtering and ranking
├── data_prep.py         # dataset cleaning and normalization
├── songs_normalized.csv # prepared song data
└── frontend/            # HTML, CSS, JS
```