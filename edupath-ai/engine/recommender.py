"""
engine/recommender.py
TF-IDF + cosine similarity content-based recommender.
"""
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Module-level storage (populated once at startup)
_tfidf_matrix = None
_cosine_sim: np.ndarray | None = None
_courses_list: list | None = None
_id_to_index: dict = {}


def init_recommender(courses_list: list) -> None:
    """
    Precompute TF-IDF matrix and cosine similarity matrix.
    Call once at Flask app startup.
    """
    global _tfidf_matrix, _cosine_sim, _courses_list, _id_to_index

    _courses_list = courses_list

    # Build combined text feature
    texts = [
        f"{c.get('course_title', '')} {c.get('category', '')} {c.get('course_difficulty', '')}"
        for c in courses_list
    ]

    vectorizer = TfidfVectorizer(stop_words='english', ngram_range=(1, 2))
    _tfidf_matrix = vectorizer.fit_transform(texts)
    _cosine_sim = cosine_similarity(_tfidf_matrix, _tfidf_matrix)

    # Build index map: course_id → position in list
    _id_to_index = {c['course_id']: idx for idx, c in enumerate(courses_list)}


def get_similar_courses(course_id: int, top_k: int = 5) -> list:
    """
    Return top-k courses most similar to the given course_id using cosine similarity.
    """
    if _cosine_sim is None or _courses_list is None:
        return []

    idx = _id_to_index.get(int(course_id))
    if idx is None:
        return []

    scores = list(enumerate(_cosine_sim[idx]))
    # Sort by similarity descending, exclude self
    scores = sorted(scores, key=lambda x: x[1], reverse=True)
    scores = [(i, s) for i, s in scores if i != idx]

    result = []
    for i, _ in scores[:top_k]:
        result.append(_courses_list[i])
    return result


def recommend_by_filters(
    courses_list: list,
    category: str | None = None,
    difficulty: str | None = None,
    max_hours: float | None = None,
    min_rating: float | None = None,
    top_k: int = 5,
) -> list:
    """
    Filter courses by optional criteria, sort by rating descending, return top-k.
    """
    filtered = courses_list

    if category:
        cat_lower = category.lower()
        filtered = [c for c in filtered if cat_lower in c.get('category', '').lower()]

    if difficulty:
        diff_lower = difficulty.lower()
        filtered = [c for c in filtered if diff_lower in c.get('course_difficulty', '').lower()]

    if max_hours is not None:
        filtered = [c for c in filtered if float(c.get('est_hours', 0)) <= max_hours]

    if min_rating is not None:
        filtered = [c for c in filtered if float(c.get('course_rating', 0)) >= min_rating]

    filtered = sorted(filtered, key=lambda c: float(c.get('course_rating', 0)), reverse=True)
    return filtered[:top_k]
