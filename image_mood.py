import sys
import torch
from PIL import Image
from transformers import CLIPModel, CLIPProcessor

model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")

MOOD_PROMPTS = {
    "happy":    "a photo of happy cheerful people having fun",
    "calm":     "a photo of a calm peaceful quiet place",
    "sad":      "a photo of a sad lonely gloomy scene",
    "party":    "a photo of a party, nightlife, dancing and celebration",
    "romantic": "a romantic photo of a couple at sunset, love",
}

def get_mood_probs(image, temperature=2.0):
    # image: PIL image ya file path
    if isinstance(image, str):
        image = Image.open(image)
    image = image.convert("RGB")

    inputs = processor(text=list(MOOD_PROMPTS.values()), images=image,
                       return_tensors="pt", padding=True)
    with torch.no_grad():
        logits = model(**inputs).logits_per_image[0]
    probs = (logits / temperature).softmax(dim=0)
    return {m: float(p) for m, p in zip(MOOD_PROMPTS, probs)}

if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else "happy.jpeg"
    probs = get_mood_probs(path)
    for mood, p in sorted(probs.items(), key=lambda x: -x[1]):
        print(f"{mood:10s} {p:.2f}")