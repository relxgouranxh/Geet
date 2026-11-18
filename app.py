import gradio as gr
import pandas as pd
from image_mood import get_mood_probs
from recommender import recommend

data = pd.read_csv("songs_normalized.csv")

def make_player(songs, n=5):
    html = ""
    for _, r in songs.head(n).iterrows():
        html += (
            f'<iframe src="https://open.spotify.com/embed/track/{r.track_id}" '
            f'width="100%" height="80" frameborder="0" allow="encrypted-media" '
            f'style="margin-bottom:8px;border-radius:12px"></iframe>'
        )
    return html

def run(image, industry):
    if image is None:
        return {}, pd.DataFrame(), ""
    probs = get_mood_probs(image)
    songs = recommend(data, probs, industry, top_n=15)
    table = songs.drop(columns="track_id")
    table["distance"] = table["distance"].round(3)
    return probs, table, make_player(songs)

def make_player(songs):
    html = '<div style="max-height:620px;overflow-y:auto;padding-right:8px">'
    for _, r in songs.iterrows():
        html += (
            f'<iframe src="https://open.spotify.com/embed/track/{r.track_id}" '
            f'width="100%" height="80" frameborder="0" loading="lazy" '
            f'allow="encrypted-media" style="margin-bottom:8px;border-radius:12px"></iframe>'
        )
    return html + "</div>"

demo = gr.Interface(
    fn=run,
    inputs=[
        gr.Image(type="pil", label="upload photo"),
        gr.Radio(["Bollywood", "Hollywood", "Both"], value="Both", label="Industry"),
    ],
    outputs=[
        gr.Label(label="mood of photo"),
        gr.Dataframe(label="Recommended songs"),
        gr.HTML(label="Play"),
    ],
    title="Geet",
)

if __name__ == "__main__":
    demo.launch()