# EduPath AI – Intelligent Career Learning Navigator

An AI-powered course recommendation and learning path generation system built with Flask, TailwindCSS, and Machine Learning.

## 🎯 Features

- **Binary Search Course Lookup** – O(log n) fast search by course ID
- **Recursive Prerequisite Engine** – Automatically generates complete learning paths with cycle detection
- **TF-IDF Recommendations** – Content-based course similarity using machine learning
- **Career Mode** – Generate custom roadmaps for Data Scientist, Full Stack Developer, AI Engineer, Cloud Engineer, Cybersecurity Analyst
- **Skill Gap Analysis** – Identify missing prerequisites and track progress
- **AI Chat Assistant** – Rule-based conversational bot for course guidance (5+ intents)
- **Gamification** – XP system, levels (1–5), and badges to motivate learning
- **Interactive Dashboard** – Chart.js visualisations: category doughnut, difficulty bar, top-rated, avg hours

## 🛠️ Tech Stack

| Layer      | Technology                        |
|------------|-----------------------------------|
| Backend    | Python 3 + Flask                  |
| Frontend   | TailwindCSS + Chart.js            |
| ML         | Scikit-learn (TF-IDF + Cosine Similarity) |
| Data       | Pandas                            |
| Deployment | Render (gunicorn)                 |

## 📊 Dataset

1000 courses with columns: `course_id`, `course_title`, `category`, `prerequisite_ids`, `est_hours`, `course_organization`, `course_difficulty`, `course_rating`.

## 🚀 Local Setup

```bash
# Clone / navigate to the project folder
cd edupath-ai

# Install dependencies
pip install -r requirements.txt

# Run the app
py app.py          # Windows
python app.py      # Linux/macOS

# Open in browser
# http://localhost:5000
```

## 📁 Project Structure

```
edupath-ai/
├── app.py                  # Flask entry point + blueprint registration
├── requirements.txt
├── Procfile                # Deployment config (gunicorn)
├── data/
│   └── EduPath_Dataset.csv
├── engine/
│   ├── loader.py           # CSV loading + preprocessing
│   ├── binary_search.py    # O(log n) iterative search
│   ├── prerequisite.py     # Recursive prerequisite engine
│   └── recommender.py      # TF-IDF cosine similarity
├── routes/
│   ├── search.py           # GET /api/search
│   ├── roadmap.py          # GET /api/roadmap/<id>, GET /roadmap/<id>
│   ├── recommend.py        # Similar, smart, career, skill-gap endpoints
│   ├── dashboard.py        # GET /api/stats, GET /dashboard
│   └── chat.py             # POST /api/chat, GET /chat
├── static/
│   ├── css/custom.css
│   └── js/gamification.js
└── templates/
    ├── base.html
    ├── index.html
    ├── roadmap.html
    ├── dashboard.html
    └── chat.html
```

## 🔀 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/search?course_id=1003` | Binary search by ID |
| GET | `/api/search?title=python` | Title keyword search |
| GET | `/api/roadmap/<id>` | Full prerequisite path (JSON) |
| GET | `/api/recommend/similar/<id>` | TF-IDF similar courses |
| POST | `/api/recommend/smart` | Filter-based recommendations |
| POST | `/api/recommend/career` | Career roadmap |
| POST | `/api/skill-gap` | Skill gap analysis |
| GET | `/api/stats` | Dashboard statistics |
| POST | `/api/chat` | AI chat assistant |
| GET | `/health` | Health check |

## 🎓 Algorithms

1. **Binary Search** – `engine/binary_search.py` – O(log n) course lookup on sorted list
2. **Recursive BFS with Cycle Detection** – `engine/prerequisite.py` – safe prerequisite tree traversal
3. **TF-IDF Vectorisation** – `engine/recommender.py` – combined text fields → sparse matrix
4. **Cosine Similarity** – `engine/recommender.py` – n×n similarity matrix, precomputed at startup

## 🏆 Gamification

- XP: `est_hours × difficulty_multiplier` (Beginner ×10, Intermediate ×20, Advanced ×30)
- Levels: Learner → Explorer → Practitioner → Master → Expert
- Badges: First Step, Getting Started, Dedicated Learner, Advanced Seeker, Speed Runner, Category Expert

## 🌐 Deployment (Render)

1. Push to GitHub
2. New Web Service → connect repo
3. Build: `pip install -r requirements.txt`
4. Start: `gunicorn app:app`
5. Environment: Python 3

## 📝 License

MIT
