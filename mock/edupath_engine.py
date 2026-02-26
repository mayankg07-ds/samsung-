# edupath_engine.py
# Edu-Path Discovery Engine
# SDG 4 | Binary Search O(log n) | Recursive Prerequisite Tree | Data Tidying
# ─────────────────────────────────────────────────────────────────────────────

import csv, json, os
from collections import defaultdict
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import networkx as nx

# ════════════════════════════════════════════════════════════════════
#  1.  DATA LOADING & TIDYING
# ════════════════════════════════════════════════════════════════════

def load_and_tidy(filepath="courses.csv"):
    """
    Loads courses.csv and performs Data Tidying:
      - Removes duplicate course_ids (keep first occurrence)
      - Removes broken prerequisite links (prereq ID not in dataset)
      - Removes rows with missing title or category
    Returns a sorted list of course dicts.
    """
    raw = []
    seen_ids = set()
    duplicates_removed = 0
    missing_fields_removed = 0

    with open(filepath, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            cid = int(row["course_id"])
            # Tidy: drop duplicates
            if cid in seen_ids:
                duplicates_removed += 1
                continue
            # Tidy: drop rows with missing title/category
            if not row["course_title"].strip() or not row["category"].strip():
                missing_fields_removed += 1
                continue
            row["course_id"]       = cid
            row["prerequisite_ids"] = json.loads(row["prerequisite_ids"])
            row["est_hours"]       = float(row["est_hours"])
            row["course_rating"]   = float(row["course_rating"])
            seen_ids.add(cid)
            raw.append(row)

    # Tidy: remove broken prerequisite links
    valid_ids = {r["course_id"] for r in raw}
    broken_links = 0
    for r in raw:
        original_len = len(r["prerequisite_ids"])
        r["prerequisite_ids"] = [p for p in r["prerequisite_ids"] if p in valid_ids]
        broken_links += original_len - len(r["prerequisite_ids"])

    # Sort by course_id for Binary Search
    raw.sort(key=lambda x: x["course_id"])

    print(f"\n[DATA TIDYING REPORT]")
    print(f"  Total courses loaded : {len(raw)}")
    print(f"  Duplicates removed   : {duplicates_removed}")
    print(f"  Missing-field rows   : {missing_fields_removed}")
    print(f"  Broken prereq links  : {broken_links}")
    return raw


# ════════════════════════════════════════════════════════════════════
#  2.  BINARY SEARCH  —  O(log n)
# ════════════════════════════════════════════════════════════════════

def binary_search(courses_sorted, target_id):
    """
    Iterative Binary Search on a list sorted by course_id.
    Time Complexity: O(log n)
    Returns the course dict or None.
    """
    lo, hi = 0, len(courses_sorted) - 1
    steps  = 0
    while lo <= hi:
        mid = (lo + hi) // 2
        steps += 1
        mid_id = courses_sorted[mid]["course_id"]
        if mid_id == target_id:
            print(f"  [Binary Search] Found course_id {target_id} in {steps} step(s)  → O(log {len(courses_sorted)}) ✓")
            return courses_sorted[mid]
        elif mid_id < target_id:
            lo = mid + 1
        else:
            hi = mid - 1
    print(f"  [Binary Search] course_id {target_id} NOT FOUND after {steps} step(s).")
    return None


# ════════════════════════════════════════════════════════════════════
#  3.  RECURSIVE LEARNING TREE  (with circular-dependency guard)
# ════════════════════════════════════════════════════════════════════

def build_index(courses):
    """Build a dict: course_id → course dict for O(1) lookup."""
    return {c["course_id"]: c for c in courses}


def get_learning_path(course_id, index, visited=None, depth=0, max_depth=20):
    """
    Recursively traces ALL prerequisite levels for a given course_id.

    Base cases (infinite-loop guards):
      1. course_id not in index          → unknown course, stop
      2. course_id already in visited    → circular dependency detected, stop
      3. depth > max_depth               → safety cap, stop

    Returns a list of course dicts in prerequisite-first order.
    """
    if visited is None:
        visited = set()

    # Base case 1: unknown course
    if course_id not in index:
        return []

    # Base case 2: circular dependency
    if course_id in visited:
        print(f"  [Prereq Tree] ⚠ Circular dependency detected at course_id={course_id}, skipping.")
        return []

    # Base case 3: depth cap
    if depth > max_depth:
        print(f"  [Prereq Tree] ⚠ Max depth {max_depth} reached, stopping recursion.")
        return []

    visited.add(course_id)
    course = index[course_id]
    path = []

    # Recurse into each prerequisite first
    for prereq_id in course["prerequisite_ids"]:
        path.extend(get_learning_path(prereq_id, index, visited, depth + 1, max_depth))

    path.append(course)
    return path
