"""
routes/search.py
Search API – binary search by ID, title keyword scan.
"""
from flask import Blueprint, request, jsonify, current_app
from engine import binary_search

search_bp = Blueprint('search', __name__)


@search_bp.route('/api/search', methods=['GET'])
def search():
    courses_list = current_app.config['COURSES_LIST']

    course_id = request.args.get('course_id', type=int)
    title = request.args.get('title', type=str)

    if course_id is not None:
        result = binary_search.binary_search(courses_list, course_id)
        if result:
            return jsonify({'success': True, 'data': result})
        return jsonify({'success': False, 'error': 'Course not found'}), 404

    if title:
        results = binary_search.search_by_title(courses_list, title)
        return jsonify({'success': True, 'data': results})

    return jsonify({'success': False, 'error': 'Provide course_id or title parameter'}), 400
