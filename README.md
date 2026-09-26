# CineMatch — Movie Recommendation Chatbot

A Netflix-styled recommendation chatbot demo. Chat on the left describes what
you feel like watching; the catalog on the right re-ranks and badges each
title with a **% match** score computed with TF-IDF + cosine similarity.

All catalog data is **dummy data based on real, publicly known movies**
(title, genre, cast, description) — no confidential or personal data, and no
external API keys are required.

## Stack
- FastAPI (backend + chat API)
- Jinja2 + vanilla JS/CSS (frontend, Netflix-inspired dark UI)
- scikit-learn TF-IDF content-based recommender

## Run locally
```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```
Open http://127.0.0.1:8000

## Deploy to Render
This repo includes `render.yaml` for one-click Blueprint deploy:
1. Push this repo to GitHub.
2. On Render: New → Blueprint → select this repo.
3. Render reads `render.yaml` and deploys automatically (free plan, no secrets needed).

## How it works
1. Type what you're in the mood for (genre, title, actor, vibe) in the chat.
2. CineBot cleans the text and computes cosine similarity against the TF-IDF
   vectors built from each movie's title/genres/cast/description.
3. The catalog panel re-sorts and highlights matches with a color-coded
   match-percentage badge (green = high, yellow = medium, gray = low).
