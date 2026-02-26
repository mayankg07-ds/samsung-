"""
engine/binary_search.py
Iterative binary search for O(log n) course lookup by course_id.
"""


def binary_search(courses_list: list, target_id: int) -> dict | None:
    """
    Perform iterative binary search on a sorted list of course dicts.

    Args:
        courses_list: List of course dicts sorted by 'course_id' ascending.
        target_id: The course_id to search for.

    Returns:
        The matching course dict, or None if not found.
    """
    left, right = 0, len(courses_list) - 1

    while left <= right:
        mid = (left + right) // 2
        mid_id = courses_list[mid]['course_id']

        if mid_id == target_id:
            return courses_list[mid]
        elif mid_id < target_id:
            left = mid + 1
        else:
            right = mid - 1

    return None


def search_by_title(courses_list: list, keyword: str) -> list:
    """
    Linear scan for courses whose title contains `keyword` (case-insensitive).

    Args:
        courses_list: List of course dicts.
        keyword: Partial title to search.

    Returns:
        List of matching course dicts.
    """
    keyword_lower = keyword.lower().strip()
    return [
        c for c in courses_list
        if keyword_lower in c.get('course_title', '').lower()
    ]
