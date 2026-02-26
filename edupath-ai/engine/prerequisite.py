"""
engine/prerequisite.py
Recursive prerequisite engine – generates full learning paths with cycle detection.
"""
from collections import deque


def get_learning_path(
    course_id: int,
    courses_index: dict,
    *,
    max_depth: int = 20,
) -> dict | None:
    """
    Build a complete learning path for `course_id` using BFS-style level tracking.

    Args:
        course_id:      Target course id.
        courses_index:  {course_id (int): course_dict} mapping.
        max_depth:      Safety cap on recursion depth.

    Returns:
        {
            "target": course_dict,
            "levels": [[L1 dicts], [L2 dicts], ...],
            "flat_path": [ordered unique prereq dicts],
            "total_hours": int,
            "cycle_detected": bool,
        }
        or None if the target course is not found.
    """
    target = courses_index.get(int(course_id))
    if target is None:
        return None

    cycle_detected = False
    seen: set = set()          # tracks courses already placed in a level
    levels: list[list] = []    # BFS levels of prerequisites

    # BFS – each "current frontier" is the set of prereq IDs at this depth
    current_frontier: list[int] = list(target.get('prerequisite_ids') or [])

    depth = 0
    while current_frontier and depth < max_depth:
        level_courses: list[dict] = []
        next_frontier: list[int] = []

        for pid in current_frontier:
            pid = int(pid)

            if pid in seen:
                # Already placed in an earlier level – skip or flag cycle
                # A cycle occurs only when a course references an ancestor
                cycle_detected = True
                continue

            course = courses_index.get(pid)
            if course is None:
                continue

            seen.add(pid)
            level_courses.append(course)

            # Queue this course's prerequisites for the next level
            for sub_id in (course.get('prerequisite_ids') or []):
                sub_id = int(sub_id)
                if sub_id not in seen:
                    next_frontier.append(sub_id)

        if level_courses:
            levels.append(level_courses)

        current_frontier = next_frontier
        depth += 1

    # Build flat_path: deepest level first (leaf → target) then reverse
    flat_path: list[dict] = []
    seen_flat: set = set()
    for level in reversed(levels):
        for c in level:
            cid = c['course_id']
            if cid not in seen_flat:
                flat_path.append(c)
                seen_flat.add(cid)

    total_hours = sum(int(c.get('est_hours', 0)) for c in flat_path)

    return {
        'target': target,
        'levels': levels,
        'flat_path': flat_path,
        'total_hours': total_hours,
        'cycle_detected': cycle_detected,
    }
