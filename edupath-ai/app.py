"""
app.py – EduPath AI – Flask entry point.
"""
import os
from flask import Flask, render_template, jsonify

from engine import loader, recommender
from routes.search import search_bp
from routes.roadmap import roadmap_bp
from routes.recommend import recommend_bp
from routes.dashboard import dashboard_bp
from routes.chat import chat_bp

# ── App setup ──────────────────────────────────────────────────────────────────
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

# ── Load data at startup ───────────────────────────────────────────────────────
print("Loading course data...")
courses_df = loader.get_all_courses()
courses_list = loader.get_courses_list()
course_index = loader.build_course_index()
print(f"Loaded {len(courses_list)} courses")

app.config['COURSES_DF'] = courses_df
app.config['COURSES_LIST'] = courses_list
app.config['COURSE_INDEX'] = course_index

# ── Init recommender ───────────────────────────────────────────────────────────
print("Initialising recommendation engine...")
recommender.init_recommender(courses_list)
print("Recommender ready")

# ── Register blueprints ────────────────────────────────────────────────────────
app.register_blueprint(search_bp)
app.register_blueprint(roadmap_bp)
app.register_blueprint(recommend_bp)
app.register_blueprint(dashboard_bp)
app.register_blueprint(chat_bp)

# ── Home route ─────────────────────────────────────────────────────────────────
@app.route('/')
def index():
    return render_template('index.html')


# ── Health check ───────────────────────────────────────────────────────────────
@app.route('/health')
def health():
    return jsonify({'status': 'healthy', 'courses_loaded': len(courses_list)})


# ── Error handlers ─────────────────────────────────────────────────────────────
@app.errorhandler(404)
def not_found(error):
    return jsonify({'success': False, 'error': 'Endpoint not found'}), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({'success': False, 'error': 'Internal server error'}), 500


# ── Run ────────────────────────────────────────────────────────────────────────
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') == 'development'
    app.run(host='0.0.0.0', port=port, debug=debug)
