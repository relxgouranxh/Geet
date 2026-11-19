import io
from contextlib import asynccontextmanager
from pathlib import Path

import pandas as pd
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.staticfiles import StaticFiles
from PIL import Image, UnidentifiedImageError

from image_mood import get_mood_probs
from recommender import recommend

BASE = Path(__file__).parent
REQUIRED = {"track_id", "track_name", "artist_name", "industry",
            "valence", "energy", "danceability", "acousticness", "tempo", "loudness"}
VALID_INDUSTRIES = {"Both", "Bollywood", "Hollywood"}
MAX_BYTES = 10 * 1024 * 1024  # 10 MB

data = pd.read_csv(BASE / "songs_normalized.csv")
missing = REQUIRED - set(data.columns)
if missing:
    raise RuntimeError(f"songs_normalized.csv is missing columns: {sorted(missing)}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    get_mood_probs(Image.new("RGB", (64, 64), "gray"))   # model warm-up
    yield


app = FastAPI(title="Geet", lifespan=lifespan)


@app.get("/health")
def health():
    return {"status": "ok", "songs": len(data)}


# def (async nahi): CLIP heavy hai, FastAPI ise threadpool mein chalata hai
@app.post("/recommend")
def rec(image: UploadFile = File(...), industry: str = Form("Both")):
    if industry not in VALID_INDUSTRIES:
        raise HTTPException(400, "Invalid industry")

    raw = image.file.read(MAX_BYTES + 1)
    if len(raw) > MAX_BYTES:
        raise HTTPException(413, "Image is too large (max 10 MB)")

    try:
        img = Image.open(io.BytesIO(raw))
        img.load()
    except (UnidentifiedImageError, OSError):
        raise HTTPException(400, "This is not a valid image")

    img = img.convert("RGB")
    img.thumbnail((1024, 1024))

    probs = get_mood_probs(img)
    songs = recommend(data, probs, industry, top_n=15)
    if songs.empty:
        raise HTTPException(404, "No songs found for this filter")

    songs = songs.copy()
    songs["distance"] = songs["distance"].astype(float).round(3)
    return {"moods": probs, "songs": songs.to_dict("records")}


app.mount("/", StaticFiles(directory=BASE / "frontend", html=True), name="frontend")