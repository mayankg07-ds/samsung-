"""
routes/chat.py
Rule-based AI chat assistant with intent detection.
"""
from flask import Blueprint, request, jsonify, current_app
from engine import recommender, binary_search, prerequisite

chat_bp = Blueprint('chat', __name__)

# ── Intent keyword maps ────────────────────────────────────────────────────────
INTENTS = {
    'recommend_next': [
        'what should i learn', 'next course', 'after python', "what's next",
        'what next', 'recommend', 'suggest',
    ],
    'career_path': ['become', 'career', 'want to be', 'path to', 'how to become'],
    'skill_gap': ['missing', 'gap', 'what am i missing', 'need to learn', 'prerequisite'],
    'time_estimate': ['how long', 'hours', 'time', 'duration', 'how many hours'],
    'find_course': ['find', 'search', 'show me courses', 'courses about', 'courses on'],
}

CAREER_GOAL_MAP = {
    'data scientist': 'Data Scientist',
    'full stack': 'Full Stack Developer',
    'fullstack': 'Full Stack Developer',
    'ai engineer': 'AI Engineer',
    'cloud engineer': 'Cloud Engineer',
    'cybersecurity': 'Cybersecurity Analyst',
    'security analyst': 'Cybersecurity Analyst',
}

CAREER_CATEGORIES = {
    'Data Scientist': ['Data Science', 'AI', 'Programming', 'Mathematics'],
    'Full Stack Developer': ['Web Dev', 'Programming', 'Database', 'Cloud'],
    'AI Engineer': ['AI', 'Programming', 'Mathematics', 'Computer Sci'],
    'Cloud Engineer': ['Cloud', 'DevOps', 'Networking', 'Programming'],
    'Cybersecurity Analyst': ['Cybersecurity', 'Networking', 'Programming'],
}


def detect_intent(message: str) -> str:
    msg = message.lower()
    for intent, keywords in INTENTS.items():
        if any(kw in msg for kw in keywords):
            return intent
    return 'fallback'


# ── Intent handlers ────────────────────────────────────────────────────────────

def handle_recommend_next(completed_ids: list, courses_list: list) -> dict:
    if not completed_ids:
        sample = sorted(courses_list, key=lambda c: float(c.get('course_rating', 0)), reverse=True)[:5]
        return {
            'reply': "You haven't marked any courses as completed yet! Here are some top-rated courses to start with:",
            'courses': sample,
            'intent': 'recommend_next',
        }

    last_id = int(completed_ids[-1])
    similar = recommender.get_similar_courses(last_id, top_k=5)
    similar = [c for c in similar if c['course_id'] not in completed_ids][:5]
    return {
        'reply': f'Based on your last completed course, here are great next steps:',
        'courses': similar,
        'intent': 'recommend_next',
    }


def handle_career_path(message: str, courses_list: list) -> dict:
    msg = message.lower()
    matched_goal = None
    for keyword, goal in CAREER_GOAL_MAP.items():
        if keyword in msg:
            matched_goal = goal
            break

    if not matched_goal:
        return {
            'reply': 'Which career path are you aiming for? Options: Data Scientist, Full Stack Developer, AI Engineer, Cloud Engineer, Cybersecurity Analyst.',
            'courses': [],
            'intent': 'career_path',
        }

    categories = CAREER_CATEGORIES[matched_goal]
    top_courses = []
    for cat in categories[:2]:
        cat_lower = cat.lower()
        matching = [c for c in courses_list if cat_lower in c.get('category', '').lower()]
        matching = sorted(matching, key=lambda c: float(c.get('course_rating', 0)), reverse=True)[:2]
        top_courses.extend(matching)

    return {
        'reply': f"Great choice! Here's your {matched_goal} learning roadmap. Start with these key courses:",
        'courses': top_courses[:5],
        'intent': 'career_path',
    }


def handle_skill_gap(message: str, courses_list: list, course_index: dict) -> dict:
    # Try to extract a course_id from the message
    import re
    ids = re.findall(r'\b1\d{3}\b', message)
    if ids:
        target_id = int(ids[0])
        path = prerequisite.get_learning_path(target_id, course_index)
        if path:
            prereqs = path.get('flat_path', [])[:5]
            return {
                'reply': f"To take \"{path['target']['course_title']}\", you need these prerequisites:",
                'courses': prereqs,
                'intent': 'skill_gap',
            }

    return {
        'reply': 'To check skill gaps, visit the Skill Gap Analyzer on the home page, or mention a course ID like "What am I missing for course 1010?"',
        'courses': [],
        'intent': 'skill_gap',
    }


