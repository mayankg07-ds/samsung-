/**
 * gamification.js – EduPath AI
 * XP, levels, and badges system powered by localStorage.
 */

class GamificationSystem {
    constructor() {
        this.xp = parseInt(localStorage.getItem('user_xp') || '0');
        this.level = parseInt(localStorage.getItem('user_level') || '1');
        this.badges = JSON.parse(localStorage.getItem('user_badges') || '[]');
        this.completedCourses = JSON.parse(localStorage.getItem('completed_courses') || '[]');
    }

    /** Calculate XP earned for completing a course */
    calculateXP(course) {
        const multipliers = { Beginner: 10, Intermediate: 20, Advanced: 30 };
        const multiplier = multipliers[course.course_difficulty] || 10;
        return Math.round(parseFloat(course.est_hours) * multiplier);
    }

    /** Award XP for a completed course */
    awardXP(course) {
        const earned = this.calculateXP(course);
        this.xp += earned;
        this.updateLevel();
        this.checkBadges(course);
        this.save();
        this.showXPGain(earned);
        return earned;
    }

    updateLevel() {
        const prevLevel = this.level;
        if (this.xp >= 5000) this.level = 5;
        else if (this.xp >= 3000) this.level = 4;
        else if (this.xp >= 1500) this.level = 3;
        else if (this.xp >= 500) this.level = 2;
        else this.level = 1;
        if (this.level > prevLevel) this.showLevelUp();
    }

    checkBadges(course) {
        const newBadges = [];
        const count = this.completedCourses.length;

        if (count >= 1 && !this.badges.includes('First Step'))
            newBadges.push('First Step');
        if (count >= 5 && !this.badges.includes('Getting Started'))
            newBadges.push('Getting Started');
        if (count >= 10 && !this.badges.includes('Dedicated Learner'))
            newBadges.push('Dedicated Learner');
        if (course.course_difficulty === 'Advanced' && !this.badges.includes('Advanced Seeker'))
            newBadges.push('Advanced Seeker');

        // Speed Runner: 5 courses, total hours ≤ 50
        if (count >= 5 && !this.badges.includes('Speed Runner')) {
            const totalH = this.completedCourses.reduce(
                (sum, c) => sum + parseFloat(c.est_hours || 0), 0
            );
            if (totalH <= 50) newBadges.push('Speed Runner');
        }

        // Category Expert: 5 courses same category
        if (!this.badges.includes('Category Expert')) {
            const catCounts = {};
            this.completedCourses.forEach(c => {
                const cat = c.category || '';
                catCounts[cat] = (catCounts[cat] || 0) + 1;
            });
            if (Object.values(catCounts).some(n => n >= 5))
                newBadges.push('Category Expert');
        }

        newBadges.forEach(b => {
            if (!this.badges.includes(b)) {
                this.badges.push(b);
                this.showBadgeEarned(b);
            }
        });
    }

    // ── UI helpers ────────────────────────────────────────────────────────────

    _toast(html, bgClass, duration = 2500) {
        const el = document.createElement('div');
        el.className = `${bgClass} text-white px-5 py-3 rounded-lg shadow-lg text-sm font-medium fade-in-up`;
        el.innerHTML = html;

        let container = document.getElementById('toast-container');
        if (!container) {
            container = document.createElement('div');
            container.id = 'toast-container';
            container.className = 'toast-container';
            document.body.appendChild(container);
        }
        container.appendChild(el);

        setTimeout(() => {
            el.style.transition = 'opacity 0.3s';
            el.style.opacity = '0';
            setTimeout(() => el.remove(), 350);
        }, duration);
    }

    showXPGain(xp) {
        this._toast(`+${xp} XP 🎉`, 'bg-green-600');
    }

    showLevelUp() {
        const names = ['', 'Learner', 'Explorer', 'Practitioner', 'Master', 'Expert'];
        const overlay = document.createElement('div');
        overlay.className =
            'fixed inset-0 flex items-center justify-center z-50 bg-black bg-opacity-60';
        overlay.innerHTML = `
            <div class="bg-purple-700 text-white text-center px-12 py-10 rounded-2xl shadow-2xl fade-in-up">
                <p class="text-5xl mb-3">🎊</p>
                <h2 class="text-4xl font-bold mb-2">Level Up!</h2>
                <p class="text-2xl">You are now Level ${this.level} – ${names[this.level]}</p>
            </div>`;
        document.body.appendChild(overlay);
        setTimeout(() => {
            overlay.style.transition = 'opacity 0.4s';
            overlay.style.opacity = '0';
            setTimeout(() => overlay.remove(), 400);
        }, 3000);
    }

    showBadgeEarned(badge) {
        this._toast(`🏆 Badge Earned: <strong>${badge}</strong>`, 'bg-yellow-600', 3500);
    }

    updateUI() {
        const setEl = (id, val) => {
            const el = document.getElementById(id);
            if (el) el.textContent = val;
        };

        setEl('user-xp', this.xp);
        setEl('user-level', this.level);
        setEl('badge-count', this.badges.length);

        const levelThresholds = [0, 500, 1500, 3000, 5000, 10000];
        const cur = levelThresholds[this.level - 1] || 0;
        const next = levelThresholds[this.level] || 10000;
        const pct = Math.min(100, ((this.xp - cur) / (next - cur)) * 100);

        const bar = document.getElementById('xp-progress');
        if (bar) bar.style.width = pct + '%';

        const levelName = document.getElementById('level-name');
        if (levelName) {
            const names = ['', 'Learner', 'Explorer', 'Practitioner', 'Master', 'Expert'];
            levelName.textContent = names[this.level] || '';
        }
    }

    save() {
        localStorage.setItem('user_xp', this.xp.toString());
        localStorage.setItem('user_level', this.level.toString());
        localStorage.setItem('user_badges', JSON.stringify(this.badges));
        this.updateUI();
    }

    getLevelName() {
        const names = ['', 'Learner', 'Explorer', 'Practitioner', 'Master', 'Expert'];
        return names[this.level] || '';
    }
}

// ── Initialise ────────────────────────────────────────────────────────────────
const gamification = new GamificationSystem();
window.gamification = gamification;

document.addEventListener('DOMContentLoaded', () => {
    gamification.updateUI();
});

/**
 * Call this from roadmap.html when a course is toggled.
 * courseData must be the full course object with est_hours, course_difficulty, etc.
 */
function toggleCompleted(courseId, courseData) {
    let completed = JSON.parse(localStorage.getItem('completed_courses') || '[]');

    const exists = completed.some(c => c.course_id === courseId);
    if (exists) {
        completed = completed.filter(c => c.course_id !== courseId);
    } else {
        completed.push(courseData);
        gamification.completedCourses = completed;
        gamification.awardXP(courseData);
    }

    localStorage.setItem('completed_courses', JSON.stringify(completed));
    gamification.completedCourses = JSON.parse(localStorage.getItem('completed_courses') || '[]');

    // Update progress bar on roadmap page if present
    if (typeof updateProgress === 'function') updateProgress();
}
