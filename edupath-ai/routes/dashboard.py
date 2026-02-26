"""
routes/dashboard.py
Analytics dashboard – statistics and Chart.js data.
"""
from flask import Blueprint, render_template, jsonify, current_app

dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/api/stats')
def stats():
    df = current_app.config['COURSES_DF']

    courses_per_category = df.groupby('category').size().to_dict()
    difficulty_distribution = df.groupby('course_difficulty').size().to_dict()

    top_rated = (
        df[['course_title', 'course_rating']]
        .sort_values('course_rating', ascending=False)
        .head(10)
        .to_dict(orient='records')
    )

    avg_hours_by_difficulty = (
        df.groupby('course_difficulty')['est_hours'].mean().round(1).to_dict()
    )

    total_courses = len(df)
    avg_rating = round(float(df['course_rating'].mean()), 2)
    most_popular_category = df['category'].value_counts().idxmax()

    return jsonify({
        'success': True,
        'data': {
            'courses_per_category': courses_per_category,
            'difficulty_distribution': difficulty_distribution,
            'top_rated_courses': top_rated,
            'avg_hours_by_difficulty': avg_hours_by_difficulty,
            'total_courses': total_courses,
            'avg_rating': avg_rating,
            'most_popular_category': most_popular_category,
        },
    })


@dashboard_bp.route('/dashboard')
def dashboard_page():
    return render_template('dashboard.html')
