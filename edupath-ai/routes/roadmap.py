"""
routes/roadmap.py
Roadmap routes – generate and display prerequisite learning paths.
"""
from flask import Blueprint, render_template, jsonify, current_app
from engine import prerequisite

roadmap_bp = Blueprint('roadmap', __name__)


@roadmap_bp.route('/api/roadmap/<int:course_id>')
def api_roadmap(course_id):
    course_index = current_app.config['COURSE_INDEX']
    path = prerequisite.get_learning_path(course_id, course_index)

    if path is None:
        return jsonify({'success': False, 'error': 'Course not found'}), 404

    return jsonify({'success': True, 'data': path})


@roadmap_bp.route('/roadmap/<int:course_id>')
def roadmap_page(course_id):
    course_index = current_app.config['COURSE_INDEX']
    path = prerequisite.get_learning_path(course_id, course_index)

    if path is None:
        return render_template('roadmap.html', path=None, course_id=course_id)

    return render_template('roadmap.html', path=path, course_id=course_id)