def handle_time_estimate(message: str, courses_list: list) -> dict:
    import re

    ids = re.findall(r'\b1\d{3}\b', message)
    if ids:
        cid = int(ids[0])
        course = binary_search.binary_search(courses_list, cid)
        if course:
            return {
                'reply': f"\"{course['course_title']}\" takes approximately {course['est_hours']} hours to complete ({course['course_difficulty']} level).",
                'courses': [course],
                'intent': 'time_estimate',
            }

    # Try category keyword
    for cat in ['ai', 'programming', 'data science', 'web dev', 'cloud', 'cybersecurity']:
        if cat in message.lower():
            matching = [c for c in courses_list if cat in c.get('category', '').lower()]
            if matching:
                avg = sum(float(c.get('est_hours', 0)) for c in matching) / len(matching)
                return {
                    'reply': f'The average time to complete a {cat.title()} course is ~{avg:.0f} hours.',
                    'courses': [],
                    'intent': 'time_estimate',
                }

    total = sum(float(c.get('est_hours', 0)) for c in courses_list)
    avg = total / len(courses_list)
    return {
        'reply': f'On average, courses take about {avg:.0f} hours. Use the Roadmap page for full path time estimates.',
        'courses': [],
        'intent': 'time_estimate',
    }


def handle_find_course(message: str, courses_list: list) -> dict:
    # Extract topic: text after "on", "about", "courses", etc.
    import re
    msg = message.lower()
    # Strip common prefixes to get the topic word
    topic = re.sub(r'.*(find|search|show me courses|courses about|courses on)\s*', '', msg).strip()
    if not topic:
        return {
            'reply': 'What topic would you like to search for? E.g. "Show me courses on machine learning"',
            'courses': [],
            'intent': 'find_course',
        }

    results = binary_search.search_by_title(courses_list, topic)
    if not results:
        # Try category match
        results = [c for c in courses_list if topic in c.get('category', '').lower()]

    results = sorted(results, key=lambda c: float(c.get('course_rating', 0)), reverse=True)[:5]

    if results:
        return {
            'reply': f'Found {len(results)} courses matching "{topic}":',
            'courses': results,
            'intent': 'find_course',
        }
    return {
        'reply': f'No courses found for "{topic}". Try a broader keyword.',
        'courses': [],
        'intent': 'find_course',
    }


def handle_fallback() -> dict:
    return {
        'reply': (
            "I'm EduPath AI! Here are things I can help with:\n"
            "• **Recommend next courses** – \"What should I learn after Python?\"\n"
            "• **Career roadmap** – \"I want to become a Data Scientist\"\n"
            "• **Skill gap** – \"What am I missing for course 1010?\"\n"
            "• **Time estimate** – \"How long is course 1005?\"\n"
            "• **Find courses** – \"Show me courses on AI\""
        ),
        'courses': [],
        'intent': 'fallback',
    }


# ── Chat endpoint ──────────────────────────────────────────────────────────────

@chat_bp.route('/api/chat', methods=['POST'])
def chat():
    data = request.get_json(silent=True) or {}
    message = data.get('message', '').strip()
    completed = data.get('completed_courses', [])

    courses_list = current_app.config['COURSES_LIST']
    course_index = current_app.config['COURSE_INDEX']

    if not message:
        return jsonify({'reply': 'Please send a message!', 'courses': [], 'intent': 'none'})

    intent = detect_intent(message)

    handlers = {
        'recommend_next': lambda: handle_recommend_next(completed, courses_list),
        'career_path': lambda: handle_career_path(message, courses_list),
        'skill_gap': lambda: handle_skill_gap(message, courses_list, course_index),
        'time_estimate': lambda: handle_time_estimate(message, courses_list),
        'find_course': lambda: handle_find_course(message, courses_list),
        'fallback': handle_fallback,
    }

    response = handlers.get(intent, handle_fallback)()
    return jsonify(response)


@chat_bp.route('/chat')
def chat_page():
    from flask import render_template
    return render_template('chat.html')
