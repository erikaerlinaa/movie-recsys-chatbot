import json
import re
from pathlib import Path

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

DATA_PATH = Path(__file__).parent / "data" / "catalog.json"

STOPWORDS = {
    # Indonesian
    "aku", "saya", "gue", "gw", "suka", "mau", "pengen", "cari", "carikan",
    "yang", "kayak", "seperti", "mirip", "dong", "nih", "tolong", "kasih",
    "rekomendasi", "rekomendasiin", "tontonan", "buat", "untuk", "ada",
    "gak", "nggak",
    # English
    "i", "me", "my", "im", "like", "love", "want", "looking", "for",
    "find", "recommend", "recommendation", "movie", "movies", "film",
    "films", "genre", "please", "some", "give", "show", "watch", "to",
    "the", "and", "of", "a", "an", "with",
}


def _clean(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    tokens = [t for t in text.split() if t not in STOPWORDS]
    return " ".join(tokens)


class MovieRecommender:
    def __init__(self, data_path: Path = DATA_PATH):
        with open(data_path, "r", encoding="utf-8") as f:
            self.catalog = json.load(f)

        self.corpus = [
            _clean(
                " ".join(
                    [
                        movie["title"],
                        movie["director"],
                        " ".join(movie["cast"]),
                        " ".join(movie["genres"] * 3),  # weight genres higher
                        movie["description"],
                    ]
                )
            )
            for movie in self.catalog
        ]

        self.vectorizer = TfidfVectorizer()
        self.matrix = self.vectorizer.fit_transform(self.corpus)

    def get_catalog(self):
        return [{**m, "match": None} for m in self.catalog]

    def recommend(self, query: str, top_n: int = 6):
        cleaned = _clean(query)
        if not cleaned.strip():
            return []

        query_vec = self.vectorizer.transform([cleaned])
        scores = cosine_similarity(query_vec, self.matrix).flatten()

        ranked = sorted(
            zip(self.catalog, scores), key=lambda pair: pair[1], reverse=True
        )

        results = []
        for movie, score in ranked[:top_n]:
            if score <= 0:
                continue
            results.append({**movie, "match": round(float(score) * 100, 1)})
        return results

    def genres_mentioned(self, query: str):
        q = query.lower()
        all_genres = {g for m in self.catalog for g in m["genres"]}
        return [g for g in all_genres if g.lower() in q]
