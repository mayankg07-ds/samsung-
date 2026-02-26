"""
routes/recommend.py
Recommendation routes – similar courses, smart filters, career roadmaps, skill gap.
"""
from flask import Blueprint, request, jsonify, current_app
from engine import recommender, prerequisite

recommend_bp = Blueprint('recommend', __name__)

CAREER_PATHS = {
    'Data Scientist': ['Data Science', 'AI', 'Programming', 'Mathematics'],
    'Full Stack Developer': ['Web Dev', 'Programming', 'Database', 'Cloud'],
    'AI Engineer': ['AI', 'Programming', 'Mathematics', 'Computer Sci'],
    'Cloud Engineer': ['Cloud', 'DevOps', 'Networking', 'Programming'],
    'Cybersecurity Analyst': ['Cybersecurity', 'Networking', 'Programming'],
}


@recommend_bp.route('/api/recommend/similar/<int:course_id>')
def similar_courses(course_id):
    top_k = request.args.get('top_k', default=5, type=int)
    results = recommender.get_similar_courses(course_id, top_k=top_k)
    return jsonify({'success': True, 'data': results})


@recommend_bp.route('/api/recommend/smart', methods=['POST'])
def smart_recommend():
    courses_list = current_app.config['COURSES_LIST']
    data = request.get_json(silent=True) or {}

    results = recommender.recommend_by_filters(
        courses_list,
        category=data.get('category'),
        difficulty=data.get('difficulty'),
        max_hours=data.get('max_hours'),
        min_rating=data.get('min_rating'),
        top_k=data.get('top_k', 5),
    )
    return jsonify({'success': True, 'data': results})


@recommend_bp.route('/api/recommend/career', methods=['POST'])
def career_recommend():
    courses_list = current_app.config['COURSES_LIST']
    data = request.get_json(silent=True) or {}
    career_goal = data.get('career_goal', '')

    categories = CAREER_PATHS.get(career_goal)
    if not categories:
        available = list(CAREER_PATHS.keys())
        return jsonify({
            'success': False,
            'error': f'Unknown career goal. Choose from: {available}',
        }), 400

    roadmap = {}
    for cat in categories:
        cat_lower = cat.lower()
        matching = [
            c for c in courses_list
            if cat_lower in c.get('category', '').lower()
        ]
        matching_sorted = sorted(
            matching, key=lambda c: float(c.get('course_rating', 0)), reverse=True
        )
        roadmap[cat] = matching_sorted[:5]

    return jsonify({'success': True, 'career_goal': career_goal, 'data': roadmap})


@recommend_bp.route('/api/skill-gap', methods=['POST'])
def skill_gap_analysis():
    course_index = current_app.config['COURSE_INDEX']
    data = request.get_json(silent=True) or {}

    completed = set(int(x) for x in data.get('completed_course_ids', []))
    target_id = data.get('target_course_id')

    if not target_id:
        return jsonify({'success': False, 'error': 'target_course_id required'}), 400

    path = prerequisite.get_learning_path(int(target_id), course_index)
    if not path:
        return jsonify({'success': False, 'error': 'Target course not found'}), 404

    all_prereqs: set = set()
    for level in path['levels']:
        for course in level:
            all_prereqs.add(course['course_id'])

    missing = all_prereqs - completed
    completed_prereqs = all_prereqs & completed

    missing_courses = []
    for level in path['levels']:
        for course in level:
            if course['course_id'] in missing:
                missing_courses.append(course)

    progress = (len(completed_prereqs) / len(all_prereqs) * 100) if all_prereqs else 100.0
    next_recommended = missing_courses[:3]

    return jsonify({
        'success': True,
        'data': {
            'target': path['target'],
            'missing_courses': missing_courses,
            'completed_course_ids': list(completed_prereqs),
            'progress_percent': round(progress, 1),
            'next_recommended': next_recommended,
            'total_missing': len(missing),
            'total_required': len(all_prereqs),
        },
    })
