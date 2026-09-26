import os
import random
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

from app.recommender import MovieRecommender

BASE_DIR = Path(__file__).parent

app = FastAPI(title="CineMatch - Movie Recommendation Chatbot")
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
templates = Jinja2Templates(directory=BASE_DIR / "templates")

recommender = MovieRecommender()

GREETINGS = [
    "Hi! I'm CineBot 🎬 Tell me your mood today, or what movies you like.",
    "Hey there! What do you feel like watching? Give me a genre or a favorite title.",
]

NO_MATCH_REPLIES = [
    "Hmm, I couldn't find a strong match. Try naming a genre you like, e.g. 'action' or 'romance'?",
    "I didn't quite catch that. Try describing in more detail what kind of movie you're in the mood for.",
]


class ChatRequest(BaseModel):
    message: str


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    catalog = recommender.get_catalog()
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "catalog": catalog, "greeting": random.choice(GREETINGS)},
    )


@app.post("/api/chat")
async def chat(payload: ChatRequest):
    message = payload.message.strip()
    if not message:
        return {"reply": "Try typing something first \U0001F642", "recommendations": []}

    recommendations = recommender.recommend(message, top_n=6)

    if not recommendations:
        return {"reply": random.choice(NO_MATCH_REPLIES), "recommendations": []}

    top = recommendations[0]
    genres = recommender.genres_mentioned(message)
    genre_txt = f" in {', '.join(genres)}" if genres else ""
    reply = (
        f"Here are some recommendations{genre_txt} for you! "
        f"Top pick: **{top['title']}** ({top['match']}% match)."
    )
    return {"reply": reply, "recommendations": recommendations}


@app.get("/api/catalog")
async def get_catalog():
    return recommender.get_catalog()


if __name__ == "__main__":
    import uvicorn

    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("app.main:app", host="0.0.0.0", port=port)
