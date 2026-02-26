"""
engine/loader.py
Load and preprocess the EduPath course dataset.
"""
import os
import ast
import pandas as pd

# Resolve path relative to this file so it works from any working directory
_DATA_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'EduPath_Dataset.csv')

_df: pd.DataFrame | None = None


def _parse_prereqs(value):
    """Safely parse prerequisite_ids from string to list of ints."""
    if isinstance(value, list):
        return value
    try:
        result = ast.literal_eval(str(value))
        if isinstance(result, list):
            return [int(x) for x in result]
    except (ValueError, SyntaxError):
        pass
    return []


def load_and_preprocess() -> pd.DataFrame:
    """Load CSV, clean data, sort by course_id, return DataFrame."""
    global _df
    df = pd.read_csv(_DATA_PATH)

    # Normalise column names (strip whitespace)
    df.columns = [c.strip() for c in df.columns]

    # Parse prerequisite_ids
    df['prerequisite_ids'] = df['prerequisite_ids'].apply(_parse_prereqs)

    # Ensure numeric types
    df['course_id'] = pd.to_numeric(df['course_id'], errors='coerce').astype(int)
    df['est_hours'] = pd.to_numeric(df['est_hours'], errors='coerce').fillna(0)
    df['course_rating'] = pd.to_numeric(df['course_rating'], errors='coerce').fillna(0.0)

    # Fill missing strings
    for col in ['course_title', 'category', 'course_organization', 'course_difficulty']:
        df[col] = df[col].fillna('').astype(str).str.strip()

    # Sort for binary search
    df = df.sort_values('course_id').reset_index(drop=True)
    _df = df
    return df


def _ensure_loaded() -> pd.DataFrame:
    global _df
    if _df is None:
        load_and_preprocess()
    return _df


def get_all_courses() -> pd.DataFrame:
    """Return the preprocessed, sorted DataFrame."""
    return _ensure_loaded()


def get_courses_list() -> list[dict]:
    """Return a list of course dicts (one per row)."""
    df = _ensure_loaded()
    return df.to_dict(orient='records')


def build_course_index() -> dict:
    """Return {course_id (int): course_dict} for O(1) lookup."""
    courses = get_courses_list()
    return {c['course_id']: c for c in courses}
