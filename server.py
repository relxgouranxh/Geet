from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.staticfiles import StaticFiles
import pandas as pd
from PIL import Image, UnidentifiedImageError
from image_mood import get_mood_probs
from recommender import recommend

app = FastAPI(title="Photo to Song")
data = pd.read_csv("data/songs_normalized.csv")


@app.post("/recommend")
def rec(
    image: UploadFile = File(...),
    industry: str = Form("Both"),
):
    try:
        img = Image.open(image.file)
        img.load()
    except UnidentifiedImageError:
        raise HTTPException(status_code=400, detail="This is not a valid image")

    probs = get_mood_probs(img)
    songs = recommend(data, probs, industry, top_n=15)
    return {"moods": probs, "songs": songs.to_dict("records")}


# Sabse last mein rakhna
app.mount("/", StaticFiles(directory="frontend", html=True), name="static")