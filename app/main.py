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
    "Halo! Aku CineBot 🎬 Ceritain mood kamu hari ini, atau film apa yang kamu suka?",
    "Hai! Mau nonton apa hari ini? Kasih tau genre atau judul film favoritmu.",
]

NO_MATCH_REPLIES = [
    "Hmm, belum ketemu yang cocok banget. Coba sebutin genre favoritmu, misalnya 'action' atau 'romance'?",
    "Aku belum nangkep maksudnya nih. Coba ceritain lebih detail film seperti apa yang kamu mau tonton.",
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
        return {"reply": "Coba ketik sesuatu dulu ya \U0001F642", "recommendations": []}

    recommendations = recommender.recommend(message, top_n=6)

    if not recommendations:
        return {"reply": random.choice(NO_MATCH_REPLIES), "recommendations": []}

    top = recommendations[0]
    genres = recommender.genres_mentioned(message)
    genre_txt = f" bertema {', '.join(genres)}" if genres else ""
    reply = (
        f"Nih beberapa rekomendasi{genre_txt} buat kamu! "
        f"Yang paling cocok: **{top['title']}** ({top['match']}% match)."
    )
    return {"reply": reply, "recommendations": recommendations}


@app.get("/api/catalog")
async def get_catalog():
    return recommender.get_catalog()


if __name__ == "__main__":
    import uvicorn

    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("app.main:app", host="0.0.0.0", port=port)
